# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import sys


def confusing_factor_by_distance(cf, distance_matrix, places=None, **kwargs):
    def sort_key_gen(place):
        return lambda (p, v): (distance_matrix[place][p], -v)

    confusing_factor(cf, places, sort_key_gen, **kwargs)


def confusing_factor(confusing_factor, places=None, sort_key_gen=None, **kwargs):
    if not places:
        places = confusing_factor.keys()
    normalized = {}
    for place in places:
        if not sort_key_gen:
            sort_key = lambda (p, v): -v
        else:
            sort_key = sort_key_gen(place)
        total = float(sum(confusing_factor[place].values()))
        normalized[place] = map(
            lambda x: x[1] / total,
            sorted(confusing_factor[place].iteritems(), key=sort_key))
    for place in places:
        plt.plot(range(len(normalized[place])), normalized[place], **kwargs)


def answers_per_user(answers, **kwargs):
    per_user = {}
    for i, row in answers.iterrows():
        per_user[row['user']] = per_user.get(row['user'], 0) + 1
    plt.hist(per_user.values(), **kwargs)


def total_success(answers, history_length, **kwargs):
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
    plt.plot(x, y, **kwargs)


def total_answers(answers, **kwargs):
    x = []
    y = []
    count = 1
    for i, row in answers.iterrows():
        x.append(row['inserted'])
        y.append(count)
        count += 1
    plt.plot(x, y, **kwargs)
