import user.play_strategies
from game.constants import DEALER_NAME
from game.exceptions import StrategyNotFoundException
from game.player.player import Player
from game.strategy import DealerPlayStrategy, Action, default_dealer_play_strategy


class Dealer(Player):
    play_strategy: DealerPlayStrategy

    @classmethod
    def from_yaml(cls, data: dict):
        val = cls.from_data(
            name=DEALER_NAME,
            data=data,
        )

        val.play_strategy = cls._get_play_strategy(data)

    @staticmethod
    def _get_play_strategy(data: dict) -> DealerPlayStrategy:
        if "play_strategy" not in data:
            func = default_dealer_play_strategy
        else:
            function_name = data["play-strategy"]
            func = getattr(user.play_strategies, function_name, None)

            if func is None:
                raise StrategyNotFoundException(function_name)

        return func

    def run_play_strategy(self, dealer_stop: int) -> Action:
        return self.play_strategy(self.get_value(), dealer_stop)
