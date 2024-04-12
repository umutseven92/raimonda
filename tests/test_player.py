import yaml
from yaml import Loader

from game.constants import DEALER_NAME
from game.dealer import Dealer
from game.deck import Card, Suit, Rank
from game.gambler import Gambler
from tests.helpers import player_to_test


class TestPlayer:
    def test_can_load_gambler_from_yaml(self):
        yaml_val = """
        gamblers:
            - gambler:
                name: "Player 1"
                bankroll: 200
            - gambler:
                name: "Player 2"
        """

        loaded = yaml.load(yaml_val, Loader=Loader)

        gamblers = []

        for player_yaml in loaded["gamblers"]:
            gamblers.append(Gambler.from_yaml(player_yaml["gambler"]))

        assert gamblers[0].name == "Player 1"
        assert gamblers[0].bankroll == 200

        assert gamblers[1].name == "Player 2"
        assert gamblers[1].bankroll is None

    def test_can_load_dealer_from_yaml(self):
        yaml_val = """
        dealer:
          bankroll: 1000
        """

        loaded = yaml.load(yaml_val, Loader=Loader)

        dealer = Dealer.from_yaml(loaded["dealer"])

        assert dealer.name == DEALER_NAME
        assert dealer.bankroll == 1000

    def test_can_get_value(self):
        player = player_to_test()
        player.deal_card(Card(rank=Rank.JACK, suit=Suit.CLUBS))  # 10
        player.deal_card(Card(rank=Rank.THREE, suit=Suit.CLUBS))  # 13
        player.deal_card(Card(rank=Rank.ACE, suit=Suit.CLUBS))  # 14, 24

        assert player.get_value() == (14, 24)

    def test_can_get_hashed(self):
        player = player_to_test()
        assert hash(player) == hash(player.name)

        player2 = player_to_test()

        assert player == player2
