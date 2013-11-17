import random
import scipy.optimize as optimize
import numpy as np
from geodata import Simulator


class Experiment:

    def __init__(self, answers):
        self.answers = answers

    def split_users(self, n):
        users = self.answers['user'].unique()
        if len(users) < n:
            raise Exception("Can't split " + len(users) + " to " + n + " groups.")
        random.shuffle(users)
        group_size = len(users) / float(n)
        return [ users[int(i*group_size): int((i+1)*group_size)] for i in range(n)]

    def cross_validation(self, model_class, n_params, K, output = False):
        params, rmse, mae, auc = [], [], [], []
        for user_group in self.split_users(K):
            training_set = self.answers[
                np.logical_not(self.answers['user'].isin(user_group))]
            test_set = self.answers[self.answers['user'].isin(user_group)]
            simulator = Simulator(training_set)
            minimized = optimize.minimize(
                lambda params: self._objective_function(simulator, model_class, params),
                [0] * n_params
            )
            simulated = Simulator(test_set).simulate(model_class(*minimized.x))
            params.append(minimized.x)
            rmse.append(simulated.rmse())
            mae.append(simulated.mae())
            auc.append(simulated.auc())
            if output:
                print "Model", model_class
                print "\t - found parameters: ", minimized.x
                print "\t - RMSE:", simulated.rmse()
                print "\t - MAE: ", simulated.mae()
                print "\t - AUC: ", simulated.auc()
        return ExperimentResult(model_class, params, rmse, mae, auc)

    def _objective_function(self, simulator, model_class, params):
        if any(map(lambda x: x < 0, params)):
            return sum(map(abs, filter(lambda x: x < 0, params))) * 10000000
        model = model_class(*params)
        return simulator.simulate(model).rmse()


class ExperimentResult:

    def __init__(self, model_class, params, rmse, mae, auc):
        self._model_class = model_class
        self._params = params
        self._rmse = rmse
        self._mae = mae
        self._auc = auc

    def rmse(self):
        return np.mean(self._rmse)

    def mae(self):
        return np.mean(self._mae)

    def auc(self):
        return np.mean(self._auc)

    def params(self):
        i = self._rmse.index(min(self._rmse))
        return self._params[i]

    def __str__(self):
        return ("Experiment results for model " + str(self._model_class) + "\n"
                "\t - found parameters: " + str(self.params()) + "\n" +
                "\t - RMSE: " + str(self.rmse()) + "\n" +
                "\t - MAE:  " + str(self.mae()) + "\n" +
                "\t - AUC:  " + str(self.auc()) + "\n")
