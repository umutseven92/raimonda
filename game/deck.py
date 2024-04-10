import dataclasses
import random
from enum import Enum, auto


class Rank(Enum):
    ACE = auto()
    TWO = auto()
    THREE = auto()
    FOUR = auto()
    FIVE = auto()
    SIX = auto()
    SEVEN = auto()
    EIGHT = auto()
    NINE = auto()
    TEN = auto()
    JACK = auto()
    QUEEN = auto()
    KING = auto()

    def rank_value(self) -> tuple[int, int]:
        if self == Rank.ACE:
            return 1, 11
        elif self in [
            Rank.TWO,
            Rank.THREE,
            Rank.FOUR,
            Rank.FIVE,
            Rank.SIX,
            Rank.SEVEN,
            Rank.EIGHT,
            Rank.NINE,
        ]:
            return self.value, self.value
        else:
            return 10, 10


class Suit(Enum):
    CLUBS = auto()
    DIAMONDS = auto()
    HEARTS = auto()
    SPADES = auto()


@dataclasses.dataclass
class Card:
    rank: Rank
    suit: Suit

    def card_value(self) -> tuple[int, int]:
        return self.rank.rank_value()

    def __str__(self):
        return f"{self.rank.name.title()} of {self.suit.name.title()}"


class Deck:
    _cards: list[Card]

    def __init__(self):
        self._cards = self._generate_deck()

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
