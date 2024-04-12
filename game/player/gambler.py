import user.bet_strategies
import user.play_strategies
from game.constants import CardValues
from game.exceptions import StrategyNotFoundException
from game.player.player import Player
from game.strategy import (
    BetStrategy,
    minimum_bet_strategy,
    default_gambler_play_strategy,
    GamblerPlayStrategy,
    Action,
)


class Gambler(Player):
    bet_strategy: BetStrategy
    play_strategy: GamblerPlayStrategy

    @classmethod
    def from_yaml(cls, data: dict):
        val = super().from_data(name=data["name"], data=data)

        val.bet_strategy = cls._get_bet_strategy(data)
        val.play_strategy = cls._get_play_strategy(data)

        return val

    @staticmethod
    def _get_bet_strategy(data: dict) -> BetStrategy:
        if "bet-strategy" not in data:
            func = minimum_bet_strategy
        else:
            function_name = data["bet-strategy"]
            func = getattr(user.bet_strategies, function_name, None)

            if func is None:
                raise StrategyNotFoundException(function_name)

        return func

    @staticmethod
    def _get_play_strategy(data: dict) -> GamblerPlayStrategy:
        if "play_strategy" not in data:
            func = default_gambler_play_strategy
        else:
            function_name = data["play-strategy"]
            func = getattr(user.play_strategies, function_name, None)

            if func is None:
                raise StrategyNotFoundException(function_name)

        return func

    def run_bet_strategy(self, minimum_bet: float, maximum_bet: float) -> float:
        bet = self.bet_strategy(self.bankroll, minimum_bet, maximum_bet)
        self.take_away(bet)
        return bet

    def run_play_strategy(self, dealer_value: CardValues) -> Action:
        return self.play_strategy(self.get_value(), dealer_value)
