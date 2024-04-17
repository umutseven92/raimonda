from enum import Enum, auto


class RoundResult(Enum):
    WIN = auto()
    BLACKJACK_WIN = auto()
    LOST = auto()
    PUSH = auto()
    NOT_PLAYED = auto()
