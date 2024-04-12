from game.player import Player
from game.strategy import Action


def player_to_test() -> Player:
    return Player(
        play_strategy=lambda x, y: Action.HIT, bankroll=100, name="Test Player"
    )
