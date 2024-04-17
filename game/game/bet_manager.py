import logging

from game.player.dealer import Dealer
from game.player.gambler import Gambler


class BetManager:
    def __init__(self, minimum_bet: float, maximum_bet: float, blackjack_value: int):
        self.bets: dict[Gambler, float] = {}
        self.minimum_bet = minimum_bet
        self.maximum_bet = maximum_bet
        self.blackjack_value = blackjack_value

    def collect_bets(self, in_game_gamblers: list[Gambler]):
        bets = {}
        for gambler in in_game_gamblers:
            bet = gambler.run_bet_strategy(
                minimum_bet=self.minimum_bet,
                maximum_bet=self.maximum_bet,
            )
            bets[gambler] = bet

        self.bets = bets

    def distribute_bets(
        self,
        dealer: Dealer,
        winning_gamblers: list[Gambler],
        losing_gamblers: list[Gambler],
        pushed_gamblers: list[Gambler],
    ):
        # All lost bets go to the dealer.
        for lost_gambler in losing_gamblers:
            lost_bet = self.bets[lost_gambler]
            logging.debug(f"{lost_gambler} lost {lost_bet} to {dealer.name}.")

            dealer.pay(lost_bet)

        # The winning players get paid 1:2, except for when it is blackjack, in which case they get paid 2:3.
        for winning_gambler in winning_gamblers:
            winning_bet = self.bets[winning_gambler]
            dealer.take_away(winning_bet)
            if winning_gambler.value_is_blackjack(self.blackjack_value):
                amount = winning_bet + (winning_bet * 1.5)
                logging.debug(
                    f"Blackjack! {winning_gambler} won {amount} from {dealer.name}."
                )

                winning_gambler.pay(amount)
            else:
                amount = winning_bet + (winning_bet * 0.5)
                logging.debug(f"{winning_gambler} won {amount} from {dealer.name}.")

                winning_gambler.pay(amount)

        # Pushed gamblers get their money back.
        for pushed_gambler in pushed_gamblers:
            pushed_bet = self.bets[pushed_gambler]
            pushed_gambler.pay(pushed_bet)
