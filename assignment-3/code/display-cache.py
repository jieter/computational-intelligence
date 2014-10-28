#!/usr/bin/env python

from tspmaze import TSPMaze
from util import RED, GREEN, ENDC
tspmaze = TSPMaze()

import sys

if len(sys.argv) == 2:
    maze = tspmaze.maze

    if sys.argv[1] == 'check':
        print tspmaze.valid_matrix(forget=False)
    elif sys.argv[1] == 'forget-invalid':
        print tspmaze.valid_matrix(forget=True)
        print
        print 'after forgetting:'
        print tspmaze.valid_matrix(forget=False)



elif len(sys.argv) == 3:
    a = int(sys.argv[1])
    b = int(sys.argv[2])

    print 'Route van locatie %d naar %d' % (a, b)
    print tspmaze.visualize_route(a, b)
else:
    print tspmaze.result_matrix()
    while True:
        try:
            a = int(raw_input('Startlocatie?'))
            b = int(raw_input('Eindlocatie?'))
            print tspmaze.visualize_route(a, b)

        except ValueError:
            pass


