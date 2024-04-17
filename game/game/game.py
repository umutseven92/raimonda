import logging
import time
from pathlib import Path

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
from game.game.bet_manager import BetManager
from game.game.game_config import GameConfig
from game.game.game_result import GameResult
from game.player.dealer import Dealer
from game.player.gambler import Gambler
from game.player.player import Player
from game.player.round_result import RoundResult
from game.strategy import Action


class Game:
    def __init__(
        self, gamblers: list[Gambler], dealer: Dealer, config: GameConfig, deck: Deck
    ):
        self._gamblers = gamblers
        self._validate_gamblers(gamblers)

        self._dealer = dealer
        self._config = config

        self._deck = deck
        self._bet_manager = BetManager(
            minimum_bet=self._config.minimum_bet,
            maximum_bet=self._config.maximum_bet,
            blackjack_value=self._config.blackjack,
        )

    @property
    def in_game_gamblers(self) -> list[Gambler]:
        return [gambler for gambler in self._gamblers if gambler.is_in_game]

    @property
    def busted_gamblers(self) -> list[Gambler]:
        return [gambler for gambler in self._gamblers if gambler.is_busted]

    @property
    def bankrupt_gamblers(self) -> list[Gambler]:
        return [gambler for gambler in self._gamblers if gambler.is_bankrupt]

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

        return cls(gamblers, dealer, config, Deck.shuffled_cards())

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

        self._deck = Deck.shuffled_cards()
        self._reset_players()

    def _reset_players(self):
        for player in self._gamblers:
            player.reset()
        self._dealer.reset()

    def _get_allowed_gambler_actions(
        self, gambler: Gambler, nth_card: int
    ) -> list[Action]:
        actions = [Action.HIT, Action.STAY]
        value = gambler.get_value()

        if nth_card == 0 and (
            value[0] in self._config.double_down_allowed
            or value[1] in self._config.double_down_allowed
        ):
            actions.append(Action.DOUBLE_DOWN)

        return actions

    def _core_gambler_loop(self, gambler: Gambler):
        logging.debug(f"{gambler.name} is playing..")

        card_index = 0
        while True:
            action = gambler.run_play_strategy(
                dealer_value=self._dealer.get_value(),
                allowed_actions=self._get_allowed_gambler_actions(gambler, card_index),
            )

            if action == Action.STAY:
                logging.debug(f"{gambler.name} stays.")
                break
            elif action == Action.HIT or action == Action.DOUBLE_DOWN:
                if action == Action.HIT:
                    logging.debug(f"{gambler.name} hits.")
                else:
                    logging.debug(f"{gambler.name} doubles down.")

                    # Double the bet of the current gambler.
                    current_bet = self._bet_manager.bets[gambler]
                    gambler.take_away(current_bet)
                    self._bet_manager.bets[gambler] += current_bet

                gambler.deal_card(self._deck.get_card())
                card_index += 1

                logging.debug(f"{gambler.name}'s new value is {gambler.get_value()}.")

                if self._player_busted(gambler):
                    logging.debug(f"{gambler.name} busted.")
                    gambler.bust()
                    break
                elif action == Action.DOUBLE_DOWN:
                    # The gambler only gets one card after doubling down.
                    break
                else:
                    continue

    def _core_dealer_loop(self, dealer: Dealer):
        logging.debug(f"{dealer.name} is playing..")

        while True:
            action = dealer.run_play_strategy()

            if action == Action.STAY:
                logging.debug(f"{dealer.name} stays.")
                break
            elif action == Action.HIT:
                logging.debug(f"{dealer.name} hits.")

                dealer.deal_card(self._deck.get_card())

                logging.debug(f"{dealer.name}'s new value is {dealer.get_value()}.")

                if self._player_busted(dealer):
                    logging.debug(f"{dealer.name} busted.")
                    dealer.bust()
                    break
                else:
                    continue

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
            if not self._check_if_game_can_go_on():
                logging.info("Game cannot continue. Terminating early..")
                break

            self._bet_manager.collect_bets(self.in_game_gamblers)

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
                self._bet_manager.distribute_bets(
                    dealer=self._dealer,
                    winning_gamblers=self.in_game_gamblers,
                    losing_gamblers=self.busted_gamblers,
                    pushed_gamblers=[],
                )
                self._dealer.add_result_to_log(RoundResult.LOST)

                for in_game_gambler in self.in_game_gamblers:
                    in_game_gambler.add_result_to_log(RoundResult.WIN)

                for busted_gambler in self.busted_gamblers:
                    busted_gambler.add_result_to_log(RoundResult.LOST)
            else:
                # Dealer stays. Everyone else with score less than the dealer loses, everyone with a score higher
                # than the dealer wins. Rest get their money back (push).
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
                pushed = [
                    gambler
                    for gambler in self.in_game_gamblers
                    if gambler.get_value() == self._dealer.get_value()
                ]

                self._bet_manager.distribute_bets(
                    dealer=self._dealer,
                    winning_gamblers=winners,
                    losing_gamblers=losers + self.busted_gamblers,
                    pushed_gamblers=pushed,
                )

                self._dealer.add_result_to_log(RoundResult.WIN)

                for winner in winners:
                    winner.add_result_to_log(RoundResult.WIN)

                for loser in losers:
                    loser.add_result_to_log(RoundResult.LOST)

                for push in pushed:
                    push.add_result_to_log(RoundResult.PUSH)

            for bankrupt_player in self.bankrupt_gamblers:
                bankrupt_player.add_result_to_log(RoundResult.NOT_PLAYED)

            for player in self.all_players:
                player.add_to_bankroll_log()

            self._check_for_bankruptcy()

            games_played += 1
            self._reset_game()

        end = time.time()
        logging.info(f"Played {games_played} games. Took {(end - start):.4f} seconds.")

        return GameResult(
            actual_played=games_played, gamblers=self._gamblers, dealer=self._dealer
        )
