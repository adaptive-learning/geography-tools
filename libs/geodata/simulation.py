import math
import numpy as np
from pprint import pprint
import pandas as pd


class Simulator:

    def __init__(self, answers, sorted = False):
        if not sorted:
            self.answers = answers.sort(['inserted'])
        else:
            self.answers = answers

    def __getitem__(self, key):
        if np.isscalar(key):
            return self.answers[key]
        else:
            return Simulator(self.answers[key], True)

    def step_by_step(self, model):
        return StepByStepSimulation(model, self.answers)

    def simulate(self, model, status = False, n = None):
        predicted = []
        answered = []
        data = self.answers.data
        progress_before = None
        index = 0
        if n == None or n > len(data):
            n = len(data)
        for i, row in data.iterrows():
            predicted.append(model.predict(row.to_dict()))
            answered.append(row['place.asked'] == row['place.answered'])
            model.save(row.to_dict())

            if status:
                progress = int(round(100 * float(index) / n))
                if progress_before == None or progress_before != progress:
                    progress_before = progress
                    print "[" + progress * "*" + (100 - progress) * "-" + "]", index, "/", n
            index += 1
            if index >= n:
                break
        return SimulationResult(model, predicted, answered)


class StepByStepSimulation:

    def __init__(self, model, answers):
        self._step = 0
        self.answers = answers
        self.answers = self.answers.sort(["inserted"])
        self.answers.data.index = range(len(self.answers))
        self.model = model
        self.predicted = []
        self.answered = []
        self.last_answer = None

    def step(self):
        if self._step >= len(self.answers):
            return None
        row = self.answers.data.xs(self._step)
        self.predicted.append(self.model.predict(row.to_dict()))
        self.answered.append(row['place.asked'] == row['place.answered'])
        self.model.save(row.to_dict())
        self._step += 1
        self.last_answer = row
        return self

    def rmse(self):
        return math.sqrt(
            sum((self.predicted - self.answered) ** 2)
            /
            float(len(self.predicted))
        )


class Model:

    def save(self, answer):
        raise Exception("The save(answer) method is not defined")

    def predict(self, answer):
        raise Exception("The predict(answer) method is not defined")

    def difficulties(self, places):
        raise Exception("The difficulties(places) method is not defined")

    def predictions(self, places, user):
        result = []
        for i, place in places.data.iterrows():
            question = {
                'user': user,
                'place.asked': place['id'],
                'type': 10}
            result.append({
                'code': place['code'],
                'ratio': self.predict(question)})
        return pd.DataFrame(result)

    def sigmoid(self, x):
        return 1 / (1 + math.exp(-x))

    def sigmoid_shift(self, x, c):
        return c + (1-c) * self.sigmoid(x)

    def random_factor(self, question_type):
        if question_type == 10:
            return 0
        return 1.0 / (question_type - 10*(question_type//10))

class SimulationResult:

    def __init__(self, model, predicted, answered):
        self.model = model
        self.predicted = np.array(predicted)
        self.answered = np.array(answered)

    def rmse(self):
        return math.sqrt(
            sum((self.predicted - self.answered) ** 2)
            /
            float(len(self.predicted))
        )

    def __str__(self):
        return str(self.model) + ", RMSE: " + str(self.rmse())

