# -*- coding: utf-8 -*-

def same_lengths(*args):
    last_length = -1
    for arg in args:
        if last_length != -1 and last_length != len(arg):
            raise Exception('arguments differ in length')
        last_length = len(arg)
