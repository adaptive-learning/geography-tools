import sys
from pprint import pprint

sys.path.append('../libs')
sys.path.append('../target/external-libs/')

import geodata
import scipy.optimize as optimize

answers = geodata.Answers.from_csv('../target/data/answers.csv')
experiment = geodata.Experiment(answers)
print experiment.cross_validation(
    model_class = geodata.HierarchicalEloWithForgetting,
    n_params    = 3,
    K           = 5,
    output      = True)
