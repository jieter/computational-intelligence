#!/usr/bin/env python

import sys
import pickle

if len(sys.argv) < 2:
    sys.exit()

a = pickle.load(open(sys.argv[1]))
b = pickle.load(open(sys.argv[2]))

def diff(this, that):
    if len(this) is not len(that):
        return 'Dimensions do not agree'

    FORMAT = '%5d '

    ret = '   '
    for a, A in enumerate(this):
        ret += (FORMAT % a)
    ret += '\n'

    for a, A in enumerate(this):
        ret += '%2d ' % a
        for b, B in enumerate(A):
            thisval = int(this[a][b]['length'])
            thatval = int(that[a][b]['length'])
            ret += (FORMAT % (thisval - thatval))
        ret += '\n'

    return ret

def merge(this, that):
    if len(this) is not len(that):
        return 'Dimensions do not agree'

    ret = map(list, [[{}] * len(this)] * len(this))

    for a, A in enumerate(this):
        for b, B in enumerate(A):
            thisval = int(this[a][b]['length'])
            thatval = int(that[a][b]['length'])

            if thisval < thatval:
                ret[a][b] = this[a][b]
            else:
                ret[a][b] = that[a][b]


    return ret

print 'diff between %s and %s' % (sys.argv[1], sys.argv[2])
print 'Negative numbers mean second is better'
print diff(a, b)

if len(sys.argv[3]) == 3:
    print
    print 'Writing best values from these files to', sys.argv[3]
    pickle.dump(merge(a, b), open(sys.argv[3], 'w'))
