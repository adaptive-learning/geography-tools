# -*- coding: utf-8 -*-
import math


def confusing_factor(answers):
    cf = {}
    for i, row in answers.iterrows():
        asked = int(row['place_asked'])
        answered = row['place_answered']
        if math.isnan(answered):
            continue
        answered = int(answered)
        if asked != answered:
            f_asked = cf.get(asked, {})
            f_asked[answered] = 1 + f_asked.get(answered, 0)
            cf[asked] = f_asked
            f_answered = cf.get(answered, {})
            f_answered[asked] = 1 + f_answered.get(asked, 0)
            cf[answered] = f_answered
    return cf
