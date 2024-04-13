import dataclasses
from typing import Self


@dataclasses.dataclass
class GameConfig:
    minimum_bet: float
    maximum_bet: float
    dealer_stop: int
    push_on: int | None
    blackjack: int

    @classmethod
    def from_yaml(cls, data: dict) -> Self:
        minimum_bet = float(data["minimum-bet"])
        maximum_bet = float(data["maximum-bet"])

        push_on = int(data["push-on"]) if "push-on" in data else None
        blackjack = int(data["blackjack"]) if "blackjack" in data else 21
        dealer_stop = int(data["dealer-stop"]) if "dealer-stop" in data else 17

        return cls(
            minimum_bet=minimum_bet,
            maximum_bet=maximum_bet,
            push_on=push_on,
            blackjack=blackjack,
            dealer_stop=dealer_stop,
        )
