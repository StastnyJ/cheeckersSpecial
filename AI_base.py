from enum import Enum
from random import randint
from math import *

class Directions(Enum):
    lu = 0
    ru = 1
    ld = 2
    rd = 3


class AIMove:
    def __init__(self, start, end, removed):
        self.start = start
        self.end = end
        self.removed = removed 


class Validator:
    def __init__(self, start_position, end_position):
        import types
        self.my_start, self.enemy_start, self.my_start_score, self.enemy_start_score = start_position
        self.invalid = False
        self.toolAI = AIBase()
        if type(end_position) is not tuple:
            self.invalid = True
        elif len(end_position) != 4:
            self.invalid = True
        else:
            self.my_end, self.enemy_end, self.my_end_score, self.enemy_end_score = end_position

    def validate(self):
        if self.invalid:
            return False
        if not self._are_results_correct_type():
            return False
        if not self._are_scores_ok():
            return False
        if not self._are_stones_placed_well():
            return False
        if not self._moved_with_one_stone():
            return False        
        if not self._didint_enemy_moved():
            return False
        my_move = self._get_my_move()
        if self._is_jump(my_move):
            if not self._is_jump_valid(my_move):
                return False
            if not self._is_jump_compleated(my_move):
                return False
        else:
            if self._can_i_jump():
                return False
            if not self._is_classic_move_valid(my_move):
                return False
        return True

    def _are_scores_ok(self):
        if self.enemy_start_score != self.enemy_end_score:
            return False
        if self.my_end_score == self.my_start_score:
            return True
        if self.my_end_score == self.my_start_score + 1 and len(self.my_start) - 1 == len(self.my_end):
            return True
        return False

    def _are_results_correct_type(self):
        return True #TODO

    def _are_stones_placed_well(self):
        for stone in self.my_end:
            if stone < 0 or stone > 63:
                return False
            if stone in self.enemy_end:
                return False
        for stone in self.enemy_end:
            if stone < 0 or stone > 63:
                return False
            if stone in self.my_end:
                return False
        return True

    def _moved_with_one_stone(self):
        if len(self.my_end) > len(self.my_start):
            return False
        diffs = 0
        for stone in self.my_start:
            if stone not in self.my_end:
                diffs += 1
        return diffs == 1

    def _didint_enemy_moved(self):
        for stone in self.enemy_end:
            if stone not in self.enemy_start:
                return False
        return True

    def _get_my_move(self):
        start = None
        end = None
        for stone in self.my_start:
            if stone not in self.my_end:
                start = stone
                break
        for stone in self.my_end:
            if stone not in self.my_start:
                end = stone
                break
        return (start, end)

    def _is_jump(self, move):
        start, end = move
        return len(self.enemy_end) < len(self.enemy_start)
    
    def _can_i_jump(self):
        move = self.toolAI._generate_all_my_moves(self.my_start, self.enemy_start, self.my_start_score, self.enemy_start_score)[0]
        return len(move[1]) < len(self.enemy_start)

    def _is_jump_compleated(self, move):
        _, end = move
        if end is None:
            return True
        if end // 8 > 5:
            return True
        lu, ru, _, _ = self.toolAI._get_neighbor_positions(end)
        if lu in self.enemy_start:
            if self._is_pos_free(self.toolAI._get_neighbor_position(lu, Directions.lu)):
                return False
        if ru in self.enemy_start:
            if self._is_pos_free(self.toolAI._get_neighbor_position(ru, Directions.ru)):
                return False
        return True


    def _is_classic_move_valid(self, move):
        start, end = move
        if end is not None:
            if not self._is_pos_free(end):
                return False
            return end in self.toolAI._get_neighbor_positions(start)[:2]
        else:
            if start // 8 != 6:
                return False
            for pos in self.toolAI._get_neighbor_positions(start)[:2]:
                if self._is_pos_free(pos):
                    return True
            return False

    def _get_jumped_stones(self):
        res = []
        for stone in self.enemy_start:
            if stone not in self.enemy_end:
                res.append(stone)
        return sorted(res)

    def _is_pos_free(self, pos):
        return pos not in self.my_start and pos not in self.enemy_start

    def _is_jump_valid(self, move):
        pos, end = move
        jump_stones = self._get_jumped_stones()
        for stone in jump_stones:
            lu, ru, _, _ = self.toolAI._get_neighbor_positions(pos)
            if stone == lu:
                target = self.toolAI._get_neighbor_position(lu, Directions.lu)
            elif stone == ru:
                target = self.toolAI._get_neighbor_position(ru, Directions.ru)
            else:
                return False
            if not self._is_pos_free(target):
                return False
            pos = target
        return (pos // 8 == 7 and end == None) or pos == end  
            

class AIBase:
    def _format_input(self, playground, my_id, rotate):
        enemy_stones = set()
        my_stones = set()
        my_score = 0
        enemy_score = 0
        for row in playground:
            for pos in row:
                if pos is None:
                    continue
                if pos.owner.id == my_id:
                    my_score = pos.owner.score
                    my_stones.add(self._coords_to_num(pos.position, rotate))
                else:
                    enemy_score = pos.owner.score
                    enemy_stones.add(self._coords_to_num(pos.position, rotate))
        return (my_stones, enemy_stones, my_score, enemy_score)

    def _coords_to_num(self, coords, rotate):
        col, row = coords
        col = 7 - col
        return 8 * row + col % 8 if rotate else 63 - (8 * row + col % 8)

    def _num_to_coords(self, num, rotate):
        if not rotate:
            num = 63 - num
        return (7 - num % 8, num // 8)

    def _format_output(self, start_position, end_position, rotate):
        my_start, enemy_start, _, _ = start_position
        my_end, enemy_end, _, _ = end_position
        end = None
        for m in my_start.symmetric_difference(my_end):
            if m in my_start:
                start = self._num_to_coords(m, rotate)
            else:
                end = self._num_to_coords(m, rotate)
        removed = []
        for r in enemy_start - enemy_end:
            removed.append(self._num_to_coords(r, rotate))
        if end is None:
            end = self._num_to_coords(self._find_end_for_start(self._coords_to_num(start, rotate), my_start, enemy_start), rotate)
        return AIMove(start, end, removed)

    def _find_end_for_start(self, start, my_stones, enemy_stones):
        if start > 55:
            return start
        lu, ru, _, _ = self._get_neighbor_positions(start)
        must_jump = start < 48
        normal, jump = self._generate_moves(my_stones, enemy_stones, 0, 0, start, lu, Directions.lu, 0)
        if must_jump:
            for j in jump:
                if len(j[0]) < len(my_stones):
                    new_pos = self._get_neighbor_position(lu, Directions.lu)
                    new_my = my_stones
                    new_enemy = enemy_stones
                    new_my.remove(start)
                    new_my.add(new_pos)
                    new_enemy.remove(lu)
                    return self._find_end_for_start(new_pos, new_my, new_enemy)
            new_pos = self._get_neighbor_position(ru, Directions.ru)
            new_my = my_stones
            new_enemy = enemy_stones
            new_my.remove(start)
            new_my.add(new_pos)
            new_enemy.remove(ru)
            return self._find_end_for_start(new_pos, new_my, new_enemy)       
        else:
            if len(normal) > 0:
                return lu
            else:
                return ru

    def _get_neighbor_positions(self, pos):
        lu = pos + 7
        ru = pos + 9
        ld = pos - 9
        rd = pos - 7
        if pos % 8 == 0:
            lu = pos + 15
            ld = pos - 1
        if pos % 8 == 7:
            ru = pos + 1
            rd = pos - 15
        if pos < 8:
            ld = None
            rd = None
        if pos > 55:
            lu = None
            ru = None
        return lu, ru, ld, rd

    def _get_neighbor_position(self, pos, direction):
        return self._get_neighbor_positions(pos)[direction.value]

    def make_move(self, playground, my_id, rotate = False):
        start_position = self._format_input(playground, my_id, rotate)
        end_position = self._solve_problem(start_position)
        val = Validator(start_position, end_position)
        if val.validate():
            return self._format_output(start_position, end_position, rotate)
        print("INVALID")
        return None

    def _solve_problem(self, start):
        print("AIBase")
        return start

    def _generate_all_my_moves(self, my_stones, enemy_stones, my_score, enemy_score):
        return self._generate_all_possible_moves(my_stones, enemy_stones, my_score, enemy_score, 0)        

    def _generate_all_enemy_moves(self, my_stones, enemy_stones, my_score, enemy_score):
        moves = self._generate_all_possible_moves(enemy_stones, my_stones, enemy_score, my_score, 1)
        res = []
        for m in moves:
            enemy_new, my_new, enemy_score, my_score = m
            res.append((my_new, enemy_new, my_score, enemy_score))
        return res

    def _generate_all_possible_moves(self, my_stones, enemy_stones, my_score, enemy_score, orientation):
        jump_moves = []
        normal_moves = []
        for stone in my_stones:
            act, act_jump = self._generate_possible_moves(my_stones, enemy_stones, my_score, enemy_score, stone, orientation)
            jump_moves += act_jump
            if len(jump_moves) == 0:
                normal_moves += act
        return jump_moves if len(jump_moves) > 0 else normal_moves
       
    def _generate_possible_moves(self, my_stones, enemy_stones, my_score, enemy_score, actual_stone, orientation):
        lu, ru, ld, rd = self._get_neighbor_positions(actual_stone)
        res_normal = []
        res_jump = []
        if orientation == 0:
            normal, jump = self._generate_moves(my_stones, enemy_stones, my_score, enemy_score, actual_stone, lu, Directions.lu, orientation)
        else:
            normal, jump = self._generate_moves(my_stones, enemy_stones, my_score, enemy_score, actual_stone, ld, Directions.ld, orientation)
        res_normal += normal
        res_jump += jump
        if orientation == 0:
            normal, jump = self._generate_moves(my_stones, enemy_stones, my_score, enemy_score, actual_stone, ru, Directions.ru, orientation)
        else:
            normal, jump = self._generate_moves(my_stones, enemy_stones, my_score, enemy_score, actual_stone, rd, Directions.rd, orientation)
        res_normal += normal
        res_jump += jump
        return (res_normal, res_jump)
    
    def _generate_moves(self, my_stones, enemy_stones, my_score, enemy_score, actual_stone, target, direction, orientation):
        if target is None:
            return ([], [])
        if target in my_stones:
            return ([], [])
        if target in enemy_stones:
            new_pos = self._get_neighbor_position(target, direction)
            if new_pos is None or new_pos in my_stones or new_pos in enemy_stones:
                return ([], [])
            new_my = set(my_stones)
            new_enemy = set(enemy_stones)
            new_enemy.remove(target)
            new_my_score = my_score
            if actual_stone in new_my:
                new_my.remove(actual_stone)
            if new_pos < 56:
                new_my.add(new_pos)
            else:
                new_my_score += 1
            _, moves = self._generate_possible_moves(new_my, new_enemy, new_my_score, enemy_score, new_pos, orientation)
            if len(moves) > 0:
                return ([], moves)
            return ([], [(new_my, new_enemy, new_my_score, enemy_score)])
        new_my = set(my_stones)
        new_my_score = my_score
        if actual_stone in new_my:
            new_my.remove(actual_stone)
        if target < 56:
            new_my.add(target)
        else:
            new_my_score += 1
        return ([(new_my, enemy_stones, new_my_score, enemy_score)], [])
