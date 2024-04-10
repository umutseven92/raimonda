import logging
from enum import Enum, auto

import user.play_strategies
from game.constants import CardValues
from game.deck import Card
from game.exceptions import StrategyNotFoundException
from game.strategy import PlayStrategy, Action, default_dealer_play_strategy


class Status(Enum):
    INGAME = auto()
    BUSTED = auto()


class Player:
    name: str
    play_strategy: PlayStrategy
    bankroll: float | None
    status: Status = Status.INGAME
    _cards: list[Card] = []

    def __init__(self, name: str, data: dict):
        bankroll = data["bankroll"] if "bankroll" in data else None
        if "play-strategy" not in data:
            play_strategy = default_dealer_play_strategy
        else:
            function_name = data["play-strategy"]
            func = getattr(user.play_strategies, function_name, None)

            if func is None:
                raise StrategyNotFoundException(function_name)

            play_strategy = func

        self.name = name
        self.play_strategy = play_strategy
        self.bankroll = bankroll

    def reset(self):
        self._cards = []
        self.status = Status.INGAME

    def play(self, dealer_value: CardValues) -> Action:
        return self.play_strategy(self.get_value(), dealer_value)

    def bust(self):
        self.status = Status.BUSTED

    def deal_card(self, card: Card):
        logging.debug(f"Dealing {str(card)} to {self.name}.")
        self._cards.append(card)

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

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name

    def __repr__(self):
        return f"{self.name}, value {self.get_value()}"
