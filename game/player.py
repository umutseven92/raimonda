import dataclasses
import logging
from enum import Enum, auto

from game.deck import Card
from game.strategy import Strategy, Action


class Status(Enum):
    INGAME = auto()
    BUSTED = auto()


@dataclasses.dataclass
class Player:
    name: str
    bankroll: float
    strategy: Strategy
    status: Status = Status.INGAME
    _cards: list[Card] = dataclasses.field(default_factory=list)

    def reset(self):
        self._cards = []
        self.status = Status.INGAME

    def play(self, dealer_value: tuple[int, int]) -> Action:
        return self.strategy.play(self.get_value(), dealer_value)

    def bust(self):
        self.status = Status.BUSTED

    def deal_card(self, card: Card):
        logging.debug(f"Dealing {str(card)} to {self.name}.")
        self._cards.append(card)

    def get_value(self) -> tuple[int, int]:
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

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name

    def __repr__(self):
        return f"{self.name}, value {self.get_value()}"
