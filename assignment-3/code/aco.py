#!/usr/bin/env python

import itertools
import multiprocessing
import numpy as np
import os
import sys
import time

from ant import Ant
from maze import Maze, test_mazes
from util import mean
from visualize import Visualizer


def ant_loop(ant, threshold):
    '''
    Ant loop is exited when the ants takes too much time.
    '''
    while not ant.done and len(ant.trail) < threshold:
        ant.step()

    if ant.done:
        print ' Ant found the end, trail length:', len(ant.trail)
    return ant


def ant_loop_apply(args):
    return ant_loop(*args)


class ACO(object):
    '''
    Perform ACO on the maze.
    '''

    evaporation = 0.1

    # Initialize Q to high value
    Q = 1000
    # update Q using the minimum path length  as value.
    update_Q = False

    # Number of steps an ant may wander before it is terminated for that
    # iterations.
    ant_max_steps = 10000

    # Wether or not to optimize the trails of the ants after they found the end.
    optimize_ants = True

    def __init__(self, maze, visualize=True, iterations=20, ant_count=15):
        self.maze = maze
        self.ants = []

        self.visualize = visualize
        self.iterations = iterations
        self.ant_count = ant_count

        if visualize:
            self.visualizer = Visualizer(maze)
            self.visualizer.save('0_initial.png')

    def delta_matrix(self, ant):
        delta_tau = np.zeros((self.maze.height, self.maze.width))

        unique_positions = list(set(ant.position_list))
        delta_tau_k = self.Q / len(unique_positions)

        for x, y in unique_positions:
            delta_tau[y][x] += delta_tau_k

        return delta_tau

    def run(self, quiet=False):
        maze = self.maze
        pool = multiprocessing.Pool()

        # initialize ants
        for k in range(self.ant_count):
            self.ants.append(Ant(maze, maze.start))

        global_best = iteration_best = None
        for i in range(self.iterations):
            if not quiet:
                print '\nIteration: %d, Q: %d, max_steps: %d' % (i, self.Q, self.ant_max_steps)

            # Make ants do their steps.
            self.ants = pool.map(ant_loop_apply, itertools.izip(self.ants, [self.ant_max_steps] * self.ant_count))

            if not quiet:
                print 'Done stepping for this iteration...'

            done_ants = [a for a in self.ants if a is not None and a.done]

            if self.optimize_ants:
                # optimize the trails for these ants
                opts = []
                for ant in done_ants:
                    opts.append(ant.optimize_trail())
                print 'Optimisation reduced trail langth with an average of', mean(opts)

            # disable the dead ends found by the ant
            for ant in self.ants:
                for p in ant.disable_positions:
                    self.maze.disable_at(p)

            # select the best ant:
            if len(done_ants) > 0:
                iteration_best = min(done_ants)

                if global_best is None:
                    global_best = iteration_best.clone()
                else:
                    global_best = min([iteration_best, global_best]).clone()

            # update pheromone in the maze, for unique positions
            deltas = np.zeros((self.maze.height, self.maze.width))
            if global_best is not None:
                deltas = self.delta_matrix(global_best)

            if iteration_best is not None and global_best is not iteration_best:
                deltas += self.delta_matrix(iteration_best)

            # only update if iteration returned something.
            if iteration_best is not None:
                maze.update_tau(delta_tau=deltas, evaporation=self.evaporation)

            # update ant_max_steps to the max value of this iteration
            if len(done_ants) > 3:
                try:
                    self.ant_max_steps = min(
                        self.ant_max_steps,
                        max(len(x.trail) for x in done_ants if len(x.trail) < self.ant_max_steps)
                    )
                except:
                    pass
                if self.update_Q:
                    self.Q = min(min(len(x.trail) for x in self.ants), self.Q)

            # reset ants
            for ant in self.ants:
                ant.reset()

            if self.visualize:
                self.visualizer.update('Pheromone level iteration %d' % i)
                self.visualizer.save('%dth_iteration.png' % i)

        pool.close()
        pool.join()

        return global_best

if __name__ == '__main__':
    if len(sys.argv) > 1:
        maze = Maze.from_file(os.path.join('..', 'data', sys.argv[1]))
    else:
        maze = test_mazes('tour_detour')
        print maze
        # maze = Maze.from_file('../data/easy-maze.txt')

    print 'Maze "%s" (%d, %d)' % (maze.name, maze.width, maze.height)
    print 'start:', maze.start, 'end:', maze.end

    start_time = time.time()

    aco = ACO(maze)
    best = aco.run()

    print
    print 'Done in %0.2fs' % (time.time() - start_time)
    print 'Best ant: ', len(best.trail)

    with open('output/solution_%d.txt' % len(best.trail), 'w') as out:
        out.write(best.trail_to_str())

    os.system('convert $(for a in output/*.png; do printf -- "-delay 80 %s " $a; done; ) ' +
              'output/sequence_%d.gif' % len(best.trail))
    os.system('rm output/*.png')
