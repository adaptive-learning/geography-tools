# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt


def answers_per_user(answers, **args):
    per_user = {}
    for i, row in answers.iterrows():
        per_user[row['user']] = per_user.get(row['user'], 0) + 1
    plt.hist(per_user.values(), **args)


def total_success(answers, history_length, **args):
    x = []
    y = []
    corrects = []
    total_sum = 0
    count = 0
    for i, row in answers.iterrows():
        c = row['place_asked'] == row['place_answered']
        total_sum += c
        corrects.append(c)
        if len(corrects) > history_length:
            total_sum -= corrects[0]
            corrects = corrects[1:]
        count += 1
        x.append(row['inserted'])
        y.append(float(total_sum) / min(history_length, count))
    plt.plot(x, y, **args)


def total_answers(answers, **args):
    x = []
    y = []
    count = 1
    for i, row in answers.iterrows():
        x.append(row['inserted'])
        y.append(count)
        count += 1
    plt.plot(x, y, **args)
