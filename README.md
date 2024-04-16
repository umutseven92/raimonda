# Raimonda

A simple-to-use, configurable Blackjack simulator, written in Python.

## Usage

First, copy the example configuration file (`example-config.yaml`), and rename it to `config.yaml`.
Modify it according to your needs.

To run the simulator, do:

```bash
python raimonda.py -ga 1000
```

This will run 1000 games, and generate two graphs; one showing the win and loss rate (saved under `figures/scores`),
and one showing the bankroll over time (saved under `figures/bankroll`).

If you have multiple configurations, or if you want to name your configuration something else, you can use the `-c`
flag:

```bash
python raimonda.py -c another-config.yaml -ga 1000

```

## Customising Bet and Play Behaviour

By default, gamblers will play optimal strategy, and bet the minium amount. The dealer by default will stop at 17.
To change this, you can define your own behaviour and define them in the configuration.

### Gambler Play Strategy

Gambler Play Strategies control how the gamblers play.
To define play strategies for gamblers, add them in the file `user/play_strategies.py` as a function. The function
must take in two `CardValues` (an alias for `tuple[int, int]`), representing the players total card values, and the
dealers total card values,
respectively. The first element of the tuple is the soft value, and the second value is the hard value.

Example gambler play strategy:

```python
def example_gambler_play_strategy(player_val: CardValues, dealer_val: CardValues, can_double_down: bool) -> Action:
    """Example gambler strategy."""

    if player_val[0] > dealer_val[0] and player_val[1] > dealer_val[1]:
        # If the players card values are bigger than the dealers, then stay.
        return Action.STAY
    else:
        # If not, hit.
        return Action.HIT
```

To have a gambler use this strategy, define it as `play-strategy`, under the gambler, in your configuration file, like
so:

```yaml
gamblers:
  - gambler:
      name: "Example Gambler"
      bankroll: 150
      play-strategy: "example_gambler_play_strategy"
```

### Dealer Play Strategy

Dealer Play Strategies control how the dealer plays, and they also go in the file `user/play_strategies.py` as a
function. This function must take in one
`CardValues` (an alias for `tuple[int, int]`), representing the dealers total card values. As with gambler play
strategies, the first element of the tuple is the soft value, and the second value is the hard value.

Example gambler play strategy:

```python
def example_dealer_play_strategy(dealer_val: CardValues) -> Action:
    """Example dealer strategy."""

    if dealer_val[0] % 3 == 0 and dealer_val[1] % 3 == 0:
        # If the dealers card values are divisible by 3, then stay.
        return Action.STAY
    else:
        # If not, hit.
        return Action.HIT
```

To have the dealer use this strategy, define it as `play-strategy`, under the gambler, in your configuration file, like
so:

```yaml
dealer:
  bankroll: 1000
  play-strategy: "example_dealer_play_strategy"
```

### Gambler Bet Strategy

Gambler Bet Strategies define how gamblers bet each round. They go in the file `user/bet_strategies.py` as a function,
and must
take three float parameters, representing the players bankroll, minimum bet amount of the game, and the maximum bet
amount
of the game, respectively, and return a float, representing the bet amount.

Make sure the bet amount you return is valid; it needs to be between the minimum and maximum bet amounts. You don't need
to check
whether the player has enough bankroll for a minimum bet, as bankrupt players won't be able to play in the round, but if
returning
any amount larger than the minimum, make sure the player has enough bankroll.

Dealers don't have bet strategies, as they don't bet.

Example bet strategy:

```python
def example_bet_strategy(
        bankroll: float, minimum_bet: float, maximum_bet: float
) -> float:
    """Example bet strategy."""
    if bankroll > maximum_bet:
        # If the player has more than the maximum bet amount, then bet the maximum.
        return maximum_bet
    else:
        if bankroll > minimum_bet * 2:
            # If the player has less than the maximum bet amount, and has enough to bet double the minimum, then bet
            # double the minimum.
            return minimum_bet * 2
        # If not, bet the minimum.
        return minimum_bet
```