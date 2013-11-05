from geodata import Model
import pandas as pd


class ConstantModel(Model):

    def __init__(self, prediction):
        self.prediction = prediction

    def save(self, answer):
        pass

    def predict(self, answer):
        return self.prediction

    def __str__(self):
        return "Constant (" + str(self.prediction) + ")"

class  HierarchicalElo(Model):

    def __init__(self, alpha1 = 0.05, alpha2 = 0.1):
        self.alpha1 = alpha1
        self.alpha2 = alpha2
        self.G = {} # global user's skill
        self.D = {} # global difficulty of place
        self.K = {} # user's skil and difficulty of place combined together

    def save(self, answer):
        user = answer['user']
        place = answer['place.asked']
        correct = answer['place.asked'] != answer['place.answered']
        # first attempt
        if answer['question.number.all'] == 0:
            self.K[user, place] = self.G.get(user, 0) - self.D.get(place, 0)
        diff = correct - self.predict(answer)
        # first attempt
        if answer['question.number.all'] == 0:
            self.G[user] = self.G.get(user, 0) + self.alpha1 * diff
            self.D[place] = self.D.get(place, 0) - self.alpha1 * diff
        self.K[user, place] = self.K.get((user, place), 0) + self.alpha2 * diff

    def predict(self, answer):
        user = answer['user']
        place = answer['place.asked']
        type = answer['type']
        return self.sigmoid_shift(
            self.K.get((user,place), 0),
            self.random_factor(type)
        )

    def difficulties(self, places):
        result = []
        for i, place in places.data.iterrows():
            if not self.D.has_key(place['id']):
                continue
            result.append({
                'code': place['code'],
                'ratio': self.D[place['id']]
            })
        return pd.DataFrame(result)

    def __str__(self):
        return "Hierarchical ELO [alpha1=" + str(self.alpha1) + ", alpha2=" + str(self.alpha2) + "]"
