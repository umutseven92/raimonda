from game.deck.card import Rank, Suit, Card
from game.deck.deck import Deck


class TestDeck:
    def test_can_name_card(self):
        card = Card(rank=Rank.ACE, suit=Suit.SPADES)
        assert str(card) == "Ace of Spades"

    def test_can_value_card(self):
        card = Card(rank=Rank.ACE, suit=Suit.SPADES)
        assert card.card_value() == (1, 11)

        card = Card(rank=Rank.TWO, suit=Suit.SPADES)
        assert card.card_value() == (2, 2)

        card = Card(rank=Rank.JACK, suit=Suit.SPADES)
        assert card.card_value() == (10, 10)

    def test_can_generate_deck(self):
        deck = Deck()
        assert deck.card_amount() == 52
