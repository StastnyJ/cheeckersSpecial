from enum import Enum
from AI_base import *


class PlayerType(Enum):
    Player = 0
    AI = 1


class MovementDirection(Enum):
    Up = 0
    Down = 1


class Game:
    def __init__(self, player0_type, player1_type, player0_AI = None, player1_AI = None, arena_simulation = False):
        self.player0 = Player(0, player0_type, player0_AI)
        self.player1 = Player(1, player1_type, player1_AI)
        self.playground = [[None] * 8 for _ in range(8)]
        self.player_on_move = self.player0
        self.selected_stone = None
        self.possible_moves = None
        self.force_move = False
        self.no_move = False
        self.highlighted_move = []
        self.highlighted_removed = []
        self.is_AI_simulation = player0_type == PlayerType.AI and player1_type == PlayerType.AI
        self._terminated = False
        self._end_game = False

        for _, stone in self.player0.stones.items():
            col, row = stone.position
            self.playground[col][row] = stone
        for _, stone in self.player1.stones.items():
            col, row = stone.position
            self.playground[col][row] = stone
        
        if self.is_AI_simulation and not arena_simulation:
            self._play_automatic_turn()

    def click_event(self, position):
        if self.is_AI_simulation:
            return self._play_automatic_turn()
        if self.no_move:
            return self._end_turn()
        col, row = position
        if self._is_click_on_my_stone(position) and not self.force_move:
            self._select_stone(self.playground[col][row])
        else:
            if self._is_move_click(position):
                move = self._get_move_object(position)
                reached_end = self._move_stone(move)
                if move.removed_stone is not None and not reached_end and self._can_jump(move.end):
                    self._select_stone(self.playground[move.end[0]][move.end[1]])
                    self.force_move = True
                else:
                    return self._end_turn()
            elif not self.force_move:
                self._remove_selected_stone()
        return False

    def simulate_game(self, timeout):
        from threading import Thread, Event

        stop_event = Event()
        while not self._end_game:
            action_thread = Thread(target=self._play_automatic_turn)
            action_thread.setDaemon(True)
            action_thread.start()
            action_thread.join(timeout=timeout)
            stop_event.set()
            if self._terminated:
                self.player_on_move.score = -2
                break
        return (self.player0.score, self.player1.score)

    def _can_jump(self, pos):
        moves = self._possible_moves(pos)
        for m in moves:
            if m.is_jump():
                return True
        return False

    def _move_stone(self, move):
        self.playground[self.selected_stone.position[0]][self.selected_stone.position[1]] = None
        self.selected_stone.position = move.end
        self.playground[self.selected_stone.position[0]][self.selected_stone.position[1]] = self.selected_stone
        if move.is_jump():
            self._remove_stone(move.removed_stone)
        if self.selected_stone.position[1] in [0, 7]:
            self._remove_stone(self.selected_stone)
            self.player_on_move.score += 1
            return True
        return False

    def _remove_stone(self, stone):
        self.playground[stone.position[0]][stone.position[1]] = None
        del stone.owner.stones[stone.id]

    def _end_turn(self):
        self._remove_selected_stone()
        self.force_move = False
        if self.player_on_move.id == 0:
            self.player_on_move = self.player1
        else:
            self.player_on_move = self.player0
        if len(self._get_all_possible_moves()) <= 0:
            if self.no_move:
                self._end_game = True
                return True
            self.no_move = True
            return False
        self.no_move = False
        if self.player_on_move.type == PlayerType.AI and not self.is_AI_simulation:
            return self._play_automatic_turn()
        return False

    def _play_automatic_turn(self):
        self._terminated = True
        if self.no_move:
            self._terminated = False
            return self._end_turn()
        rotate = self.player_on_move.direction == MovementDirection.Down
        move = self.player_on_move.AI.make_move(self.playground, self.player_on_move.id, rotate)
        if move is None:
            self.player_on_move.score = -1
            self._end_game = True
            self._terminated = False
            return True
        moving_stone = self.playground[move.start[0]][move.start[1]]
        self.playground[move.start[0]][move.start[1]] = None
        moving_stone.position = move.end
        self.playground[move.end[0]][move.end[1]] = moving_stone
        self.highlighted_move = [move.start, move.end]
        self.highlighted_removed = move.removed
        if moving_stone.position[1] in [0, 7]:
            self._remove_stone(moving_stone)
            self.player_on_move.score += 1
        for pos in move.removed:
            self._remove_stone(self.playground[pos[0]][pos[1]])
        self._terminated = False
        return self._end_turn()

    def _is_click_on_my_stone(self, position):
        col, row = position
        stone = self.playground[col][row]
        if stone is None or stone.owner.id != self.player_on_move.id:
            return False
        return True

    def _remove_selected_stone(self):
        self.selected_stone = None
        self.possible_moves = None

    def _select_stone(self, stone):
        self.selected_stone = stone
        self.possible_moves = self._get_possible_moves()

    def _get_possible_moves(self):
        moves = []
        moves = self._possible_moves(self.selected_stone.position)
        moves = self._filter_possible_moves(moves)
        return moves

    def _possible_moves(self, start):
        result = []
        new_row = start[1]
        new_row += 1 if self.player_on_move.direction == MovementDirection.Down else -1
        if new_row < 0 or new_row > 7:
            return []
        adepts = [(start[0] - 1, new_row), (start[0] + 1, new_row)]
        for col, row in adepts:
            if col < 0:
                col += 8
            if col > 7:
                col -= 8
            if self.playground[col][row] is None:
                result.append(Move((col, row), None))
            elif self.playground[col][row].owner.id == self.player_on_move.id:
                continue
            else:
                moves = self._create_jump_moves((col, row), start)
                for m in moves:
                    result.append(m)
        return result

    def _create_jump_moves(self, target, start):
        col, row = target
        new_col = 2 * col - start[0]
        new_row = 2 * row - start[1]
        if new_col < 0:
            new_col += 8
        if new_col > 7:
            new_col -= 8
        if new_row < 0 or new_row > 7:
            return []
        result = []
        if self.playground[new_col][new_row] is None:
            result.append(Move((new_col, new_row), self.playground[col][row]))
        return result

    def _is_move_click(self, position):
        if self.possible_moves is None:
            return False
        for move in self.possible_moves:
            if position == move.end:
                return True
        return False

    def _get_move_object(self, position):
        for move in self.possible_moves:
            if position == move.end:
                return move
        return None

    def _can_someone_jump(self):
        moves = self._get_all_possible_moves()
        for m in moves:
            if m.is_jump():
                return True
        return False

    def _get_all_possible_moves(self):
        result = []
        for _, stone in self.player_on_move.stones.items():
            result += self._possible_moves(stone.position)
        return result

    def _filter_possible_moves(self, moves):
        res = []
        if self._can_someone_jump():
            for m in moves:
                if m.is_jump():
                    res.append(m)
            return res
        return moves


class Stone:
    def __init__(self, id, position, player):
        self.id = id
        self.position = position
        self.owner = player


class Player:
    def __init__(self, id, type, AI_Algorithm = None):
        self.id = id
        self.type = type
        self.stones = self._generate_stones()
        self.direction = MovementDirection.Up if id == 0 else MovementDirection.Down
        self.score = 0
        self.AI = AI_Algorithm

    def _generate_stones(self):
        stones = {}
        stone_id = self.id
        for _ in range(16):
            actual_stone = Stone(stone_id, self._get_init_stone_position(stone_id), self)
            stones[stone_id] = actual_stone
            stone_id += 2
        return stones

    def _get_init_stone_position(self, stone_id):
        modified_id = stone_id // 2
        row = modified_id // 8
        col = modified_id % 8
        if stone_id % 2 == 0:
            row = 7 - row
            col = 7 - col
        return col, row


class Move:
    def __init__(self, end, removed_stone):
        self.end = end
        self.removed_stone = removed_stone

    def is_jump(self):
        return self.removed_stone is not None
