from enum import Enum, auto
from typing import Callable

from game.constants import CardValues


class Action(Enum):
    HIT = auto()
    STAY = auto()


PlayStrategy = Callable[[CardValues, CardValues], Action]
BetStrategy = Callable[[float], float]


def default_dealer_play_strategy(
    player_val: CardValues, _dealer_val: CardValues
) -> Action:
    """Default dealer strategy is to hit if the card value is lower than 17."""
    if player_val[0] >= 17 or player_val[1] >= 17:
        return Action.STAY
    else:
        return Action.HIT


def stand_everytime_play_strategy(
    _player_val: CardValues, _dealer_val: CardValues
) -> Action:
    return Action.STAY


def one_bet_strategy(_remaining_bankroll: float) -> float:
    return 1
