#!/usr/bin/python3.7

import requests
import json
from enum import Enum
from game import *
from example_solution import *
import sys

GET_URL = 'https://ksi-api.borysek.eu/getEvaluations'
POST_URL = 'https://ksi-api.borysek.eu/updateEvaluations'
KEY = 'f7efa29687adc65aa292afea265dc4e1'

class PlayerColors(Enum):
    White = 0
    Black = 1

def get_submissions():
    query = {
        "key": KEY,
        "onlyLast": 1
    }
    response = requests.request("GET", GET_URL, data="", params=query)
    if response.status_code != 200:
        print("Invalid response")
        # TODO - someting?
    return json.loads(response.text)

def get_class_from_code(code):
    try:
        exec(code, None, globals())
        return FinalSolution()
    except:
        return None

def evaluate_strategy(strategy, level):
    if strategy is None:
        return (False, "Chyba při parsování kódu, zkontroluj, že odpovídá popsanému formátu.")
    enemy_strategy = get_enemy_strategy(level)
    res = []
    rounds_per_color = 16 if level == 0 else 1
    for _ in range(rounds_per_color):
        game = Game(PlayerType.AI, PlayerType.AI, strategy, enemy_strategy, True)
        res.append((game.simulate_game(1.1), PlayerColors.White))
    for _ in range(rounds_per_color):
        game =  Game(PlayerType.AI, PlayerType.AI, enemy_strategy, strategy, True)
        res.append((game.simulate_game(1.1), PlayerColors.Black))
    return generate_feedback(res)

def get_enemy_strategy(level):
    strategies = [
        RandomStrategy(),
        BackStepStrategy(),
        MinMax1(),
        MinMax1V2(),
        MinMax2(),
        MinMax2V2(),
        AlphaBeta(),
        AlphaBetaV2()
    ]
    return strategies[level]

def generate_feedback(results):
    for res, color in results:
        my, enemy = res
        if color == PlayerColors.Black:
            my, enemy = enemy, my
        if my == -1:
            return (False, "Pokusil jsi se provést nevalidní tah")
        if my == -2:
            return (False, "Nestihl jsi udělat tah v časovém limitu")
        if my <= enemy:
            return (False, "Alespoň jednu z her jsi nevyhrál")
    return (True, "Vyhrál jsi všechny hry, GRATULUJI")

def post_evaluation_result(result):
    payload = json.dumps(result)
    query = {'key': KEY}
    response = requests.request("POST", POST_URL, data=payload, headers= {'content-type': "application/json"}, params=query)
    if response.status_code != 200:
        print("Invalid post")
        # TODO - something?

def get_points_for_level(level):
    table = [0.5, 0.5, 0.5, 0.5, 1, 1, 1, 1]
    return table[level]

def get_level(module):    
    return module - 520 # Module ids are 520 + level

submissions = get_submissions()
result = []
for act in submissions:
    try:
        if act['evaluator'] is not None:
            continue
        level = get_level(act["module"])
        if level < 0 or level > 7:
            continue
        strategy = get_class_from_code(act['code'])
        act_result = {"evaluation" : act['evaluation'], "evaluator": 2146, "full_report" : "Level " + str(level) + ": ", "ok": 0, "points" : 0.0}
        success, feedback = evaluate_strategy(strategy, level)
        act_result["full_report"] += feedback
        if success:
            act_result["ok"] = 1
            act_result["points"] = get_points_for_level(level)
        result.append(act_result)
    except:
        pass # TODO
post_evaluation_result(result)
sys.exit()
