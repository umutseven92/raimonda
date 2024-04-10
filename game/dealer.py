from game.constants import DEALER_NAME
from game.player import Player


class Dealer(Player):
    @classmethod
    def from_yaml(cls, data: dict):
        return cls(name=DEALER_NAME, data=data)
