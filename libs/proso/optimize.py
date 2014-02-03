# -*- coding: utf-8 -*-
import scipy.optimize


def minimize(fun, x, *args, **kwargs):
    def fun_wrapper(x):
        x_new = x.tolist()
        x_new.extend(args)
        return fun(*(x_new), **kwargs)
    result = scipy.optimize.minimize(fun_wrapper, x)
    if result['success']:
        return result['x'].tolist()
    else:
        return None
