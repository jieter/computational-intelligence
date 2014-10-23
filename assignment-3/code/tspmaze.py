#!/usr/bin/env python

import os
import time
import random
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

    base_aco_settings = dict(
        visualize=False,
        quiet=True,
    )

    cachefile = 'tsp-results.pickle'

    def __init__(self, filename='../data/hard-maze.txt'):
        self.maze = Maze.from_file(filename)
        self.cachefile = filename + '.tsp-results.pickle'

        self.maze.load_products()
        self.num = self.maze.product_count
        self.products = self.maze.products_dict

        # initialize array for the distances.
        if os.path.exists(self.cachefile):
            print 'Loading from cachefile: %s' % self.cachefile
            self.load_cache()
        else:
            size = len(self.locations())
            self.results = map(list, [[TSPMaze.EMPTY] * size] * size)

    def calculate_paths(self, refine=False):
        maze = self.maze
        count = self.count()

        total_paths = 0.5 * (count - 1) * count
        print 'Calculate paths between %d products (%d paths total) in maze %s.' % (
            count, total_paths, maze.name
        )
        overall_start_time = time.time()
        elapsed_list = []

        for A in range(len(self.locations())):
            self.set_result(A, A, None)

        self.dump_cache()

        settings = self.base_aco_settings.copy()
        settings.update(dict(
            ant_count=5,
            do_reconnaissance=10000
        ))
        aco = ACO(maze, **settings)
        maze = aco.reconnaissance(iterations=4)

        i = 1
        failes = 0
        locationsA = self.locations()
        random.shuffle(locationsA)
        locationsA = locationsA
        for A, locationA in locationsA:
            locationsB = self.locations()
            random.shuffle(locationsB)
            for B, locationB in locationsB:
                i += 1

                if A is B:
                    continue
                if not refine and self.results[B][A] not in (TSPMaze.EMPTY, TSPMaze.FAILED):
                    continue

                print 'Route %2d -> %2d' % (A, B),

                maze.reset_start_end(locationA, locationB)

                start_time = time.time()

                tries = 1
                settings = self.base_aco_settings.copy()
                settings.update(dict(
                    iterations=3,
                    ant_count=8,
                    ant_max_steps=4000,
                    evaporation=0.1
                ))
                aco = ACO(maze, **settings)
                ant = aco.run()

                if ant is None:
                    print 'try reverse,',
                    maze.reset_start_end(locationB, locationA)
                    aco = ACO(maze, **settings)
                    ant = aco.run()
                    tries += 1

                while ant is None and tries < 3:
                    print 'try %d failed,' % tries,
                    # we have to reset pheromone to start a really new search
                    maze.reset_pheromone()
                    settings.update(dict(
                        iterations=6,
                        ant_count=tries * 10,
                        ant_max_steps=tries * 10000,
                    ))
                    aco = ACO(maze, **settings)
                    ant = aco.run()

                    tries += 1

                elapsed = time.time() - start_time
                elapsed_list.append(elapsed)

                if ant is None:
                    self.set_result(A, B, TSPMaze.FAILED, elapsed=elapsed)
                    print '\n!! not found in %0.2fs, run again to try again. ' % elapsed
                    failes += 1
                else:
                    self.set_result(A, B, ant)

                    print 'done (length: %d) in %0.2fs' % (len(ant.trail), elapsed)

                if i % self.count() == 1:
                    print '  running %0.2fs now, average time: %0.2fs (TSP matrix done in: %0.0fs)' % (
                        time.time() - overall_start_time,
                        mean(elapsed_list),
                        total_paths * mean(elapsed_list)
                    )
                self.dump_cache()

        return failes

    def set_result(self, A, B, ant=None, elapsed=None):
        known_length = None
        if self.results[A][B] not in (self.EMPTY, self.FAILED):
            known_length = self.results[A][B]['length']

            if ant in (TSPMaze.FAILED, None):
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
                if known_length <= len(ant.trail):
                    print 'Existing is better (%d > %d), not updating.' % (len(ant.trail), known_length),
                    return
                else:
                    print 'Updating solution  (%d < %d)' % (len(ant.trail), known_length),

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
        for x in range(self.count()):
            for y in range(self.count()):
                if self.results[x][y] in (self.EMPTY, self.FAILED):
                    return False

        return True

    def count(self):
        return len(self.locations())

    def locations(self):
        return (
            [(0, self.maze.start)] +
            self.products.items() +
            [(len(self.products) + 1, self.maze.end)]
        )

    def result_matrix(self):
        '''
        Display the result matrix in ascii from
        '''

        FORMAT = '%4d '

        ret = '   '
        for A, locationA in self.locations():
            ret += (FORMAT % A)
        ret += '\n'

        for A, locationA in self.locations():
            ret += '%2d ' % A
            for B, locationB in self.locations():
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
    start_time = time.time()
    print 'Loading TSPMaze...'
    tspmaze = TSPMaze()
    print '0 = start, %d = end' % (tspmaze.count() - 1)

    print tspmaze.result_matrix()
    print

    if tspmaze.done():
        print 'All possible paths calculated, running over it again to refine values.'
        print
        failed = tspmaze.calculate_paths(refine=True)

    else:
        failed = tspmaze.calculate_paths()
        tspmaze.result_matrix()

        print 'Failed paths: %d' % failed

        while not tspmaze.done():
            tspmaze.calculate_paths()

    print 'Total running time: %0.0fs' % (time.time() - start_time)
