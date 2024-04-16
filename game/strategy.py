from enum import Enum, auto
from typing import Callable, Final

from game.constants import CardValues

DEALER_STOP: Final[int] = 17


class Action(Enum):
    HIT = auto()
    STAY = auto()


GamblerPlayStrategy = Callable[[CardValues, CardValues], Action]
DealerPlayStrategy = Callable[[CardValues], Action]
BetStrategy = Callable[[float, float, float], float]


def default_dealer_play_strategy(dealer_val: CardValues) -> Action:
    """Default dealer strategy is to hit if the card value is lower 17."""
    if dealer_val[0] >= DEALER_STOP or dealer_val[1] >= DEALER_STOP:
        return Action.STAY
    else:
        return Action.HIT


def default_gambler_play_strategy(
    player_val: CardValues, dealer_val: CardValues
) -> Action:
    # TODO: Optimal gambler strategy.
    return Action.STAY


def minimum_bet_strategy(
    _bankroll: float, minimum_bet: float, _maximum_bet: float
) -> float:
    return minimum_bet
