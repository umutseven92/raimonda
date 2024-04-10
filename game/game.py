import logging

from game.deck import Deck
from game.exceptions import NotEnoughPlayersException, DuplicatePlayerNameException
from game.player import Player, Status
from game.strategy import DEFAULT_DEALER_STRAT, Action


class Game:
    def __init__(self, players: list[Player], game_amount: int, push_22: bool = False):
        self._validate_players(players)

        self._deck = Deck()
        self._players = players
        self._push_22 = push_22
        self._game_amount = game_amount

        self._dealer = Player(
            bankroll=1000, name="Dealer", strategy=DEFAULT_DEALER_STRAT
        )

    @staticmethod
    def _validate_players(players: list[Player]):
        if len(players) <= 0:
            raise NotEnoughPlayersException()

        player_names = [player.name for player in players]
        if len(player_names) != len(set(player_names)):
            raise DuplicatePlayerNameException()

    @staticmethod
    def _player_busted(player: Player) -> bool:
        val = player.get_value()
        if val[0] > 21 and val[1] > 21:
            return True

        return False

    def _deal_to_every_player(self):
        for player in self._players:
            player.deal_card(self._deck.get_card())

    def _reset_game(self):
        logging.info("Resetting game..")

        self._deck = Deck()
        self._reset_players()

    def _reset_players(self):
        for player in self._players:
            player.reset()

    def _init_scores(self) -> dict[Player, int]:
        scores: dict[Player, int] = {self._dealer: 0}

        for player in self._players:
            scores[player] = 0

        return scores

    def _core_loop(self, player: Player):
        logging.info(f"{player.name} is playing..")
        while True:
            action = player.play(dealer_value=self._dealer.get_value())

            if action == Action.STAY:
                logging.info(f"{player.name} stays.")
                break
            elif action == Action.HIT:
                logging.info(f"{player.name} hits.")

                player.deal_card(self._deck.get_card())

                logging.info(f"{player.name}'s new value is {player.get_value()}.")

                if self._player_busted(player):
                    logging.info(f"{player.name} busted.")
                    player.bust()
                    break
                else:
                    continue

    def play(self) -> dict[Player, int]:
        scores = self._init_scores()

        for i in range(self._game_amount):
            self._reset_game()

            # First, each player gets one card.
            self._deal_to_every_player()

            # Then the dealer gets one card
            self._dealer.deal_card(self._deck.get_card())

            # Then each player gets their second card.
            self._deal_to_every_player()

            for player in self._players:
                self._core_loop(player)

            self._core_loop(self._dealer)

            ingame_players = [
                player for player in self._players if player.status != Status.BUSTED
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

        return scores
