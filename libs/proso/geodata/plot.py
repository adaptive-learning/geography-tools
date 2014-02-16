# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import numpy as np
import util
import proso.stats


def response_time_pattern(answers, use_log, normalize_by=None, **kvargs):
    answers = answers.copy(deep=True)
    if use_log:
        answers['response_time'] = np.log(answers['response_time'])
    if normalize_by:
        answers = util.normalize_by(answers, by=normalize_by)
    else:
        answers['response_time'] = proso.stats.normalize(answers['response_time'])
    answers.sort(['user', 'place_asked', 'inserted'])
    last_user = None
    last_place = None
    last_response_time = None
    correct = []
    wrong = []
    for i, row in answers.iterrows():
        if last_user and last_user == row['user'] and last_place == row['place_asked'] and last_response_time:
            if row['place_asked'] == row['place_answered']:
                correct.append(last_response_time)
            else:
                wrong.append(last_response_time)
        if row['place_asked'] != row['place_answered']:
            last_user = None
            last_place = None
            last_response_time = None
        else:
            last_user = row['user']
            last_place = row['place_asked']
            last_response_time = row['response_time']
    plt.hist([correct, wrong], **kvargs)


def response_time(answers, use_log, **kvargs):
    times = answers['response_time']
    if use_log:
        times = np.log(times)
    times = np.array(proso.stats.normalize(times))
    wrong = times[answers['place_asked'] != answers['place_answered']]
    correct = times[answers['place_asked'] == answers['place_answered']]
    plt.hist([correct, wrong], **kvargs)


def confusing_factor_by_distance(cf, distance_matrix, places=None, **kvargs):
    def sort_key_gen(place):
        return lambda (p, v): (distance_matrix[place][p], -v)

    confusing_factor(cf, places, sort_key_gen, **kvargs)


def confusing_factor(confusing_factor, places=None, sort_key_gen=None, **kvargs):
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
        plt.plot(range(len(normalized[place])), normalized[place], **kvargs)


def answers_per_user(answers, **kvargs):
    per_user = {}
    for i, row in answers.iterrows():
        per_user[row['user']] = per_user.get(row['user'], 0) + 1
    plt.hist(per_user.values(), **kvargs)


def total_success(answers, history_length, **kvargs):
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
    plt.plot(x, y, **kvargs)


def total_answers(answers, **kvargs):
    x = []
    y = []
    count = 1
    for i, row in answers.iterrows():
        x.append(row['inserted'])
        y.append(count)
        count += 1
    plt.plot(x, y, **kvargs)
