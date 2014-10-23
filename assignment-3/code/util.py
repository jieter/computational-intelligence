
def mean(l):
    if len(l) == 0:
        return -1
    return round(sum(l) / float(len(l)), 1)
