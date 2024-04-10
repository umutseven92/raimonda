class NotEnoughPlayersException(Exception):
    def __init__(self):
        self.message = "Not enough players; at least one player is required."


class DuplicatePlayerNameException(Exception):
    def __init__(self):
        self.message = "Duplicate player names."


class CantNamePlayerDealerException(Exception):
    def __init__(self, dealer_name: str):
        self.message = f"Cannot name player {dealer_name}."
