import user.play_strategies
from game.constants import DEALER_NAME
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

        return val

    @staticmethod
    def _get_play_strategy(data: dict) -> DealerPlayStrategy:
        return Player._get_strategy(
            data, "play-strategy", default_dealer_play_strategy, user.play_strategies
        )

    def run_play_strategy(self, dealer_stop: int) -> Action:
        return self.play_strategy(self.get_value(), dealer_stop)
