from game.constants import DEALER_NAME
from game.player import Player
from game.strategy import default_dealer_play_strategy


class Dealer(Player):
    @classmethod
    def from_yaml(cls, data: dict):
        return cls.from_data(
            name=DEALER_NAME,
            data=data,
            default_play_strategy=default_dealer_play_strategy,
        )
