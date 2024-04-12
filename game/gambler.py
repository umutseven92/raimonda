import user.bet_strategies
from game.exceptions import StrategyNotFoundException
from game.player import Player
from game.strategy import BetStrategy, one_bet_strategy, default_gambler_play_strategy


class Gambler(Player):
    bet_strategy: BetStrategy

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

        val = super().from_data(
            name=data["name"],
            data=data,
            default_play_strategy=default_gambler_play_strategy,
        )

        val.bet_strategy = bet_strategy

        return val

    def run_bet_strategy(self) -> float:
        bet = self.bet_strategy(self.bankroll)
        self.take_away(bet)
        return bet
