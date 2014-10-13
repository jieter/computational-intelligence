import numpy as np
import os
import time

import pickle

from maze import Maze
from aco import ACO


class TSPMaze(object):
    '''
    assumes
    3 files in ../data/:
     - hard-maze.txt
     - medium-maze.txt
     - tst-products.txt
    '''

    EMPTY = -1
    FAILED = -2

    cachefile = 'tsp-results.pickle'

    def __init__(self, filename='../data/hard-maze.txt'):
        self.maze = Maze.from_file(filename)

        self.load_products()

        # initialize array for the distances.
        if os.path.exists(self.cachefile):
            print 'Loading from cachefile: %s' % self.cachefile
            self.load_cache()
        else:
            self.results = np.full((self.num + 1, self.num + 1), TSPMaze.EMPTY)

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

    def calculate_paths(self):
        maze = self.maze

        total_paths = 0.5 * (self.num - 1) * self.num
        print 'Calculate paths between %d products (%d paths total) in maze %s.' % (
            self.num, total_paths, maze.name
        )

        for A, locationA in self.products.items():
            for B, locationB in self.products.items():
                print 'Route %d -> %d' % (A, B),

                if A is B:
                    self.results[A, B] = 0
                    print 'is zero'
                    continue

                # no reason to do double work
                if self.results[B, A] not in (TSPMaze.EMPTY, TSPMaze.FAILED):
                    print 'already done'
                    continue

                aco = ACO(maze, visualize=False)
                maze.set_start(locationA)
                maze.set_end(locationB)

                start_time = time.time()

                ant = aco.run(quiet=True)
                if ant is None:
                    self.results[A, B] = TSPMaze.FAILED
                    print 'not found, run again to try again.' % (A, B)
                else:
                    self.results[A, B] = len(ant.trail)
                    self.results[B, A] = len(ant.trail)
                    print 'done (length: %d) in %0.2fs' % (len(ant.trail), time.time() - start_time)

                self.dump_cache()

    def load_cache(self):
        with open(self.cachefile) as f:
            self.results = pickle.load(f)

    def dump_cache(self):
        with open(self.cachefile, 'w') as f:
            pickle.dump(self.results, f)

    def result_matrix(self):
        '''
        Display the result matrix in ascii from
        '''

        FORMAT = '%4d'
        print '  ',
        for A, locationA in self.products.items():
            print FORMAT % A,
        print

        for A, locationA in self.products.items():
            print '%2d' % A,
            for B, locationB in self.products.items():
                val = self.results[A, B]
                if val == TSPMaze.FAILED:
                    print ' fail',
                elif val == TSPMaze.EMPTY:
                    print '   .',
                else:
                    print FORMAT % self.results[A, B],
            print

if __name__ == '__main__':
    print 'Loading TSPMaze...'

    tspmaze = TSPMaze()

    tspmaze.calculate_paths()
