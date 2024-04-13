import dataclasses

from game.player.dealer import Dealer
from game.player.gambler import Gambler


@dataclasses.dataclass
class GameResult:
    actual_played: int
    gamblers: list[Gambler]
    dealer: Dealer
