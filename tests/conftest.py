import os

import pytest

from game.game.game_config import GameConfig

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_RESOURCES_DIR = os.path.join(TEST_DIR, "resources")


@pytest.fixture(scope="session")
def default_config_dict() -> dict:
    return {"minimum-bet": 5, "maximum-bet": 100}


@pytest.fixture(scope="session")
def default_game_config(default_config_dict: dict) -> GameConfig:
    return GameConfig.from_yaml(data=default_config_dict)
