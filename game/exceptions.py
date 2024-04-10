class NotEnoughPlayersException(Exception):
    def __init__(self):
        self.message = "Not enough players; at least one player is required."


class DuplicatePlayerNameException(Exception):
    def __init__(self):
        self.message = "Duplicate player names."
