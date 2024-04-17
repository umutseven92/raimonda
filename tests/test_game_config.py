import pytest

from game.exceptions import InvalidDoubleDownConfigException
from game.game.game_config import GameConfig


class TestGameConfig:
    def test_can_parse_double_down_default(self, default_config_dict: dict):
        config = GameConfig.from_yaml(default_config_dict)
        assert config.double_down_allowed == set()

    def test_can_parse_double_down_all(self, default_config_dict: dict):
        default_config_dict["double-down-allowed"] = "*"

        config = GameConfig.from_yaml(default_config_dict)
        assert config.double_down_allowed == set(range(1, 21))

    def test_can_parse_double_down(self, default_config_dict: dict):
        default_config_dict["double-down-allowed"] = [9, 10, 11]

        config = GameConfig.from_yaml(default_config_dict)
        assert config.double_down_allowed == {9, 10, 11}

    def test_invalid_double_down_raises(self, default_config_dict: dict):
        default_config_dict["double-down-allowed"] = [9, 10, 11, 25]

        with pytest.raises(InvalidDoubleDownConfigException):
            GameConfig.from_yaml(default_config_dict)
