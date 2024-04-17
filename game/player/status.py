from enum import Enum, auto


class Status(Enum):
    # The player is currently in play, in the game.
    IN_GAME = auto()

    # The player has busted, but is still in the game.
    BUSTED = auto()

    # The player has lost all their bankroll, and is out of the game.
    BANKRUPT = auto()
