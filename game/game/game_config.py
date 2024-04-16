import dataclasses
from typing import Self, TypeVar

from game.exceptions import InvalidDoubleDownConfigException

T = TypeVar("T")


@dataclasses.dataclass
class GameConfig:
    minimum_bet: float
    maximum_bet: float
    push_on: int | None
    blackjack: int
    win_pays: float
    blackjack_pays: float
    double_down_allowed: set[int]

    @staticmethod
    def retrieve_with_default(data: dict, key: str, default: T) -> T:
        return data[key] if key in data else default

    @staticmethod
    def parse_double_down(data: dict, key: str) -> set[int]:
        if key not in data:
            # Double down not allowed.
            return set()

        values: str | list[int] = data[key]

        if values == "*":
            # Can double down on all values.
            return set(range(1, 21))

        assert isinstance(values, list)

        for value in values:
            if value < 1 or value > 21:
                raise InvalidDoubleDownConfigException()

        return set(values)

    @classmethod
    def from_yaml(cls, data: dict) -> Self:
        minimum_bet = float(data["minimum-bet"])
        maximum_bet = float(data["maximum-bet"])

        push_on = GameConfig.retrieve_with_default(data, "push-on", None)
        blackjack = GameConfig.retrieve_with_default(data, "blackjack", 21)
        win_pays = GameConfig.retrieve_with_default(data, "win-pays", 0.5)
        blackjack_pays = GameConfig.retrieve_with_default(data, "blackjack-pays", 1.5)
        double_down_allowed = GameConfig.parse_double_down(data, "double-down-allowed")

        return cls(
            minimum_bet=minimum_bet,
            maximum_bet=maximum_bet,
            push_on=push_on,
            blackjack=blackjack,
            win_pays=win_pays,
            blackjack_pays=blackjack_pays,
            double_down_allowed=double_down_allowed,
        )
