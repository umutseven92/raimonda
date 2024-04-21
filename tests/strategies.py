from game.constants import CardValues
from game.strategy import Action


def minimum_bet_play_strat(
    _bankroll: float, minimum_bet: float, _maximum_bet: float
) -> float:
    return minimum_bet


def stay_everytime_play_strat(
    player_val: CardValues,
    dealer_val: CardValues,
    allowed_actions: list[Action],
) -> Action:
    return Action.STAY
