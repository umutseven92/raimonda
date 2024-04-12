import logging
from enum import Enum, auto
from types import ModuleType
from typing import Self, TypeVar

from game.constants import CardValues
from game.deck.card import Card
from game.exceptions import StrategyNotFoundException


class Status(Enum):
    # The player is currently in play, in the game.
    INGAME = auto()

    # The player has busted, but is still in the game.
    BUSTED = auto()

    # The player has lost all their bankroll, and is out of the game.
    BANKRUPT = auto()


T = TypeVar("T")


class Player:
    name: str
    bankroll: float | None
    status: Status = Status.INGAME
    _cards: list[Card] = []

    @property
    def is_busted(self):
        return self.status == Status.BUSTED

    @property
    def is_in_game(self):
        return self.status == Status.INGAME

    @property
    def is_bankrupt(self):
        return self.status == Status.BANKRUPT

    @classmethod
    def from_data(cls, name: str, data: dict) -> Self:
        bankroll = data["bankroll"] if "bankroll" in data else None

        return cls(name=name, bankroll=bankroll)

    @staticmethod
    def _get_strategy(
        data: dict, name: str, default_strategy: T, module: ModuleType
    ) -> T:
        if name not in data:
            func = default_strategy
        else:
            function_name = data[name]
            func = getattr(module, function_name, None)

            if func is None:
                raise StrategyNotFoundException(function_name)

        return func

    def __init__(self, name: str, bankroll: float):
        self.name = name
        self.bankroll = bankroll

    def reset(self):
        self._cards = []
        if not self.is_bankrupt:
            self.status = Status.INGAME

    def bust(self):
        self.status = Status.BUSTED

    def bankrupt(self):
        self.status = Status.BANKRUPT

    def deal_card(self, card: Card):
        logging.debug(f"Dealing {str(card)} to {self.name}.")
        self._cards.append(card)

    def pay(self, amount: float):
        self.bankroll += amount

    def take_away(self, amount: float):
        self.bankroll -= amount

    def get_value(self) -> CardValues:
        """Get the value of the cards (total value of the ranks).

        If one of the cards is an Ace, there can be two different possible values, as Ace can be both 1 or 11.
        """
        first_value = 0
        second_value = 0

        for card in self._cards:
            card_value = card.card_value()
            first_value += card_value[0]
            second_value += card_value[1]

        return first_value, second_value

    def value_is_blackjack(self, blackjack: int) -> bool:
        value = self.get_value()
        return value[0] == blackjack or value[1] == blackjack

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name

    def __repr__(self):
        return f"{self.name}, value {self.get_value()}"
