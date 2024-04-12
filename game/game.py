import logging
import time

from game.constants import DEALER_NAME
from game.dealer import Dealer
from game.deck import Deck
from game.exceptions import (
    NotEnoughGamblersException,
    DuplicateGamblerNameException,
    CantNameGamblerDealerException,
)
from game.gambler import Gambler
from game.player import Player
from game.strategy import Action


class Game:
    def __init__(self, gamblers: list[Gambler], dealer: Dealer, push_22: bool = False):
        self._gamblers = gamblers
        self._validate_gamblers(gamblers)

        self._dealer = dealer
        self._push_22 = push_22

        self._deck = Deck()

    @property
    def in_game_gamblers(self) -> list[Gambler]:
        return [gambler for gambler in self._gamblers if gambler.is_in_game]

    @property
    def busted_gamblers(self) -> list[Gambler]:
        return [gambler for gambler in self._gamblers if gambler.is_busted]

    @classmethod
    def from_yaml(cls, data: dict):
        gamblers = []

        for player_yaml in data["gamblers"]:
            gamblers.append(Gambler.from_yaml(player_yaml["gambler"]))

        dealer = Dealer.from_yaml(data["dealer"])
        push_22 = data["game"]["push-22"]

        return cls(gamblers, dealer, push_22)

    @staticmethod
    def _validate_gamblers(gamblers: list[Gambler]):
        if len(gamblers) <= 0:
            raise NotEnoughGamblersException()

        gambler_names = [player.name for player in gamblers]
        if len(gambler_names) != len(set(gambler_names)):
            raise DuplicateGamblerNameException()

        if DEALER_NAME in gambler_names:
            raise CantNameGamblerDealerException(dealer_name=DEALER_NAME)

    @staticmethod
    def _player_busted(player: Player) -> bool:
        val = player.get_value()
        if val[0] > 21 and val[1] > 21:
            return True

        return False

    def _deal_to_every_gambler(self):
        for gambler in self._gamblers:
            gambler.deal_card(self._deck.get_card())

    def _reset_game(self):
        logging.debug("Resetting game..")

        self._deck = Deck()
        self._reset_players()

    def _reset_players(self):
        for player in self._gamblers:
            player.reset()
        self._dealer.reset()

    def _init_scores(self) -> dict[Player, int]:
        scores: dict[Player, int] = {self._dealer: 0}

        for player in self._gamblers:
            scores[player] = 0

        return scores

    def _core_loop(self, player: Player):
        logging.debug(f"{player.name} is playing..")
        while True:
            action = player.play(dealer_value=self._dealer.get_value())

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

    def _collect_bets(self) -> dict:
        bets = {}
        for gambler in self.in_game_gamblers:
            bet = gambler.run_bet_strategy()
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
            if winning_gambler.value_is_blackjack():
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
        for player in self._gamblers + [self._dealer]:
            if player.bankroll <= 0:
                player.bankrupt()

    def _check_if_game_can_go_on(self) -> bool:
        if self._dealer.is_bankrupt:
            logging.info("Dealer in bankrupt.")
            return False
        if len(self.in_game_gamblers) == 0:
            logging.info("No players left in game.")
            return False

        return True

    def play(self, game_amount: int) -> dict[Player, int]:
        logging.info(f"Playing {game_amount} games..")
        start = time.time()

        games_played = 0

        scores = self._init_scores()

        for i in range(game_amount):
            self._reset_game()

            if not self._check_if_game_can_go_on():
                logging.info("Game cannot continue. Terminating early..")
                break

            bets = self._collect_bets()

            # First, each player gets one card.
            self._deal_to_every_gambler()

            # Then the dealer gets one card.
            self._dealer.deal_card(self._deck.get_card())

            # Then each player gets their second card.
            self._deal_to_every_gambler()

            # Each player plays, one after another.
            for player in self._gamblers:
                self._core_loop(player)

            # Then the dealer plays.
            self._core_loop(self._dealer)

            if self._dealer.is_busted:
                # Dealer is busted. Anyone who has not busted out wins.
                self._distribute_bets(
                    bets=bets,
                    winning_gamblers=self.in_game_gamblers,
                    losing_gamblers=self.busted_gamblers,
                )
                # for ingame_player in self.in_game_gamblers:
                #     scores[ingame_player] += 1
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

                # scores[self._dealer] += 1
                # for ingame_player in self.in_game_gamblers:
                #     if ingame_player.get_value() > self._dealer.get_value():
                #         scores[ingame_player] += 1

            self._check_for_bankruptcy()

            games_played += 1

        end = time.time()
        logging.info(f"Played {games_played} games. Took {(end - start):.4f} seconds.")

        return scores
