#!/usr/bin/env python

import os
import sys
import time
import random
import pickle

from aco import ACO
from maze import Maze
from util import *


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

    updated = 0

    def __init__(self, filename='../data/hard-maze.txt', refine=False):
        self.maze = Maze.from_file(filename)
        self.original_start = tuple(self.maze.start)
        self.original_end = tuple(self.maze.end)

        self.cachefile = filename + '.tsp-results.pickle'
        self.refine = refine
        self.do_reconnaissance = 0

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


    def find_path(self, maze, locationA, locationB):
        maze.reset_start_end(locationA, locationB)

        tries = 1
        settings = self.base_aco_settings.copy()
        if self.refine:
            settings.update(dict(
                iterations=10,
                ant_count=15,
                ant_max_steps=4000,
                evaporation=0.2
            ))
        else:
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

        if not self.refine:
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

        return ant

    def calculate_paths(self):
        count = self.count()

        total_paths = 0.5 * (count - 1) * count
        if self.refine:
            total_paths *= 2
            print 'Trying to find better paths in maze...'
        else:
            print 'Calculate paths between %d products (%d paths total) in maze %s.' % (
                count, total_paths, self.maze.name
            )
        overall_start_time = time.time()
        elapsed_list = []

        # # clear paths from/to start/end
        # for A in range(len(self.locations())):
        #     self.set_result(0, A, TSPMaze.FAILED)
        #     self.set_result(19, A, TSPMaze.FAILED)

        # set path from from/to same node to zero
        for A in range(len(self.locations())):
            self.set_result(A, A, None)
        self.dump_cache()

        if self.do_reconnaissance > 0:
            settings = self.base_aco_settings.copy()
            settings.update(dict(
                ant_count=5,
                do_reconnaissance=self.do_reconnaissance
            ))
            aco = ACO(self.maze, **settings)
            maze = aco.reconnaissance(iterations=4)
        else:
            maze = self.maze

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
                if not self.refine and self.results[B][A] not in (TSPMaze.EMPTY, TSPMaze.FAILED):
                    continue

                print 'Route #%2d (%2d, %2d) -> #%2d (%2d, %2d)' % ((A, ) + locationA + (B, ) + locationB),

                start_time = time.time()
                ant = self.find_path(maze, locationA, locationB)
                elapsed = time.time() - start_time

                elapsed_list.append(elapsed)

                if ant is None:
                    self.set_result(A, B, TSPMaze.FAILED, elapsed=elapsed)
                    print RED, '\n!!', ENDC, ' not found in %0.2fs, run again to try again. ' % elapsed
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

        if A == B:
            self.results[A][B] = {
                'length': 0,
                'trail': []
            }
            return

        if ant is None:
            return

        if ant is TSPMaze.FAILED:
            self.results[A][B] = self.results[B][A] = ant
            return

        if ant is not None:
            if known_length is not None:
                # compare solution with known, store if better
                if known_length == len(ant.trail):
                    print 'Equal length',
                elif known_length < len(ant.trail):
                    print 'Existing is better (%d > %d), not updating.' % (len(ant.trail), known_length),
                    return
                else:
                    print 'Updating solution  %s(%d < %d)%s' % (
                        GREEN, len(ant.trail), known_length, ENDC
                    ),
                    self.updated += 1

            locationA = self.location(A)
            locationB = self.location(B)
            # print 'A: ', A, type(A), locationA
            # print 'B: ', B, type(B), locationB

            # print 'saving A->B'
            self.results[A][B] = dict(
                start=locationA,
                end=locationB,
                length=len(ant.trail),
                trail=ant.get_trail(start=locationA, end=locationB)
            )

            # print '\nsaving B->A'
            self.results[B][A] = dict(
                start=locationB,
                end=locationA,
                length=len(ant.trail),
                trail=ant.get_trail(start=locationB, end=locationA)
            )
            # print

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

    def location(self, label):
        if label == 0:
            return self.original_start
        elif label == len(self.products) + 1:
            return self.original_end
        else:
            return self.products[label]

    def locations(self):
        return (
            [(0, self.original_start)] +
            self.products.items() +
            [(len(self.products) + 1, self.original_end)]
        )
    def visualize_route(self, a, b):
        print self.results[a][b]

        a_coord = self.location(a)
        b_coord = self.location(b)
        print a_coord, b_coord

        trail = self.results[a][b]['trail']
        return self.maze.visualize_trail(a_coord, b_coord, trail)

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
                    ret += RED + 'fail ' + ENDC
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

    # for l in tspmaze.locations():
    #     print l


    print tspmaze.result_matrix()

    # for i in range(20):
    #     print i, tspmaze.location(i)
    # import sys
    # sys.exit()
    # print

    if tspmaze.done():
        print 'All possible paths calculated, running over it again to refine values.'
        print
        tspmaze.refine = True
        failed = tspmaze.calculate_paths()

        print 'Updated %d paths' % tspmaze.updated

    else:
        failed = tspmaze.calculate_paths()
        tspmaze.result_matrix()

        print 'Failed paths: %d' % failed

        while not tspmaze.done():
            tspmaze.calculate_paths()

    print 'Total running time: %0.0fs' % (time.time() - start_time)
