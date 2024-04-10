import dataclasses
from enum import Enum, auto
from typing import Callable


class Action(Enum):
    HIT = auto()
    STAY = auto()


Value = tuple[int, int]
Play = Callable[[Value, Value], Action]


@dataclasses.dataclass
class Strategy:
    play: Play


def dealer_play(player_val: Value, _dealer_val) -> Action:
    """Default dealer strategy is to hit if the card value is lower than 17."""
    if player_val[0] >= 17 or player_val[1] >= 17:
        return Action.STAY
    else:
        return Action.HIT


DEFAULT_DEALER_STRAT = Strategy(play=dealer_play)


def stand_everytime(_player_val, _dealer_val) -> Action:
    return Action.STAY


STAND_EVERYTIME_STRAT = Strategy(play=stand_everytime)
