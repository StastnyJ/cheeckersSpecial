from AI_base import AIBase
from random import randint


"""
Example of the strategy that generates random moves
"""
class RandomStrategy(AIBase):
    def _solve_problem(self, start):
        possible_moves = self._generate_all_my_moves(start[0], start[1], start[2], start[3])
        return possible_moves[randint(0, len(possible_moves) - 1)]

"""
Your final solution
"""
class FinalSolution(AIBase):
    def _solve_problem(self, start):
        # TODO - write your solution here
        return None


Strategies = {
    "Random": RandomStrategy(),
    "FinalSolution": FinalSolution()
}