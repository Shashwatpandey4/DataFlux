import random


def weighted_random_choice(streams):
    choices = []
    for name, props in streams.items():
        choices.extend([name] * int(props["weight"] * 100))
    return random.choice(choices)
