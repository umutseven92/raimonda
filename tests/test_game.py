from unittest.mock import MagicMock

import pytest

from game.constants import DEALER_NAME
from game.exceptions import (
    DuplicateGamblerNameException,
    NotEnoughGamblersException,
    CantNameGamblerDealerException,
    ConfigNotFoundException,
)
from game.game.game import Game


class TestGame:
    def test_wrong_config_path_raises(self):
        with pytest.raises(ConfigNotFoundException):
            Game.from_yaml_file("non-existent-file.yaml")

    def test_no_gamblers_raises(self):
        with pytest.raises(NotEnoughGamblersException):
            Game(gamblers=[], dealer=MagicMock(), config=MagicMock())

    def test_duplicate_gambler_name_raises(self):
        gambler_mock = MagicMock()
        gambler_mock.name = "Test"
        gamblers = [gambler_mock, gambler_mock]

        with pytest.raises(DuplicateGamblerNameException):
            Game(gamblers=gamblers, dealer=MagicMock(), config=MagicMock())

    def test_naming_player_dealer_raises(self):
        gambler_mock = MagicMock()
        gambler_mock.name = DEALER_NAME

        with pytest.raises(CantNameGamblerDealerException):
            Game(gamblers=[gambler_mock], dealer=MagicMock(), config=MagicMock())

    def test_can_play(self):
        game = Game.from_yaml_file("resources/test_config.yaml")
        result = game.play(10)

        assert result.actual_played == len(result.dealer.bankroll_log)
        assert result.actual_played >= result.dealer.wins

        for gambler in result.gamblers:
            assert result.actual_played == len(gambler.bankroll_log)
            assert result.actual_played >= gambler.wins
