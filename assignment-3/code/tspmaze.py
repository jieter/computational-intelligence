#!/usr/bin/env python

import numpy as np
import os
import time

import pickle

from aco import ACO
from maze import Maze
from util import mean


class TSPMaze(object):
    '''
    assumes
    3 files in ../data/:
     - hard-maze.txt
     - medium-maze.txt
     - tst-products.txt
    '''

    EMPTY = {}
    FAILED = {
        'failed': True
    }

    cachefile = 'tsp-results.pickle'

    def __init__(self, filename='../data/hard-maze.txt'):
        self.maze = Maze.from_file(filename)
        self.cachefile = filename + '.tsp-results.pickle'

        self.load_products()

        # initialize array for the distances.
        if os.path.exists(self.cachefile):
            print 'Loading from cachefile: %s' % self.cachefile
            self.load_cache()
        else:
            size = self.num + 1
            self.results = map(list, [[TSPMaze.EMPTY] * size] * size)

            print self.results

        np.set_printoptions(suppress=True)

    def load_products(self, filename='../data/tsp-products.txt'):
        with open(filename) as products:
            self.num = int(products.readline()[0:-2])

            # save all products to a dictionary
            self.products = {
                int(product): tuple(map(int, location.split(',')))
                for product, location in
                [row[0:-2].split(':') for row in products]
            }
            self.maze.products = self.products.values()

    def calculate_paths(self, refine=False):
        maze = self.maze

        total_paths = 0.5 * (self.num - 1) * self.num
        print 'Calculate paths between %d products (%d paths total) in maze %s.' % (
            self.num, total_paths, maze.name
        )
        overall_start_time = time.time()
        elapsed_list = []

        for A in range(self.num + 1):
            self.set_result(A, A, None)

        self.dump_cache()

        for A, locationA in self.products.items():
            for B, locationB in self.products.items():
                if A is B:
                    continue
                if not refine and self.results[B][A] not in (TSPMaze.EMPTY, TSPMaze.FAILED):
                    continue

                print 'Route %d -> %d' % (A, B),

                maze.set_start(locationA)
                maze.set_end(locationB)

                start_time = time.time()

                aco = ACO(maze, visualize=False, iterations=10)
                ant = aco.run(quiet=True)

                elapsed = time.time() - start_time

                if ant is None:
                    self.set_result(A, B, TSPMaze.FAILED, elapsed=elapsed)
                    print 'not found in %0.2fs, run again to try again. ' % elapsed
                else:
                    self.set_result(A, B, ant)

                    print 'done (length: %d) in %0.2fs' % (len(ant.trail), elapsed)
                    elapsed_list.append(elapsed)

                print 'running %0.2fs now, average time: %0.2fs' % (
                    time.time() - overall_start_time,
                    mean(elapsed_list)
                )
                self.dump_cache()

    def set_result(self, A, B, ant=None, elapsed=None):
        known_length = None
        if self.results[A][B] not in (self.EMPTY, self.FAILED):
            known_length = self.results[A][B]['length']

            if ant is None:
                return


        res = {
            'length': 0,
            'trail': []
        }

        if ant is TSPMaze.FAILED:
            res = ant
        elif ant is not None:
            if known_length is not None:
                # compare solution with known, store if better
                if known_length < len(ant.trail):
                    print 'Solution with length %d known, not updating.' % known_length
                    return
                else:
                    print 'Updating solution (%d < %d)' % (len(ant.trail), known_length)

            res['length'] = len(ant.trail)
            res['trail'] = list(ant.trail)
            if elapsed is not None:
                res['elapsed'] = elapsed

        self.results[A][B] = self.results[B][A] = res

    def load_cache(self):
        with open(self.cachefile) as f:
            self.results = pickle.load(f)

    def dump_cache(self):
        with open(self.cachefile, 'w') as f:
            pickle.dump(self.results, f)
        with open(self.cachefile + '.txt', 'w') as f:
            f.write(self.result_matrix())

    def done(self):
        for x in range(1, self.num + 1):
            for y in range(1, self.num + 1):
                if self.results[x][y] in (self.EMPTY, self.FAILED):
                    return False

        return True

    def result_matrix(self):
        '''
        Display the result matrix in ascii from
        '''

        FORMAT = '%4d '

        ret = '   '
        for A, locationA in self.products.items():
            ret += (FORMAT % A)
        ret += '\n'

        for A, locationA in self.products.items():
            ret += '%2d ' % A
            for B, locationB in self.products.items():
                val = self.results[A][B]
                if val == TSPMaze.FAILED:
                    ret += 'fail '
                elif val == TSPMaze.EMPTY:
                    ret += '   . '
                else:
                    ret += (FORMAT % self.results[A][B]['length'])
            ret += '\n'

        return ret

if __name__ == '__main__':
    print 'Loading TSPMaze...'

    tspmaze = TSPMaze()

    print tspmaze.result_matrix()
    print

    if tspmaze.done():
        print 'All possible paths calculated, running over it again to refine values.'
        tspmaze.calculate_paths(refine=True)
    else:
        tspmaze.calculate_paths()
        tspmaze.result_matrix()

        while not tspmaze.done():
            tspmaze.calculate_paths()
