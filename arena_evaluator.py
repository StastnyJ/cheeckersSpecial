#!/usr/bin/python3.7

import requests
import json
from enum import Enum
from game import *
from example_solution import *
import sys
import os

GET_URL = 'https://ksi-api.borysek.eu/getEvaluations'
POST_URL = 'https://ksi-api.borysek.eu/updateEvaluations'
POST_RESULT_URL = 'https://ksi-api.borysek.eu/saveArenaResults'
GET_RESULTS_URL = 'https://ksi-api.borysek.eu/getArenaResults'
KEY = 'f7efa29687adc65aa292afea265dc4e1'
ARENA_MODULE = 532

class PlayerColors(Enum):
    White = 0
    Black = 1

class Result(Enum):
    Win = 0
    Lose = 1
    Draw = 2
    ParseError = 3
    Timeout = 4
    WrongMove = 5
    BothParseError = 6
    EnemyTimeout = 7
    EnemyWrongMove = 8
    EnemyParseError = 9


def load_cash_results():
    query = {
        "key": KEY
    }
    response = requests.request("GET", GET_RESULTS_URL, data="", params=query)
    if response.status_code != 200:
        print("Invalid response")
    return json.loads(response.text)

def save_results(results):
    payload = json.dumps(results)
    query = {'key': KEY}
    response = requests.request("POST", POST_RESULT_URL, data=payload, headers= {'content-type': "application/json"}, params=query)
    if response.status_code != 200:
        print("Invalid post")

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

def get_all_arena_submissions(submissions):
    res = []
    for sub in submissions:
        if sub["org"] == 1:
            continue
        if sub["module"] == ARENA_MODULE:
            res.append(sub)
    return res

def get_new_submissions(submissions):
    res = []
    for sub in submissions:
        if sub["evaluator"] is None:
            res.append(sub)
    return res

def get_old_submissions(submissions):
    res = []
    for sub in submissions:
        if sub["evaluator"] is not None:
            res.append(sub)
    return res

def get_class_from_code(code):
    try:
        exec(code, None, globals())
        return FinalSolution()
    except:
        return None

def fight(my, enemy):
    if my is None and enemy is None:
        return Result.BothParseError
    if my is None:
        return Result.ParseError
    if enemy is None:
        return Result.EnemyParseError
    game =  Game(PlayerType.AI, PlayerType.AI, my, enemy, True)
    res = game.simulate_game(1.1)
    return generate_fight_feedback(res)

def generate_fight_feedback(res):
    if res[0] == -1:
        return Result.WrongMove
    if res[0] == -2:
        return Result.Timeout
    if res[1] == -1:
        return Result.EnemyWrongMove
    if res[1] == -2:
        return Result.EnemyTimeout
    if res[0] > res[1]:
        return Result.Win
    if res[0] == res[1]:
        return Result.Draw
    return Result.Lose

def post_evaluation_result(result):
    payload = json.dumps(result)
    query = {'key': KEY}
    response = requests.request("POST", POST_URL, data=payload, headers= {'content-type': "application/json"}, params=query)
    if response.status_code != 200:
        print("Invalid post")
        # TODO - something?

def evaluate_pair(act, enemy):
    global arena_results

    strategy = get_class_from_code(act['code'])
    enemy_strategy = get_class_from_code(enemy['code'])
    enemy_id = str(enemy["user"])
    act_id = str(act["user"])
    result = fight(strategy, enemy_strategy)
    if act_id not in arena_results:
        arena_results[act_id] = {}
    arena_results[act_id][enemy_id] = str(result).replace("Result.", "")

def post_submissions(submissions):
    res = []
    for act in submissions:
        res.append({"evaluation" : act['evaluation'], "evaluator": 2146, "full_report" : "", "ok": 0, "points" : 0.0})
    post_evaluation_result(res)



submissions = get_submissions()
submissions = get_all_arena_submissions(submissions)
new_submissions = get_new_submissions(submissions)
old_submissions = get_old_submissions(submissions)
arena_results = load_cash_results()


# # uncomment for test all subs

new_submissions = submissions
old_submissions = {}
arena_results = {}


for act in new_submissions:
    try:
        for enemy in submissions:
            if act['evaluation'] == enemy['evaluation']:
                continue
            try:
               evaluate_pair(act, enemy)
            except:
                pass    
    except:
        pass

for act in old_submissions:
    try:
        for enemy in new_submissions:
            try:
                evaluate_pair(act, enemy)
            except:
                pass        
    except:
        pass

save_results(arena_results)
post_submissions(new_submissions)

sys.exit()
