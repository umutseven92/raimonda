from game.strategy import PlayStrategy


class NotEnoughGamblersException(Exception):
    def __init__(self):
        self.message = "Not enough gamblers; at least one gambler is required."


class DuplicateGamblerNameException(Exception):
    def __init__(self):
        self.message = "Duplicate gambler names."


class CantNameGamblerDealerException(Exception):
    def __init__(self, dealer_name: str):
        self.message = f"Cannot name gambler {dealer_name}."


class StrategyNotFoundException(Exception):
    def __init__(self, strategy_name: str):
        self.message = (
            f"Cannot find strategy {strategy_name}. "
            f"Please make sure you have the strategy defined in user/strategies.py."
        )


class StrategyWrongTypeException(Exception):
    def __init__(self, strategy_name: str):
        self.message = (
            f"Strategy {strategy_name} has wrong type."
            f"Please make sure your defined strategy conforms to the type {str(PlayStrategy)}."
        )
