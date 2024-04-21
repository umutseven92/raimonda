from typing import Final

import user.play_strategies
from game.constants import DEALER_NAME
from game.exceptions import InvalidActionException
from game.player.player import Player
from game.player.round_result import DealerResult
from game.strategy import DealerPlayStrategy, Action, default_dealer_play_strategy

# The dealer can only hit or stay.
ALLOWED_ACTIONS: Final[list[Action]] = [Action.STAY, Action.HIT]


class Dealer(Player):
    def __init__(
        self,
        bankroll: float,
        play_strategy: DealerPlayStrategy = default_dealer_play_strategy,
    ):
        self.play_strategy = play_strategy
        self.result_log: list[DealerResult] = []

        super().__init__(DEALER_NAME, bankroll)

    @classmethod
    def from_yaml(cls, data: dict):
        val = cls(bankroll=data["bankroll"], play_strategy=cls._get_play_strategy(data))

        return val

    @staticmethod
    def _get_play_strategy(data: dict) -> DealerPlayStrategy:
        return Player._get_strategy(
            data, "play-strategy", default_dealer_play_strategy, user.play_strategies
        )

    def run_play_strategy(self) -> Action:
        action = self.play_strategy(self.get_value())

        if action not in ALLOWED_ACTIONS:
            raise InvalidActionException(action, ALLOWED_ACTIONS)

        return action

    def add_result_to_log(self, result: DealerResult):
        self.result_log.append(result)
