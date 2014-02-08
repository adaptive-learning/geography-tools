# -*- coding: utf-8 -*-
from sklearn.metrics import roc_curve, auc as sk_auc
import math
import util.ensure
import scipy as sp
import numpy as np


def rmse(expected, found):
    util.ensure.same_lengths(expected, found)
    return math.sqrt(np.mean((np.array(expected) - np.array(found)) ** 2))

def rmse_bw(expected, found):
    util.ensure.same_lengths(expected, found)
    ones = sum(expected) / float(len(expected))
    zeros = 1 - ones
    return math.sqrt(np.mean(np.array(map(
        lambda x: zeros * x if x > 0 else ones * x,
        np.array(expected) - np.array(found))) ** 2))


def logloss(expected, found):
    util.ensure.same_lengths(expected, found)
    epsilon = 1e-15
    found = sp.minimum(1 - epsilon, sp.maximum(epsilon, found))
    ll = sum(expected * sp.log(found) + sp.subtract(1, expected * sp.log(sp.subtract(1, found))))
    return ll * -1.0 / len(expected)


def mae(expected, found):
    util.ensure.same_lengths(expected, found)
    return np.mean(np.absolute(np.array(expected) - np.array(found)))


def auc(expected, found):
    fpr, tpr, thresholds = roc_curve(expected, found)
    return sk_auc(fpr, tpr)
