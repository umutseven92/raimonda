import argparse
import logging

import matplotlib.pyplot as plt
import numpy as np

from game.game import Game
from game.player import Player
from game.strategy import STAND_EVERYTIME_STRAT

parser = argparse.ArgumentParser()
parser.add_argument(
    "-ga", "--game-amount", type=int, default=100, help="How many games to play."
)
parser.add_argument(
    "-d", "--debug", type=bool, default=False, help="Whether to log debug messages."
)


def _create_players(amount: int) -> list[Player]:
    logging.info(f"Creating {amount} players..")

    players = []
    for i in range(amount):
        players.append(
            Player(
                name=f"Player {str(i + 1)}",
                bankroll=200,
                strategy=STAND_EVERYTIME_STRAT,
            )
        )

    return players


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

    plt.show()


if __name__ == "__main__":
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    player_count = 5
    players = _create_players(player_count)

    game = Game(players=players, game_amount=args.game_amount)
    scores = game.play()

    _draw_scores(scores, game_amount=args.game_amount)
