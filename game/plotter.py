import dataclasses
import datetime
import logging
import os

import matplotlib.pyplot as plt
import numpy as np

from game.game.game_result import GameResult

SCORES_DIR = "figures/scores"
BANKROLL_DIR = "figures/bankroll"


@dataclasses.dataclass
class GamePlotter:
    game_result: GameResult
    game_amount: int

    def draw_wins(self):
        logging.info("Drawing scores..")

        dealer = self.game_result.dealer
        gamblers = self.game_result.gamblers

        player_labels = [f"{dealer.name} ({dealer.bankroll}B)"] + [
            f"{gambler.name} ({gambler.bankroll}B)" for gambler in gamblers
        ]
        player_wins = [dealer.wins] + [gambler.wins for gambler in gamblers]
        player_losses = [dealer.played - dealer.wins] + [
            gambler.played - gambler.wins for gambler in gamblers
        ]

        weight_counts = {
            "Win": np.array(player_wins),
            "Loss": np.array(player_losses),
        }

        width = 0.5

        fig, ax = plt.subplots()
        bottom = np.zeros(len(player_labels))

        for boolean, weight_count in weight_counts.items():
            ax.bar(player_labels, weight_count, width, label=boolean, bottom=bottom)
            bottom += weight_count

        if self.game_result.actual_played < self.game_amount:
            title = (
                f"Wins and losses after {self.game_amount} games (game terminated after "
                f"{self.game_result.actual_played} games)"
            )
        else:
            title = f"Wins and losses after {self.game_amount} games"

        ax.set_title(title)
        ax.legend(loc="upper right")

        figure_path = f"{SCORES_DIR}/scores_{self.game_amount}_{str(datetime.datetime.utcnow()).replace(' ', '_')}.png"
        self._save_plot(figure_path)

    def draw_bankroll(self):
        if self.game_result.actual_played < self.game_amount:
            title = (
                f"Bankroll after {self.game_amount} games (game terminated after "
                f"{self.game_result.actual_played} games)"
            )
        else:
            title = f"Bankroll after {self.game_amount} games"

        fig, ax = plt.subplots()

        ax.set_title(title)

        ax.set_xlabel("Games")
        ax.set_ylabel("Bankroll")

        for player in self.game_result.gamblers + [self.game_result.dealer]:
            ax.plot(
                np.arange(0, self.game_result.actual_played),
                player.bankroll_log,
                label=player.name,
            )

        ax.legend(loc="upper right")

        figure_path = f"{BANKROLL_DIR}/bankroll_{self.game_amount}_{str(datetime.datetime.utcnow()).replace(' ', '_')}.png"
        self._save_plot(figure_path)

    @staticmethod
    def _save_plot(figure_path: str):
        logging.info(f"Saving figure to {figure_path}..")

        plt.savefig(figure_path)
        plt.show()

    @staticmethod
    def _create_folders():
        if not os.path.isdir(SCORES_DIR):
            os.makedirs(SCORES_DIR)

        if not os.path.isdir(BANKROLL_DIR):
            os.makedirs(BANKROLL_DIR)

    def draw(self):
        self._create_folders()
        self.draw_wins()
        self.draw_bankroll()
