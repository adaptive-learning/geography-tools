# -*- coding: utf-8 -*-
import common
import datetime


class BKT:

    def __init__(self, plearn=0.6, slip=0.02, guess=0.04):
        self.plearn = plearn
        self.slip = slip
        self.default_guess = guess
        self.local = {}

    def guess(self, answer):
        if answer['number_of_options'] == 0:
            return self.default_guess
        else:
            return 1.0 / answer['number_of_options']

    def model(self, answer, prior_skill, **kvargs):
        P = self.local.get(
            (answer['user'], answer['place_asked']),
            common.sigmoid(prior_skill))
        if common.correctness(answer):
            P_u = P * (1 - self.slip) / (P * (1 - self.slip) + (1 - P) * self.guess(answer))
        else:
            P_u = P * self.slip / (P * self.slip + (1 - P) * (1 - self.guess(answer)))
        self.local[answer['user'], answer['place_asked']] = P_u + (1 - P_u) * self.plearn
        if self.local[answer['user'], answer['place_asked']] > 1.0:
            from pprint import pprint
            pprint(answer)
            print P, "---->", P_u + (1 - P_u) * self.plearn
        return P


class Elo:


    def __init__(self, alpha=2.0, time_shift=160.0):
        self.alpha = alpha
        self.time_shift = time_shift
        self.skills = {}
        self.times = {}

    def model(self, answer, prior_skill, **kvargs):
        last_time = self.times.get((answer['user'], answer['place_asked']), common.UNIX_EPOCH)
        skill = self.skills.get((answer['user'], answer['place_asked']), prior_skill)
        skill_shift = skill + self.time_shift / (1 + (answer['inserted'] - last_time).total_seconds())
        pred = common.sigmoid_shift(
            skill_shift,
            common.random_factor(answer))
        self.skills[answer['user'], answer['place_asked']] = skill + (common.correctness(answer) - pred) * self.alpha
        self.times[answer['user'], answer['place_asked']] = answer['inserted']
        return pred


class PFA:

    def __init__(self, good=0.8, bad=0.2, time_shift=60.0):
        self.good = good
        self.bad = bad
        self.time_shift = time_shift
        self.skills = {}
        self.times = {}

    def model(self, answer, prior_skill, **kvargs):
        last_time = self.times.get((answer['user'], answer['place_asked']), common.UNIX_EPOCH)
        skill = self.skills.get((answer['user'], answer['place_asked']), prior_skill)
        skill_shift = skill + self.time_shift / (1 + (answer['inserted'] - last_time).total_seconds())
        if common.correctness(answer):
            self.skills[answer['user'], answer['place_asked']] = skill + self.good
        else:
            self.skills[answer['user'], answer['place_asked']] = skill + self.bad
        self.times[answer['user'], answer['place_asked']] = answer['inserted']
        return common.sigmoid_shift(
            skill_shift,
            common.random_factor(answer))
