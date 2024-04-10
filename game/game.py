from game.deck import Deck
from game.exceptions import NotEnoughPlayersException, DuplicatePlayerNameException
from game.player import Player, Status
from game.strategy import DEFAULT_DEALER_STRAT, Action


class Game:
    def __init__(self, players: list[Player], game_amount: int, push_22: bool = False):
        self._validate_players(players)

        self._deck = Deck()
        self.players = players
        self._push_22 = push_22
        self._game_amount = game_amount

        self.dealer = Player(
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
        for player in self.players:
            player.deal_card(self._deck.get_card())

    def _reset_game(self):
        self._deck = Deck()
        self._reset_players()

    def _reset_players(self):
        for player in self.players:
            player.reset()

    def _init_scores(self) -> dict[Player, int]:
        scores: dict[Player, int] = {self.dealer: 0}

        for player in self.players:
            scores[player] = 0

        return scores

    def _core_loop(self, player: Player):
        while True:
            action = player.play(dealer_value=self.dealer.get_value())

            if action == Action.STAY:
                break
            elif action == Action.HIT:
                player.deal_card(self._deck.get_card())
                if self._player_busted(player):
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
            self.dealer.deal_card(self._deck.get_card())

            # Then each player gets their second card.
            self._deal_to_every_player()

            for player in self.players:
                self._core_loop(player)

            self._core_loop(self.dealer)

            ingame_players = [
                player for player in self.players if player.status != Status.BUSTED
            ]

            if self.dealer.status == Status.BUSTED:
                # Dealer lost. Anyone who has not busted out wins.
                for ingame_player in ingame_players:
                    scores[ingame_player] += 1
            else:
                # Dealer won. Everyone else with score less than the dealer loses.
                scores[self.dealer] += 1

        return scores
