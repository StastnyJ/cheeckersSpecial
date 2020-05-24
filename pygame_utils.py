# -*- coding: utf-8 -*-

from game import *
import pygame as pg
from enum import Enum
import os

_score_box_height = 100
_screen_width = 800
_screen_height = 900 #Scorebox included
_cell_size = _screen_width // 8

class Colors(Enum):
    dark_brown = (68, 52, 17)
    light_brown = (237, 197, 111)
    black = (0, 0, 0)
    white = (255, 255, 255)
    white_selected = (219, 219, 219)
    black_selected = (53, 53, 53)
    green = (0, 255, 0)
    red = (255, 0, 0)
    move_highlight = (119, 169, 203)
    remove_highlight = (247, 90, 50)

def get_screen_height():
    return _screen_height

def get_screen_width():
    return _screen_width

def draw_board(screen):
    for i in range(8):
        for j in range(8):
            pg.draw.rect(screen, Colors.light_brown.value if (i + j) % 2 == 0 else Colors.dark_brown.value, pg.Rect(i * _cell_size, j * _cell_size, _cell_size, _cell_size))

def game_to_screen_coords(position):
    return (position[0] * _cell_size + _cell_size // 2, position[1] * _cell_size + _cell_size // 2)

def transform_coords_from_center_to_edge(position, size):
    return (position[0] - size // 2, position[1] - size // 2)

def draw_stones(screen, stones, color):
    for _, stone in stones.items():
        pg.draw.circle(screen, color, game_to_screen_coords(stone.position), int(_cell_size * 0.4))   
        pg.draw.circle(screen, Colors.black.value, game_to_screen_coords(stone.position), int(_cell_size * 0.4), 1)

def draw_score(screen, game):
    pg.draw.rect(screen, Colors.light_brown.value, pg.Rect(0, _screen_width, _screen_width, _score_box_height))
    pg.draw.rect(screen, Colors.dark_brown.value, pg.Rect(0, _screen_width, _screen_width, 1))
    draw_text(screen, "Score", 64, (_screen_width // 2, _screen_width + _score_box_height // 2), Colors.black.value)
    draw_text(screen, str(game.player0.score), 64, (_cell_size, _screen_width + _score_box_height // 2), Colors.white.value)
    draw_text(screen, str(game.player1.score), 64, (_screen_width - _cell_size, _screen_width + _score_box_height // 2), Colors.black.value)

def draw_no_move_message(screen, player):
    color = "WHITE" if player.direction == MovementDirection.Up else "BLACK"
    draw_text(screen, color + " PLAYER HAS NO POSSIBLE MOVE (Click to continue)", 20, (_screen_width // 2, _screen_width + _score_box_height // 4), Colors.black.value)

def draw(screen, game):
    draw_board(screen)
    draw_highlighted(screen, game)
    draw_stones(screen, game.player0.stones, Colors.white.value)
    draw_stones(screen, game.player1.stones, Colors.black.value)
    if game.selected_stone is not None:
        draw_selected_stone(screen, game.selected_stone)
        draw_possible_moves(screen, game.possible_moves)
    draw_score(screen, game)
    if game.no_move:
        draw_no_move_message(screen, game.player_on_move)

def get_clicked_field_coords(click_pos):
    return (click_pos[0] // _cell_size, click_pos[1] // _cell_size)

def draw_selected_stone(screen, stone):
    pg.draw.circle(screen, Colors.white_selected.value if stone.owner.id == 0 else Colors.black_selected.value, game_to_screen_coords(stone.position), int(_cell_size * 0.4))   
    pg.draw.circle(screen, Colors.black.value, game_to_screen_coords(stone.position), int(_cell_size * 0.4), 1)

def draw_highlighted(screen, game):
    for pos in game.highlighted_move:
        color = Colors.green.value if _is_pos_point(game, pos) else Colors.move_highlight.value
        pg.draw.rect(screen, color, pg.Rect(pos[0] * _cell_size, pos[1] * _cell_size, _cell_size, _cell_size))
    for pos in game.highlighted_removed:
        pg.draw.rect(screen, Colors.remove_highlight.value, pg.Rect(pos[0] * _cell_size, pos[1] * _cell_size, _cell_size, _cell_size))

def draw_possible_moves(screen, moves):
    for move in moves:
        pg.draw.circle(screen, Colors.green.value, game_to_screen_coords(move.end), int(_cell_size * 0.1))
        if move.is_jump():
            c = game_to_screen_coords(move.removed_stone.position)
            pg.draw.line(screen, Colors.red.value, (c[0] - int(_cell_size * 0.4), c[1] - int(_cell_size * 0.4)), (c[0] + int(_cell_size * 0.4), c[1] + int(_cell_size * 0.4)), 5)
            pg.draw.line(screen, Colors.red.value, (c[0] + int(_cell_size * 0.4), c[1] - int(_cell_size * 0.4)), (c[0] - int(_cell_size * 0.4), c[1] + int(_cell_size * 0.4)), 5)

def draw_text(surf, text, size, position, color):
    font = pg.font.Font(pg.font.match_font('Droid Sans Mono'), size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (position[0], position[1] - 20)
    surf.blit(text_surface, text_rect)

def _is_pos_point(game, pos):
    if pos[1] == 0 and game.player_on_move.direction == MovementDirection.Down:
        return True
    if pos[1] == 7 and game.player_on_move.direction == MovementDirection.Up:
        return True
    return False

def wait_for_click():
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return True
            if event.type == pg.MOUSEBUTTONUP:
                return False
        pg.display.flip()
