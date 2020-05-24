#!/usr/bin/python3.7

from game import *
from example_solution import *
import sys

game = Game(PlayerType.AI, PlayerType.AI, FinalSolution(), RandomStrategy(), True)
print(game.simulate_game(1))

sys.exit()
