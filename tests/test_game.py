from unittest.mock import MagicMock

import pytest

from game.constants import DEALER_NAME, CardValues
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
from game.strategy import Action


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
        "cards,expected_dealer_bankroll,expected_dealer_bankroll_log,expected_dealer_win,expected_dealer_played,expected_gambler_bankroll,expected_gambler_bankroll_log,expected_gambler_win,expected_gambler_played",
        [
            (  # Dealer win
                [
                    Card(Rank.TWO, Suit.SPADES),  # Gambler, 2
                    Card(Rank.THREE, Suit.CLUBS),  # Dealer, 3
                    Card(Rank.EIGHT, Suit.SPADES),  # Gambler, 10, gambler stays
                    Card(Rank.TEN, Suit.CLUBS),  # Dealer, 13
                    Card(Rank.FOUR, Suit.SPADES),  # Dealer, 17, dealer stays
                ],
                105,  # Dealer bankroll
                [100, 105],  # Dealer bankroll log
                1,  # Dealer wins
                1,  # Dealer played
                15,  # Gambler bankroll
                [20, 15],  # Gambler bankroll log
                0,  # Gambler wins
                1,  # Gambler played
            ),
            (  # Push
                [
                    Card(Rank.TEN, Suit.SPADES),  # Gambler, 10
                    Card(Rank.FIVE, Suit.CLUBS),  # Dealer, 5
                    Card(Rank.SEVEN, Suit.SPADES),  # Gambler, 17, gambler stays
                    Card(Rank.TWO, Suit.CLUBS),  # Dealer, 7
                    Card(Rank.QUEEN, Suit.SPADES),  # Dealer, 17, dealer stays
                ],
                100,  # Dealer bankroll
                [100, 100],  # Dealer bankroll log
                0,  # Dealer wins
                1,  # Dealer played
                20,  # Gambler bankroll
                [20, 20],  # Gambler bankroll log
                0,  # Gambler wins
                1,  # Gambler played
            ),
        ],
    )
    def test_can_play(
        self,
        default_game_config: GameConfig,
        cards: list[Card],
        expected_dealer_bankroll: float,
        expected_dealer_bankroll_log: list[float],
        expected_dealer_win: int,
        expected_dealer_played: int,
        expected_gambler_bankroll: float,
        expected_gambler_bankroll_log: list[float],
        expected_gambler_win: int,
        expected_gambler_played: int,
    ):
        def minimum_bet_strat(
            _bankroll: float, minimum_bet: float, _maximum_bet: float
        ) -> float:
            return minimum_bet

        def gambler_play_strat(
            player_val: CardValues,
            dealer_val: CardValues,
            allowed_actions: list[Action],
        ) -> Action:
            return Action.STAY

        # We reverse the cards because they are popped from the end when being dealt.
        cards.reverse()
        preset_deck = Deck.with_cards(cards)

        game = Game(
            gamblers=[
                Gambler(
                    name="Test Gambler",
                    bankroll=20,
                    play_strategy=gambler_play_strat,
                    bet_strategy=minimum_bet_strat,
                )
            ],
            dealer=Dealer(bankroll=100),
            config=default_game_config,
            deck=preset_deck,
        )

        result = game.play(1)
        gambler = result.gamblers[0]
        dealer = result.dealer

        assert dealer.bankroll == expected_dealer_bankroll
        assert dealer.bankroll_log == expected_dealer_bankroll_log
        assert dealer.wins == expected_dealer_win
        assert dealer.played == expected_dealer_played

        assert gambler.bankroll == expected_gambler_bankroll
        assert gambler.bankroll_log == expected_gambler_bankroll_log
        assert gambler.wins == expected_gambler_win
        assert gambler.played == expected_gambler_played
