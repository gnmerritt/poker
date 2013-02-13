"""
Unfortunately not very DRY in here. There's no easy way to expose
cdef enums to Python so some of these are duplicated in both spots
"""

## Suit constants
CLUBS = 0
DIAMONDS = 1
HEARTS = 2
SPADES = 3

# Can use real numbers for all other cards
JACK = 11
QUEEN = 12
KING = 13
ACE = 14

# Hand Score constants
NO_SCORE = -1 # when we haven't calculated the score yet
HIGH_CARD = 0
PAIR = 1
TWO_PAIR = 2
TRIPS = 3
STRAIGHT = 4
FLUSH = 5
FULL_HOUSE = 6
QUADS = 7
STRAIGHT_FLUSH = 8
