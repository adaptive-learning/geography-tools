# -*- coding: utf-8 -*-
import math
import common
import proso.optimize


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


def get_prior_knowledge(model_prior, answers, **kvargs):
    prior_knowledge = {}
    for i, answer in answers.iterrows():
        prior_k = prior_knowledge.get((answer['user'], answer['place_asked']), -1)
        if prior_k == -1:
            prior_k = model_prior(answer, **kvargs)
            prior_knowledge[answer['user'], answer['place_asked']] = prior_k
    return prior_knowledge


def simulate_with_prior_knowledge(prior_knowledge, model_current, answers, **kvargs):
    expected = []
    predictions = []
    for i, answer in answers.iterrows():
        prior_k = prior_knowledge[answer['user'], answer['place_asked']]
        predictions.append(model_current(answer, prior_k, **kvargs))
        expected.append(common.correctness(answer))
    return expected, predictions


def simulate(model_prior, model_current, answers, **kvargs):
    prior_knowledge = get_prior_knowledge(model_prior, answers, **kvargs)
    return simulate_with_prior_knowledge(prior_knowledge, model_current, answers, **kvargs)


def optimize_current(model_prior, model_current_constructor, metric, answers, *init_params, **kvargs):
    prior_knowledge = get_prior_knowledge(model_prior, answers, **kvargs)

    def optimize_current_fun(*x):
        expected, predicted = simulate_with_prior_knowledge(
            prior_knowledge,
            model_current_constructor(*x),
            answers,
            **kvargs)
        return metric(expected, predicted)
    return proso.optimize.minimize(optimize_current_fun, init_params, **kvargs)
