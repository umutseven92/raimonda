import argparse
import logging

from game.game.game import Game
from game.plotter import GamePlotter

parser = argparse.ArgumentParser()
parser.add_argument(
    "-ga", "--game-amount", type=int, default=100, help="How many games to play."
)
parser.add_argument(
    "-d", "--debug", type=bool, default=False, help="Whether to log debug messages."
)
parser.add_argument(
    "-c", "--config", type=str, default="config.yaml", help="Path to the config file."
)

if __name__ == "__main__":
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    game = Game.from_yaml_file(args.config)
    result = game.play(game_amount=args.game_amount)

    plotter = GamePlotter(game_result=result, game_amount=args.game_amount)

    plotter.draw()
