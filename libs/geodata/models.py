from geodata import Model
import pandas as pd
import numpy as np
import time
import math


class ConstantModel(Model):

    def __init__(self, prediction):
        self.prediction = prediction

    def save(self, answer):
        pass

    def predict(self, answer):
        return self.prediction

    def __str__(self):
        return "Constant (" + str(self.prediction) + ")"

class GlobalMeanModel(Model):

    def __init__(self):
        self.answered = []

    def save(self, answer):
        self.answered.append(answer['place.asked'] == answer['place.answered'])

    def predict(self, answer):
        return np.mean(self.answered) if len(self.answered) > 0 else 0.5

    def __str__(self):
        return "Global Average"

class UserMeanModel(Model):

    def __init__(self):
        self.answered = {}

    def save(self, answer):
        if not self.answered.has_key(answer['user']):
            self.answered[answer['user']] = []
        self.answered[answer['user']].append(
            answer['place.asked'] == answer['place.answered'])

    def predict(self, answer):
        answered = self.answered.pop(answer['user'], [])
        return np.mean(answered) if len(answered) > 0 else 1

    def __str__(self):
        return "User's Mean"


class  HierarchicalElo(Model):

    def __init__(self, alpha1 = 0.4, alpha2 = 1.6, alpha3 = 0):
        self.alpha1 = alpha1
        self.alpha2 = alpha2
        self.alpha3 = alpha3
        self.G = {} # global user's skill
        self.D = {} # global difficulty of place
        self.K = {} # user's skil and difficulty of place combined together

    def save(self, answer):
        user = answer['user']
        place = answer['place.asked']
        correct = answer['place.asked'] == answer['place.answered']
        # first attempt
        if answer['question.number.all'] == 0:
            self.K[user, place] = self.G.get(user, 0) - self.D.get(place, 0)
        diff = correct - self.predict(answer)
        # first attempt
        if answer['question.number.all'] == 0:
            self.G[user] = self.G.get(user, 0) + self.alpha1 * diff
            self.D[place] = self.D.get(place, 0) - self.alpha1 * diff
        self.K[user, place] = self.K.get((user, place), 0) + self.alpha2 * diff
        if not correct:
            place_conf = answer['place.answered']
            diff_conf = - self.sigmoid_shift(
                self.K.get((user, place_conf), 0),
                self.random_factor(answer['type'])
            )
            self.K[user, place_conf] = self.K.get((user, place_conf), 0) + self.alpha3 * diff_conf

    def predict(self, answer):
        user = answer['user']
        place = answer['place.asked']
        type = answer['type']
        return self.sigmoid_shift(
            self.K.get((user,place), self.G.get(user, 0) - self.D.get(place, 0)),
            self.random_factor(type)
        )

    def difficulties(self, places):
        result = []
        for i, place in places.data.iterrows():
            if not self.D.has_key(place['id']):
                continue
            result.append({
                'code': place['code'],
                'ratio': - self.D[place['id']]
            })
        return pd.DataFrame(result)

    def __str__(self):
        return "Hierarchical ELO [alpha1=" + str(self.alpha1) + ", alpha2=" + str(self.alpha2) + ", alpha3=" + str(self.alpha3) + "]"


class HierarchicalEloWithForgetting(HierarchicalElo):

    def __init__(self, alpha1 = 0.4, alpha2 = 1.6, beta = 0.15, alpha3 = 0):
        HierarchicalElo.__init__(self, alpha1, alpha2, alpha3)
        self.beta = beta
        self.last_time = {}

    def save(self, answer):
        HierarchicalElo.save(self, answer)
        self.last_time[answer['user'], answer['place.asked']] = self.to_time(answer)

    def predict(self, answer):
        user = answer['user']
        place = answer['place.asked']
        type = answer['type']
        time_diff = (self.to_time(answer) - self.last_time.get((user, place), self.to_time(answer))) / 3600.0
        K = self.K.get((user,place), self.G.get(user, 0) - self.D.get(place, 0))
        K = K - self.beta * (math.log(time_diff) if time_diff > 0 else 0)
        return self.sigmoid_shift(
            K,
            self.random_factor(type)
        )

    def to_time(self, answer):
        inserted = time.strptime(answer['inserted'], "%Y-%m-%d %H:%M:%S")
        return time.mktime(inserted)

    def __str__(self):
        return "Hierarchical ELO with forgetting [alpha1=" + str(self.alpha1) + ", alpha2=" + str(self.alpha2) + ", alpha3=" + str(self.alpha3) + ", beta=" + str(self.beta)  +  "]"
