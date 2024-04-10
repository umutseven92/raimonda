import yaml
from yaml import Loader

from game.deck import Card, Suit, Rank
from game.player import Player
from game.strategy import STAND_EVERYTIME_STRAT


class TestPlayer:
    def test_can_load_from_yaml(self):
        yaml_val = """
        players:
            - player:
                name: "Player 1"
                bankroll: 200
            - player:
                name: "Player 2"
        """

        loaded = yaml.load(yaml_val, Loader=Loader)

        players = []

        for player_yaml in loaded["players"]:
            players.append(Player.from_yaml(player_yaml["player"]))

        assert players[0].name == "Player 1"
        assert players[0].bankroll == 200

        assert players[1].name == "Player 2"
        assert players[1].bankroll is None

    def test_can_get_value(self):
        player = Player(
            name="Test Player", bankroll=100, strategy=STAND_EVERYTIME_STRAT
        )

        player.deal_card(Card(rank=Rank.JACK, suit=Suit.CLUBS))  # 10
        player.deal_card(Card(rank=Rank.THREE, suit=Suit.CLUBS))  # 13
        player.deal_card(Card(rank=Rank.ACE, suit=Suit.CLUBS))  # 14, 24

        assert player.get_value() == (14, 24)

    def test_can_get_hashed(self):
        player = Player(
            name="Test Player", bankroll=100, strategy=STAND_EVERYTIME_STRAT
        )

        assert hash(player) == hash("Test Player")

        player2 = Player(
            name="Test Player", bankroll=120, strategy=STAND_EVERYTIME_STRAT
        )

        assert player == player2
