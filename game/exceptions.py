from game.strategy import GamblerPlayStrategy


class ConfigNotFoundException(Exception):
    def __init__(self, path: str):
        super().__init__(f"Cannot find config file at {path}.")


class NotEnoughGamblersException(Exception):
    def __init__(self):
        super().__init__("Not enough gamblers; at least one gambler is required.")


class DuplicateGamblerNameException(Exception):
    def __init__(self):
        super().__init__("Duplicate gambler names.")


class CantNameGamblerDealerException(Exception):
    def __init__(self, dealer_name: str):
        super().__init__(f"Cannot name gambler {dealer_name}.")


class StrategyNotFoundException(Exception):
    def __init__(self, strategy_name: str):
        super().__init__(
            f"Cannot find strategy {strategy_name}. "
            f"Please make sure you have the strategy defined in user/strategies.py."
        )


class StrategyWrongTypeException(Exception):
    def __init__(self, strategy_name: str):
        super().__init__(
            f"Strategy {strategy_name} has wrong type."
            f"Please make sure your defined strategy conforms to the type {str(GamblerPlayStrategy)}."
        )


class NotEnoughBankrollException(Exception):
    def __init__(self, bankroll: float, attempted_bet: float):
        super().__init__(f"Not enough bankroll ({bankroll} for bet {attempted_bet}.")
