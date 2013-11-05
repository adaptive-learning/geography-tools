import math
import numpy as np

class Simulator:

    def __init__(self, answers):
        self.answers = answers
        self.predicted = []
        self.answered = []

    def simulate(self, model, status = False, n = None):
        data = self.answers.sort(["inserted"]).data
        progress_before = None
        index = 0
        if n == None or n > len(data):
            n = len(data)
        for i, row in data.iterrows():
            self.predicted.append(model.predict(row.to_dict()))
            self.answered.append(row['place.asked'] == row['place.answered'])
            model.save(row.to_dict())

            if status:
                progress = int(round(100 * float(index) / n))
                if progress_before == None or progress_before != progress:
                    progress_before = progress
                    print "[" + progress * "*" + (100 - progress) * "-" + "]", index, "/", n
            index += 1
            if index >= n:
                break
        return SimulationResult(model, self.predicted, self.answered)


class Model:

    def save(self, answer):
        raise Exception("The save(answer) method is not defined")

    def predict(self, answer):
        raise Exception("The predict(answer) method is not defined")

    def difficulties(self, places):
        raise Exception("The difficulties(places) method is not defined")

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

