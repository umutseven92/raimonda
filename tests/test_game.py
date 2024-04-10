import pytest

from game.exceptions import DuplicatePlayerNameException, NotEnoughPlayersException
from game.game import Game
from game.player import Player
from game.strategy import STAND_EVERYTIME_STRAT


class TestGame:
    def test_no_players_raises(self):
        with pytest.raises(NotEnoughPlayersException):
            Game(players=[], game_amount=100)

    def test_duplicate_player_name_raises(self):
        players = [
            Player(name="Test Player", bankroll=200, strategy=STAND_EVERYTIME_STRAT),
            Player(name="Test Player", bankroll=220, strategy=STAND_EVERYTIME_STRAT),
        ]

        with pytest.raises(DuplicatePlayerNameException):
            Game(players=players, game_amount=100)

    def test_can_play(self):
        game_amount = 1
        players = [
            Player(name="Test Player 1", bankroll=200, strategy=STAND_EVERYTIME_STRAT),
            Player(name="Test Player 2", bankroll=200, strategy=STAND_EVERYTIME_STRAT),
        ]
        game = Game(players=players, game_amount=game_amount)

        scores = game.play()

        # Scores include the players, and one dealer.
        assert len(scores.keys()) == len(players) + 1

        assert all([val <= 100 for val in scores.values()])
