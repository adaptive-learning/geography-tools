# -*- coding: utf-8 -*-
import sys
import os.path
DIRNAME = os.path.abspath(os.path.dirname(__file__))
LIBS = DIRNAME + "/../libs"
TARGET = DIRNAME + "/../target"
sys.path.append(LIBS)

import proso.geodata

MODEL_PRIOR = proso.geodata.models_prior.Elo().model

MODELS_CURRENT = [
    proso.geodata.models_current.BKT,
    proso.geodata.models_current.Elo,
    proso.geodata.models_current.PFA,
    proso.geodata.models_current.PFAElo
]

METRICS = [
    proso.metrics.rmse,
    proso.metrics.mae,
    proso.metrics.auc,
]

answers = proso.geodata.load_csv(TARGET + "/data/geography.answer.csv");

prior_knowledge = proso.geodata.models.get_prior_knowledge(MODEL_PRIOR, answers)

print "\t",
for metric in METRICS:
    print metric.func_name, "\t",
    if len(metric.func_name) < 7:
        print "\t",
print
print 80 * '-'

for model in MODELS_CURRENT:
    model_instance = model()
    print model_instance.__class__.__name__, "\t",
    expected, predicted = proso.geodata.models.simulate_with_prior_knowledge(
        prior_knowledge,
        model_instance.model,
        answers,
        track=proso.geodata.models.MODEL_CURRENT)
    for metric in METRICS:
        error = round(metric(expected, predicted) * 1000) / 1000.0
        print error, "\t",
        if len(str(error)) < 7:
            print "\t",
    print
