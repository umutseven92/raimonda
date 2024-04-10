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
from game.player import Player, Status
from game.strategy import Action


class Game:
    def __init__(self, gamblers: list[Gambler], dealer: Dealer, push_22: bool):
        self._gamblers = gamblers
        self._dealer = dealer
        self._push_22 = push_22

        self._deck = Deck()

    @classmethod
    def from_yaml(cls, data: dict):
        gamblers = []

        for player_yaml in data["gamblers"]:
            gamblers.append(Gambler.from_yaml(player_yaml["gambler"]))

        cls._validate_gamblers(gamblers)

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

    def play(self, game_amount: int) -> dict[Player, int]:
        logging.info(f"Playing {game_amount} games..")
        start = time.time()

        scores = self._init_scores()

        for i in range(game_amount):
            self._reset_game()

            # First, each player gets one card.
            self._deal_to_every_gambler()

            # Then the dealer gets one card
            self._dealer.deal_card(self._deck.get_card())

            # Then each player gets their second card.
            self._deal_to_every_gambler()

            for player in self._gamblers:
                self._core_loop(player)

            self._core_loop(self._dealer)

            ingame_players = [
                player for player in self._gamblers if player.status != Status.BUSTED
            ]

            if self._dealer.status == Status.BUSTED:
                # Dealer lost. Anyone who has not busted out wins.
                for ingame_player in ingame_players:
                    scores[ingame_player] += 1
            else:
                # Dealer won. Everyone else with score less than the dealer loses.
                scores[self._dealer] += 1
                for ingame_player in ingame_players:
                    if ingame_player.get_value() > self._dealer.get_value():
                        scores[ingame_player] += 1

        end = time.time()
        logging.info(f"Games are finished. Took {(end - start):.4f} seconds.")

        return scores
