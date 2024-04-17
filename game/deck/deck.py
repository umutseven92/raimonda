import random

from game.deck.card import Card, Suit, Rank


class Deck:
    _cards: list[Card]

    @classmethod
    def shuffled_cards(cls):
        return cls(cards=Deck._generate_deck())

    @classmethod
    def with_cards(cls, cards: list[Card]):
        return cls(cards=cards)

    def __init__(self, cards: list[Card]):
        self._cards = cards

    def get_card(self) -> Card:
        return self._cards.pop()

    def card_amount(self) -> int:
        return len(self._cards)

    @staticmethod
    def _generate_deck() -> list[Card]:
        """Generate the standard 52-card French deck."""
        cards: list[Card] = []

        for suit in Suit:
            for rank in Rank:
                cards.append(Card(rank, suit))

        random.shuffle(cards)

        return cards
