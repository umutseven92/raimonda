from unittest.mock import MagicMock

import pytest

from game.constants import DEALER_NAME
from game.exceptions import (
    DuplicateGamblerNameException,
    NotEnoughGamblersException,
    CantNameGamblerDealerException,
)
from game.game import Game


class TestGame:
    def test_no_gamblers_raises(self):
        with pytest.raises(NotEnoughGamblersException):
            Game(gamblers=[], dealer=MagicMock())

    def test_duplicate_gambler_name_raises(self):
        gambler_mock = MagicMock()
        gambler_mock.name = "Test"
        gamblers = [gambler_mock, gambler_mock]

        with pytest.raises(DuplicateGamblerNameException):
            Game(gamblers=gamblers, dealer=MagicMock())

    def test_naming_player_dealer_raises(self):
        gambler_mock = MagicMock()
        gambler_mock.name = DEALER_NAME

        with pytest.raises(CantNameGamblerDealerException):
            Game(gamblers=[gambler_mock], dealer=MagicMock())

    def test_can_play(self):
        pass
        # game_amount = 1
        # player(
        #     name="Dealer",
        #     bankroll=200,
        #     play_strategy=STAND_EVERYTIME_STRATEGY,
        # )
        # players = [
        #     Player(
        #         name="Test Player 1",
        #         bankroll=200,
        #         play_strategy=STAND_EVERYTIME_STRATEGY,
        #     ),
        #     Player(
        #         name="Test Player 2",
        #         bankroll=200,
        #         play_strategy=STAND_EVERYTIME_STRATEGY,
        #     ),
        # ]
        # game = Game(gamblers=players, game_amount=game_amount)
        #
        # scores = game.play()
        #
        # # Scores include the players, and one dealer.
        # assert len(scores.keys()) == len(players) + 1
        #
        # assert all([val <= 100 for val in scores.values()])
