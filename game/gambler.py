import user.bet_strategies
from game.exceptions import StrategyNotFoundException
from game.player import Player
from game.strategy import BetStrategy, one_bet_strategy


class Gambler(Player):
    bet_strategy: BetStrategy

    def __init__(self, name: str, bet_strategy: BetStrategy, data: dict):
        self.bet_strategy = bet_strategy
        super().__init__(name, data=data)

    @classmethod
    def from_yaml(cls, data: dict):
        if "bet-strategy" not in data:
            bet_strategy = one_bet_strategy
        else:
            function_name = data["bet-strategy"]
            func = getattr(user.bet_strategies, function_name, None)

            if func is None:
                raise StrategyNotFoundException(function_name)

            bet_strategy = func

        return cls(name=data["name"], bet_strategy=bet_strategy, data=data)
