
GREEN = '\033[92m'
RED = '\033[31m'
CYAN = '\033[36m'
ENDC = '\033[0m'


def mean(l):
    if len(l) == 0:
        return -1
    return round(sum(l) / float(len(l)), 1)
