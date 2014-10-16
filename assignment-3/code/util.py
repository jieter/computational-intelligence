
def mean(l):
    if len(l) == 0:
        return None
    return round(sum(l) / float(len(l)), 1)
