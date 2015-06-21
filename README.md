[![Build Status](https://travis-ci.org/gnmerritt/poker.svg?branch=master)](https://travis-ci.org/gnmerritt/poker)

Poker bot for http://theaigames.com/
====================================

Layout
------

[pokeher/](pokeher/)     source code for the bot

[test/](test/)        unit tests

[standalone/](standalone/)  tools & utilities

[arena/](arena/)       poker simulator for testing

[agents/](agents/)      dummy bots for testing

Install
-------
```shell
pip install -r requirements.txt
make
mkdir -p data
python standalone/preflop_hand_wins.py
make test
```
