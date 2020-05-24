#!/usr/bin/python3.7

def anal_one():
    input()
    input()
    name = input()
    input()
    wins = 0
    draws = 0
    loses = 0
    my_score = 0
    enemy_score = 0
    for _ in range(100):
        act = input()
        act = act.replace("(", "")
        act = act.replace(")", "")
        my, enemy = tuple([int(x) for x in act.split(",")])
        my_score += my
        enemy_score += enemy
        if my > enemy:
            wins += 1
        elif my == enemy:
            draws += 1
        else:
            loses += 1
    print(name + "\n----------------------------\n" + "wins: " + str(wins) + "\ndraws: " + str(draws) + "\nloses: " + str(loses) + "\nscore: " + str(my_score) + "\nenemy score: " + str(enemy_score) + "\n-------------------------------\n\n")             

for _ in range(64):
    anal_one()