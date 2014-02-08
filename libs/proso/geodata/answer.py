# -*- coding: utf-8 -*-
import pandas as pd


def time_diff(answers):
    answers = answers.sort(['user', 'place_asked', 'id'], ascending=True)
    last_user = None
    last_place = None
    last_time = None
    times = []
    for i, row in answers.iterrows():
        if row['user'] != last_user:
            last_user = row['user']
            last_place = None
        if row['place_asked'] != last_place:
            last_place = row['place_asked']
            last_time = None
        if last_time:
            times.append((row['inserted'] - last_time).total_seconds())
        else:
            times.append(None)
        last_time = row['inserted']
    answers['since_last'] = pd.Series(times, index=answers.index)
    return answers


