from AI_base import AIBase
from random import randint
from math import inf

# Base for MinMax based strategies
class MinMaxStrategyBase(AIBase):
    def __init__(self, max_deep):
        self.max_deep = max_deep

    def _get_max(self, pos, act_deep = 0):
        my_stones, enemy_stones, my_score, enemy_score = pos
        moves = self._generate_all_my_moves(my_stones, enemy_stones, my_score, enemy_score)
        if len(moves) == 0:
            return (self._value_position(pos), None)
        best = -inf
        best_moves = [None]
        if act_deep >= self.max_deep:
            for move in moves:
                score = self._value_position(move)
                if score == best:
                    best_moves.append(move)
                if score > best:
                    best = score
                    best_moves = [move]
            return (best, best_moves[randint(0, len(best_moves) - 1)])
        for move in moves:
            act, _ = self._get_min(move, act_deep + 1)
            if act == best:
                best_moves.append(move)
            if act > best:
                best = act
                best_moves = [move]
        return (best, best_moves[randint(0, len(best_moves) - 1)])

    def _get_min(self, pos, act_deep = 0):
        my_stones, enemy_stones, my_score, enemy_score = pos
        moves = self._generate_all_enemy_moves(my_stones, enemy_stones, my_score, enemy_score)
        best = inf
        if act_deep >= self.max_deep:
            for move in moves:
                score = self._value_position(move)
                if score <= best:
                    best = score
            return (best, None)
        for move in moves:
            act, _ = self._get_max(move, act_deep + 1)
            if act <= best:
                best = act
        return (best, None)

    def _value_position(self, position):
        my_stones, enemy_stones, my_score, enemy_score = position
        return my_score - enemy_score + (len(my_stones) - len(enemy_stones)) / 2

    def _get_row_value(self, stone, orientation):
        if orientation == 0:
            return stone // 8
        return 7 - (stone // 8)

class MinMaxStrategyBaseV2(MinMaxStrategyBase):
    def _value_position(self, position):
        my_stones, enemy_stones, my_score, enemy_score = position
        score = 0
        for stone in my_stones:
            score += 0.04 * self._get_row_value(stone, 0) + 0.73
        for stone in enemy_stones:
            score -= 0.04 * self._get_row_value(stone, 1) + 0.73
        score += my_score
        score -= enemy_score
        return score

from time import time

class FinalSolution(AIBase):
    def __init__(self):
        self.time_limit = 0.5
        self.cache = {}
        self.max_moves = 60
        
    def rate_board(self, board):
        return len(board[0]) - len(board[1])

    def represent_board(self, board:tuple):
        return str(board)

    def alphabeta(self, board, is_maximizing_player, alpha, beta, max_depth, current_depth=0):
        r_board = self.represent_board(board)
        try:
            return self.cache[r_board]
        except KeyError:
            pass

        if current_depth >= min(max_depth, self.max_moves):
            value = self.rate_board(board)
            self.cache[r_board] = value
            return value

        if is_maximizing_player:
            best_result = -inf
            for next_board in self._generate_all_my_moves(*board):
                result = self.alphabeta(next_board, False, alpha, beta, max_depth, current_depth + 1)
                best_result = max(best_result, result)
                alpha = max(alpha, best_result)
                if beta <= alpha:
                    break
            return best_result

        else:
            best_result = inf
            for next_board in self._generate_all_enemy_moves(*board):
                result = self.alphabeta(next_board, True, alpha, beta, max_depth, current_depth + 1)
                best_result = min(best_result, result)
                beta = min(beta, best_result)
                if beta <= alpha:
                    break

            return best_result
        
    def _solve_problem(self, start):
        move_start_t = time()
        depth = 0
        possible_moves_rated = [(self.rate_board(board), board) for board in
                                self._generate_all_my_moves(*start)]
        possible_moves_sorted = sorted(possible_moves_rated, key=lambda x: x[0], reverse=True)
        best_move = possible_moves_sorted[0]
        cycle_duration = 0
        timeleft = (move_start_t + self.time_limit) - time()

        while timeleft > 10 * cycle_duration and depth < self.max_moves:
            cycle_start = time()
            self.cache = {}
            new_possible_moves_rated = []
            depth += 2
            for value, possible_move in possible_moves_sorted:
                timeleft = (move_start_t + self.time_limit) - time()
                if timeleft < 0.2:
                    return best_move[1]
                value = self.alphabeta(possible_move, False, -inf, inf, depth)
                new_possible_moves_rated.append((value, possible_move))
            possible_moves_sorted = sorted(new_possible_moves_rated, key=lambda x: x[0], reverse=True)
            best_move = possible_moves_sorted[0]
            cycle_duration = time() - cycle_start
            timeleft = (move_start_t + self.time_limit) - time()
        return best_move[1]


class AlphaBetaMinMax(AIBase):
    def __init__(self, max_deep):
        self.max_deep = max_deep

    def _get_max(self, pos, alpha = -inf, beta = inf, act_deep = 0):
        my_stones, enemy_stones, my_score, enemy_score = pos
        moves = self._generate_all_my_moves(my_stones, enemy_stones, my_score, enemy_score)
        if len(moves) == 0:
            return (self._value_position(pos), None)
        best = -inf
        best_moves = [None]
        if act_deep >= self.max_deep:
            for move in moves:
                score = self._value_position(move)
                if score == best:
                    best_moves.append(move)
                if score > best:
                    best = score
                    best_moves = [move]
            return (best, best_moves[randint(0, len(best_moves) - 1)])
        for move in moves:
            act, _ = self._get_min(move, alpha, beta, act_deep + 1)
            alpha = max(alpha, act)
            if act == best:
                best_moves.append(move)
            if act > best:
                best = act
                best_moves = [move]
            if alpha > beta:
                break
        return (best, best_moves[randint(0, len(best_moves) - 1)])

    def _get_min(self, pos, alpha, beta, act_deep = 0):
        my_stones, enemy_stones, my_score, enemy_score = pos
        moves = self._generate_all_enemy_moves(my_stones, enemy_stones, my_score, enemy_score)
        best = inf
        if act_deep >= self.max_deep:
            for move in moves:
                score = self._value_position(move)
                if score <= best:
                    best = score
            return (best, None)
        for move in moves:
            act, _ = self._get_max(move, alpha, beta, act_deep + 1)
            beta = min(beta, act)
            if act <= best:
                best = act
            if alpha > beta:
                break
        return (best, None)

    def _value_position(self, position):
        my_stones, enemy_stones, my_score, enemy_score = position
        return my_score - enemy_score + (len(my_stones) - len(enemy_stones)) / 2

    def _get_row_value(self, stone, orientation):
        if orientation == 0:
            return stone // 8
        return 7 - (stone // 8)


# Level 0
class RandomStrategy(AIBase):
    def _solve_problem(self, start):
        possible_moves = self._generate_all_my_moves(start[0], start[1], start[2], start[3])
        return possible_moves[randint(0, len(possible_moves) - 1)]

# Level 1
class BackStepStrategy(AIBase):
    def _get_moved_stone(self, before, after):
        for stone in before[0]:
            if not stone in after[0]:
                return stone
    
    def _solve_problem(self, start):
        possible_moves = self._generate_all_my_moves(start[0], start[1], start[2], start[3])
        best = inf
        best_taken = -inf
        best_move = None
        for move in possible_moves:
            act = self._get_moved_stone(start, move)
            taken = len(move[1]) - len(start[1])
            if taken == 0:
                if act < best:
                    best = act
                    best_move = move
            else:
                if best_taken < taken:
                    best_taken = taken
                    best_move = move
        return best_move

# Level 2
class MinMax1(MinMaxStrategyBase):
    def __init__(self):
        super(MinMax1, self).__init__(1)

    def _solve_problem(self, start):
        return self._get_max(start)[1]

# Level 3
class MinMax1V2(MinMaxStrategyBaseV2):
    def __init__(self):
        super(MinMax1V2, self).__init__(1)

    def _solve_problem(self, start):
        return self._get_max(start)[1]

# Level 4
class MinMax2(MinMaxStrategyBase):
    def __init__(self):
        super(MinMax2, self).__init__(2)

    def _solve_problem(self, start):
        return self._get_max(start)[1]

# Level 5
class MinMax2V2(MinMaxStrategyBaseV2):
    def __init__(self):
        super(MinMax2V2, self).__init__(2)

    def _solve_problem(self, start):
        return self._get_max(start)[1]

# Level 6
class AlphaBeta(AlphaBetaMinMax):
    def __init__(self):
        super(AlphaBeta, self).__init__(3)
    
    def _solve_problem(self, start):
        return self._get_max(start)[1]

# Level 7
class AlphaBetaV2(AlphaBetaMinMax):
    def __init__(self):
        super(AlphaBetaV2, self).__init__(3)
    
    def _solve_problem(self, start):
        return self._get_max(start)[1]

    def _value_position(self, position):
        my_stones, enemy_stones, my_score, enemy_score = position
        score = 0
        for stone in my_stones:
            score += 0.04 * self._get_row_value(stone, 0) + 0.73
        for stone in enemy_stones:
            score -= 0.04 * self._get_row_value(stone, 1) + 0.73
        score += my_score
        score -= enemy_score
        return score


Strategies = {
    "Random": RandomStrategy(),
    "BackStep": BackStepStrategy(),
    "MinMax1": MinMax1(),
    "MinMax1V2": MinMax1V2(),
    "MinMax2": MinMax2(),
    "MinMax2V2": MinMax2V2(),
    "AlphaBeta": AlphaBeta(),
    "AlphaBetaV2": AlphaBetaV2(),
    "FinalSolution" : FinalSolution()
}