import argparse
import datetime
import logging

import matplotlib.pyplot as plt
import numpy as np

from game.game import Game
from game.player import Player

parser = argparse.ArgumentParser()
parser.add_argument(
    "-ga", "--game-amount", type=int, default=100, help="How many games to play."
)
parser.add_argument(
    "-d", "--debug", type=bool, default=False, help="Whether to log debug messages."
)


def _draw_scores(scores: dict[Player, int], game_amount: int):
    logging.info("Drawing scores..")

    all_players = scores.keys()
    player_labels = [player.name for player in all_players]
    player_wins = [scores[player] for player in all_players]
    player_losses = [game_amount - scores[player] for player in all_players]

    weight_counts = {
        "Win": np.array(player_wins),
        "Loss": np.array(player_losses),
    }
    width = 0.5

    fig, ax = plt.subplots()
    bottom = np.zeros(len(all_players))

    for boolean, weight_count in weight_counts.items():
        ax.bar(player_labels, weight_count, width, label=boolean, bottom=bottom)
        bottom += weight_count

    ax.set_title(f"Wins and losses after {game_amount} games")
    ax.legend(loc="upper right")

    figure_path = f"figures/scores_{game_amount}_{str(datetime.datetime.utcnow()).replace(' ', '_')}.png"
    logging.info(f"Saving figure to {figure_path}..")

    plt.savefig(figure_path)
    plt.show()


if __name__ == "__main__":
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    game = Game.from_yaml_file("config.yaml")
    scores = game.play(game_amount=args.game_amount)

    _draw_scores(scores, game_amount=args.game_amount)
