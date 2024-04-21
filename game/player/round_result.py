from enum import Enum, auto


class GamblerResult(Enum):
    WIN = auto()
    BLACKJACK_WIN = auto()
    LOST = auto()
    PUSH = auto()
    NOT_PLAYED = auto()


class DealerResult(Enum):
    STAY = auto()
    BLACKJACK = auto()
    BUST = auto()
