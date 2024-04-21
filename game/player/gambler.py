import user.bet_strategies
import user.play_strategies
from game.constants import CardValues
from game.exceptions import InvalidBetException, InvalidActionException
from game.player.player import Player
from game.player.round_result import GamblerResult
from game.strategy import (
    BetStrategy,
    default_gambler_play_strategy,
    GamblerPlayStrategy,
    Action,
    minimum_bet_strategy,
)


class Gambler(Player):
    def __init__(
        self,
        name: str,
        bankroll: float,
        bet_strategy: BetStrategy,
        play_strategy: GamblerPlayStrategy,
    ):
        self.bet_strategy = bet_strategy
        self.play_strategy = play_strategy
        self.result_log: list[GamblerResult] = []

        super().__init__(name, bankroll)

    @classmethod
    def from_yaml(cls, data: dict):
        val = cls(
            name=data["name"],
            bankroll=data["bankroll"],
            bet_strategy=cls._get_bet_strategy(data),
            play_strategy=cls._get_play_strategy(data),
        )

        return val

    @staticmethod
    def _get_bet_strategy(data: dict) -> BetStrategy:
        return Player._get_strategy(
            data, "bet-strategy", minimum_bet_strategy, user.bet_strategies
        )

    @staticmethod
    def _get_play_strategy(data: dict) -> GamblerPlayStrategy:
        return Player._get_strategy(
            data, "play-strategy", default_gambler_play_strategy, user.play_strategies
        )

    def run_bet_strategy(self, minimum_bet: float, maximum_bet: float) -> float:
        bet = self.bet_strategy(self.bankroll, minimum_bet, maximum_bet)
        if bet < minimum_bet or bet > maximum_bet:
            raise InvalidBetException(bet, minimum_bet, maximum_bet)

        self.take_away(bet)
        return bet

    def run_play_strategy(
        self, dealer_value: CardValues, allowed_actions: list[Action]
    ) -> Action:
        action = self.play_strategy(self.get_value(), dealer_value, allowed_actions)
        if action not in allowed_actions:
            raise InvalidActionException(action, allowed_actions)

        return action

    def add_result_to_log(self, result: GamblerResult):
        self.result_log.append(result)
