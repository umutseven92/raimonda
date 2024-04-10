import pytest

from game.exceptions import (
    DuplicateGamblerNameException,
    NotEnoughGamblersException,
    CantNameGamblerDealerException,
)
from game.game import Game
from game.player import Player
from game.strategy import STAND_EVERYTIME_STRATEGY


class TestGame:
    def test_no_players_raises(self):
        with pytest.raises(NotEnoughGamblersException):
            Game(gamblers=[], game_amount=100)

    def test_duplicate_player_name_raises(self):
        players = [
            Player(
                name="Test Player", bankroll=200, play_strategy=STAND_EVERYTIME_STRATEGY
            ),
            Player(
                name="Test Player", bankroll=220, play_strategy=STAND_EVERYTIME_STRATEGY
            ),
        ]

        with pytest.raises(DuplicateGamblerNameException):
            Game(gamblers=players, game_amount=100)

    def test_naming_player_dealer_raises(self):
        with pytest.raises(CantNameGamblerDealerException):
            Game(
                gamblers=[
                    Player(
                        name="Dealer",
                        bankroll=200,
                        play_strategy=STAND_EVERYTIME_STRATEGY,
                    )
                ],
                game_amount=100,
            )

    def test_can_play(self):
        game_amount = 1
        players = [
            Player(
                name="Test Player 1",
                bankroll=200,
                play_strategy=STAND_EVERYTIME_STRATEGY,
            ),
            Player(
                name="Test Player 2",
                bankroll=200,
                play_strategy=STAND_EVERYTIME_STRATEGY,
            ),
        ]
        game = Game(gamblers=players, game_amount=game_amount)

        scores = game.play()

        # Scores include the players, and one dealer.
        assert len(scores.keys()) == len(players) + 1

        assert all([val <= 100 for val in scores.values()])
