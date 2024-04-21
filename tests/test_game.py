from unittest.mock import MagicMock

import pytest

from game.constants import DEALER_NAME
from game.deck.card import Card, Rank, Suit
from game.deck.deck import Deck
from game.exceptions import (
    DuplicateGamblerNameException,
    NotEnoughGamblersException,
    CantNameGamblerDealerException,
    ConfigNotFoundException,
)
from game.game.game import Game
from game.game.game_config import GameConfig
from game.player.dealer import Dealer
from game.player.gambler import Gambler
from game.player.round_result import GamblerResult, DealerResult
from game.strategy import GamblerPlayStrategy, BetStrategy
from .strategies import stay_everytime_play_strat, minimum_bet_play_strat


class TestGame:
    def test_wrong_config_path_raises(self):
        with pytest.raises(ConfigNotFoundException):
            Game.from_yaml_file("non-existent-file.yaml")

    def test_no_gamblers_raises(self):
        with pytest.raises(NotEnoughGamblersException):
            Game(gamblers=[], dealer=MagicMock(), config=MagicMock(), deck=MagicMock())

    def test_duplicate_gambler_name_raises(self):
        gambler_mock = MagicMock()
        gambler_mock.name = "Test"
        gamblers = [gambler_mock, gambler_mock]

        with pytest.raises(DuplicateGamblerNameException):
            Game(
                gamblers=gamblers,
                dealer=MagicMock(),
                config=MagicMock(),
                deck=MagicMock(),
            )

    def test_naming_player_dealer_raises(self):
        gambler_mock = MagicMock()
        gambler_mock.name = DEALER_NAME

        with pytest.raises(CantNameGamblerDealerException):
            Game(
                gamblers=[gambler_mock],
                dealer=MagicMock(),
                config=MagicMock(),
                deck=MagicMock(),
            )

    @pytest.mark.parametrize(
        "game_amount,cards,gambler_play_strat,gambler_bet_strat,expected_dealer_bankroll_log,expected_dealer_round_log,expected_gambler_bankroll_log,expected_gambler_round_log",
        [
            (  # Dealer win
                1,
                [
                    Card(Rank.TWO, Suit.SPADES),  # Gambler, 2
                    Card(Rank.THREE, Suit.CLUBS),  # Dealer, 3
                    Card(Rank.EIGHT, Suit.SPADES),  # Gambler, 10, gambler stays
                    Card(Rank.TEN, Suit.CLUBS),  # Dealer, 13
                    Card(Rank.FOUR, Suit.SPADES),  # Dealer, 17, dealer stays
                ],
                stay_everytime_play_strat,
                minimum_bet_play_strat,
                [100, 105],  # Dealer bankroll log
                [DealerResult.STAY],  # Dealer results
                [20, 15],  # Gambler bankroll log
                [GamblerResult.LOST],  # Gambler results
            ),
            (  # Push
                1,
                [
                    Card(Rank.TEN, Suit.SPADES),  # Gambler, 10
                    Card(Rank.FIVE, Suit.CLUBS),  # Dealer, 5
                    Card(Rank.SEVEN, Suit.SPADES),  # Gambler, 17, gambler stays
                    Card(Rank.TWO, Suit.CLUBS),  # Dealer, 7
                    Card(Rank.QUEEN, Suit.SPADES),  # Dealer, 17, dealer stays
                ],
                stay_everytime_play_strat,
                minimum_bet_play_strat,
                [100, 100],  # Dealer bankroll log
                [DealerResult.STAY],  # Dealer wins
                [20, 20],  # Gambler bankroll log
                [GamblerResult.PUSH],  # Gambler wins
            ),
        ],
    )
    def test_can_play(
        self,
        default_game_config: GameConfig,
        game_amount: int,
        cards: list[Card],
        gambler_play_strat: GamblerPlayStrategy,
        gambler_bet_strat: BetStrategy,
        expected_dealer_bankroll_log: list[float],
        expected_dealer_round_log: list[DealerResult],
        expected_gambler_bankroll_log: list[float],
        expected_gambler_round_log: list[GamblerResult],
    ):
        # We reverse the cards because they are popped from the end when being dealt.
        cards.reverse()
        preset_deck = Deck.with_cards(cards)

        game = Game(
            gamblers=[
                Gambler(
                    name="Test Gambler",
                    bankroll=20,
                    play_strategy=gambler_play_strat,
                    bet_strategy=gambler_bet_strat,
                )
            ],
            dealer=Dealer(bankroll=100),
            config=default_game_config,
            deck=preset_deck,
        )

        result = game.play(game_amount=game_amount)
        gambler = result.gamblers[0]
        dealer = result.dealer

        assert result.actual_played == game_amount
        assert dealer.bankroll == expected_dealer_bankroll_log[-1]
        assert dealer.bankroll_log == expected_dealer_bankroll_log
        assert dealer.result_log == expected_dealer_round_log

        assert gambler.bankroll == expected_gambler_bankroll_log[-1]
        assert gambler.bankroll_log == expected_gambler_bankroll_log
        assert gambler.result_log == expected_gambler_round_log
