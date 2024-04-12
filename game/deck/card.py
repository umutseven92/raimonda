import dataclasses
from enum import Enum, auto

from game.constants import CardValues


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

    def rank_value(self) -> CardValues:
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

    def card_value(self) -> CardValues:
        return self.rank.rank_value()

    def __str__(self):
        return f"{self.rank.name.title()} of {self.suit.name.title()}"
