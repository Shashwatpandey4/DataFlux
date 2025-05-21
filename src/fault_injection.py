import random


def maybe_fail(prob=0.05):
    return random.random() < prob
