import dataclasses
from typing import Self


@dataclasses.dataclass
class GameConfig:
    minimum_bet: float
    maximum_bet: float
    push_on: int | None
    blackjack: int

    @classmethod
    def from_yaml(cls, data: dict) -> Self:
        minimum_bet = float(data["minimum-bet"])
        maximum_bet = float(data["maximum-bet"])

        push_on = int(data["push-on"]) if "push-on" in data else None
        blackjack = int(data["blackjack"]) if "blackjack" in data else 21

        return cls(
            minimum_bet=minimum_bet,
            maximum_bet=maximum_bet,
            push_on=push_on,
            blackjack=blackjack,
        )
