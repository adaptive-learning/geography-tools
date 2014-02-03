# -*- coding: utf-8 -*-
import common


class Elo:

    def __init__(self, alpha=1.0, alpha_scale=0.05, beta=1.0, beta_scale=0.05):
        self.alpha = alpha
        self.beta = beta
        self.alpha_scale = alpha_scale
        self.beta_scale = beta_scale
        self.G = {}
        self.D = {}
        self.user_attempts = {}
        self.place_attempts = {}

    def scale_user(self, n):
        return self.beta / (1 + self.beta_scale * n)

    def scale_place(self, n):
        return self.alpha / (1 + self.alpha_scale * n)

    def model(self, answer, **kvargs):
        skill = self.G.get(answer['user'], 0)
        difficulty = self.D.get(answer['place_asked'], 0)
        pred = common.sigmoid_shift(skill - difficulty, common.random_factor(answer))
        diff = (common.correctness(answer) - pred)
        self.G[answer['user']] = skill + diff * self.scale_user(common.counter(answer['user'], self.user_attempts))
        self.D[answer['place_asked']] = difficulty - diff * self.scale_place(
            common.counter(answer['place_asked'], self.place_attempts))
        return skill - difficulty


def GlobalRatio():

    def __init__(self):
        self.correct = 0.0
        self.total = 0.0

    def model(self, answer, **kwargs):
        prediction = 0.5
        if self.total != 0:
            prediction = self.correct / self.total
        self.correct += common.correctness(answer)
        self.total += 1
        return common.theta(prediction)
