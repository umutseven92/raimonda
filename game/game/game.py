import logging
import time
from pathlib import Path
from typing import Callable

import yaml
from yaml import Loader

from game.constants import DEALER_NAME
from game.deck.deck import Deck
from game.exceptions import (
    NotEnoughGamblersException,
    DuplicateGamblerNameException,
    CantNameGamblerDealerException,
    ConfigNotFoundException,
)
from game.game.game_config import GameConfig
from game.game.game_result import GameResult
from game.player.dealer import Dealer
from game.player.gambler import Gambler
from game.player.player import Player
from game.strategy import Action


class Game:
    def __init__(self, gamblers: list[Gambler], dealer: Dealer, config: GameConfig):
        self._gamblers = gamblers
        self._validate_gamblers(gamblers)

        self._dealer = dealer
        self._config = config

        self._deck = Deck()

    @property
    def in_game_gamblers(self) -> list[Gambler]:
        return [gambler for gambler in self._gamblers if gambler.is_in_game]

    @property
    def busted_gamblers(self) -> list[Gambler]:
        return [gambler for gambler in self._gamblers if gambler.is_busted]

    @property
    def all_players(self) -> list[Player]:
        return self._gamblers + [self._dealer]

    @property
    def all_in_game_players(self) -> list[Player]:
        return self.in_game_gamblers + [self._dealer]

    @classmethod
    def from_yaml_file(cls, config_path: str):
        if not Path(config_path).exists():
            raise ConfigNotFoundException(config_path)

        with open(config_path) as config_file:
            data = yaml.load(config_file, Loader=Loader)

        gamblers = []

        for player_yaml in data["gamblers"]:
            gamblers.append(Gambler.from_yaml(player_yaml["gambler"]))

        dealer = Dealer.from_yaml(data["dealer"])

        config = GameConfig.from_yaml(data["game"])

        return cls(gamblers, dealer, config)

    @staticmethod
    def _validate_gamblers(gamblers: list[Gambler]):
        if len(gamblers) <= 0:
            raise NotEnoughGamblersException()

        gambler_names = [player.name for player in gamblers]
        if len(gambler_names) != len(set(gambler_names)):
            raise DuplicateGamblerNameException()

        if DEALER_NAME in gambler_names:
            raise CantNameGamblerDealerException(dealer_name=DEALER_NAME)

    def _player_busted(self, player: Player) -> bool:
        val = player.get_value()
        if val[0] > self._config.blackjack and val[1] > self._config.blackjack:
            return True

        return False

    def _deal_to_every_gambler(self):
        for gambler in self.in_game_gamblers:
            gambler.deal_card(self._deck.get_card())

    def _reset_game(self):
        logging.debug("Resetting game..")

        self._deck = Deck()
        self._reset_players()

    def _reset_players(self):
        for player in self._gamblers:
            player.reset()
        self._dealer.reset()

    def _core_loop(self, action_func: Callable[[], Action], player: Player):
        logging.debug(f"{player.name} is playing..")
        while True:
            action = action_func()

            if action == Action.STAY:
                logging.debug(f"{player.name} stays.")
                break
            elif action == Action.HIT:
                logging.debug(f"{player.name} hits.")

                player.deal_card(self._deck.get_card())

                logging.debug(f"{player.name}'s new value is {player.get_value()}.")

                if self._player_busted(player):
                    logging.debug(f"{player.name} busted.")
                    player.bust()
                    break
                else:
                    continue

    def _core_gambler_loop(self, gambler: Gambler):
        def action_func():
            return gambler.run_play_strategy(dealer_value=self._dealer.get_value())

        self._core_loop(action_func, gambler)

    def _core_dealer_loop(self, dealer: Dealer):
        def action_func():
            return dealer.run_play_strategy()

        self._core_loop(action_func, dealer)

    def _collect_bets(self) -> dict:
        bets = {}
        for gambler in self.in_game_gamblers:
            bet = gambler.run_bet_strategy(
                minimum_bet=self._config.minimum_bet,
                maximum_bet=self._config.maximum_bet,
            )
            bets[gambler] = bet

        return bets

    def _distribute_bets(
        self,
        bets: dict,
        winning_gamblers: list[Gambler],
        losing_gamblers: list[Gambler],
    ):
        # All lost bets go to the dealer.
        for lost_gambler in losing_gamblers:
            lost_bet = bets[lost_gambler]
            logging.debug(f"{lost_gambler} lost {lost_bet} to {self._dealer.name}.")

            self._dealer.pay(lost_bet)

        # The winning players get paid 1:2, except for when it is blackjack, in which case they get paid 2:3.
        for winning_gambler in winning_gamblers:
            winning_bet = bets[winning_gambler]
            self._dealer.take_away(winning_bet)
            if winning_gambler.value_is_blackjack(self._config.blackjack):
                amount = winning_bet + (winning_bet * 1.5)
                logging.debug(
                    f"Blackjack! {winning_gambler} won {amount} from {self._dealer.name}."
                )

                winning_gambler.pay(amount)
            else:
                amount = winning_bet * 2
                logging.debug(
                    f"{winning_gambler} won {amount} from {self._dealer.name}."
                )

                winning_gambler.pay(amount)

    def _check_for_bankruptcy(self):
        for gambler in self.in_game_gamblers:
            if gambler.bankroll <= self._config.minimum_bet:
                # Gamblers are bankrupt if their bankroll is lower than the minimum bet, which means they won't be able
                # to continue playing.
                gambler.bankrupt()

        if self._dealer.bankroll <= 0:
            # The dealer is bankrupt if they run out of money.
            self._dealer.bankrupt()

    def _check_if_game_can_go_on(self) -> bool:
        if self._dealer.is_bankrupt:
            logging.info("Dealer in bankrupt.")
            return False
        if len(self.in_game_gamblers) == 0:
            logging.info("No players left in game.")
            return False

        return True

    def play(self, game_amount: int) -> GameResult:
        logging.info(f"Playing {game_amount} games..")
        start = time.time()

        games_played = 0

        for i in range(game_amount):
            self._reset_game()

            if not self._check_if_game_can_go_on():
                logging.info("Game cannot continue. Terminating early..")
                break

            for player in self.all_players:
                player.add_to_bankroll_log()

            bets = self._collect_bets()

            # First, each player gets one card.
            self._deal_to_every_gambler()

            # Then the dealer gets one card.
            self._dealer.deal_card(self._deck.get_card())

            # Then each player gets their second card.
            self._deal_to_every_gambler()

            # Each player plays, one after another.
            for gambler in self._gamblers:
                self._core_gambler_loop(gambler)

            # Then the dealer plays.
            self._core_dealer_loop(self._dealer)

            if self._dealer.is_busted:
                # Dealer is busted. Anyone who has not busted out wins.
                self._distribute_bets(
                    bets=bets,
                    winning_gamblers=self.in_game_gamblers,
                    losing_gamblers=self.busted_gamblers,
                )

                for in_game_gambler in self.in_game_gamblers:
                    in_game_gambler.increment_wins()
            else:
                # Dealer stays. Everyone else with score less than the dealer loses, everyone with a score higher
                # than the dealer wins. Rest get their money back.
                winners = [
                    gambler
                    for gambler in self.in_game_gamblers
                    if gambler.get_value() > self._dealer.get_value()
                ]
                losers = [
                    gambler
                    for gambler in self.in_game_gamblers
                    if gambler.get_value() < self._dealer.get_value()
                ]

                self._distribute_bets(
                    bets=bets,
                    winning_gamblers=winners,
                    losing_gamblers=losers + self.busted_gamblers,
                )

                self._dealer.increment_wins()
                for winning_gambler in winners:
                    if winning_gambler.get_value() > self._dealer.get_value():
                        winning_gambler.increment_wins()

            for in_game_player in self.all_in_game_players:
                in_game_player.increment_played()

            self._check_for_bankruptcy()

            games_played += 1

        end = time.time()
        logging.info(f"Played {games_played} games. Took {(end - start):.4f} seconds.")

        return GameResult(
            actual_played=games_played, gamblers=self._gamblers, dealer=self._dealer
        )
