from game.deck import Card, Suit, Rank
from game.player import Player
from game.strategy import STAND_EVERYTIME_STRAT


class TestPlayer:
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
