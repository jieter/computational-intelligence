#!/usr/bin/env python

import itertools
import multiprocessing
import numpy as np
import os
import sys
import time
import traceback

from ant import Ant
from maze import Maze, test_mazes
from util import mean
from visualize import Visualizer


def ant_loop(ant, threshold):
    '''
    Ant loop is exited when the ants takes too much time.
    '''
    try:
        while not ant.done and len(ant.trail) < threshold:
            ant.step()
    except:
        print 'error in ant loop: '
        traceback.print_exc()
        return None

    # if ant.done:
    #     print ' Ant found the end, trail length:', len(ant.trail)
    return ant


def ant_loop_apply(args):
    return ant_loop(*args)


class ACO(object):
    '''
    Perform ACO on the maze.
    '''

    iterations = 15

    evaporation = 0.1

    # Initialize Q to high value
    Q = 10000

    # update Q using the minimum path length  as value.
    update_Q = False

    ant_count = 10

    # Number of steps an ant may wander before it is terminated for that
    # iterations.
    ant_max_steps = 10000
    update_max_steps = False

    # Wether or not to optimize the trails of the ants after they found the end.
    optimize_ants = True

    visualize = True
    quiet = False

    def __init__(self, maze, **settings):
        self.maze = maze
        self.ants = []

        for name, value in settings.items():
            setattr(self, name, value)

        if self.visualize:
            self.visualizer = Visualizer(maze)
            self.visualizer.save('0_initial.png')

        self.pool = multiprocessing.Pool()

    def delta_matrix(self, ant):
        delta_tau = np.zeros((self.maze.height, self.maze.width))

        unique_positions = list(set(ant.position_list))
        delta_tau_k = self.Q / len(unique_positions)

        for x, y in unique_positions:
            delta_tau[y][x] += delta_tau_k

        return delta_tau

    def run(self):
        if not self.quiet:
            print 'starting with ACO with %d ants for %d iterations' % (
                self.ant_count, self.iterations
            )
        maze = self.maze

        self.iteration_best_trail = [None] * self.iterations

        # initialize ants
        for k in range(self.ant_count):
            self.ants.append(Ant(maze, maze.start))

        global_best = iteration_best = None
        for i in range(self.iterations):
            if not self.quiet:
                print '\nIteration: %d, Q: %d, max_steps: %d' % (i, self.Q, self.ant_max_steps)

            # Make ants do their steps.
            self.ants = self.pool.map_async(
                ant_loop_apply, itertools.izip(self.ants, [self.ant_max_steps] * self.ant_count)
            ).get(9999999)


            done_ants = [a for a in self.ants if a is not None and a.done]

            if not self.quiet:
                print '%d out of %d ants finished within %d steps.' % (
                    len(done_ants),
                    self.ant_count,
                    self.ant_max_steps
                )

            if self.optimize_ants:
                # optimize the trails for these ants
                opts = []
                for ant in done_ants:
                    opts.append(ant.optimize_trail(quiet=self.quiet))
                if not self.quiet:
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
                self.iteration_best_trail[i] = len(iteration_best.trail)

            # update ant_max_steps to the max value of this iteration
            if len(done_ants) > 3:
                if self.update_max_steps:
                    try:
                        self.ant_max_steps = min(
                            self.ant_max_steps,
                            max(len(x.trail) for x in done_ants if len(x.trail) < self.ant_max_steps)
                        )
                    except:
                        pass
                if self.update_Q:
                    self.Q = min(min(len(x.trail) for x in self.ants), self.Q)

            if not self.quiet:
                print 'Best ant: %d, iteration best: %d' % (
                    len(global_best.trail),
                    len(iteration_best.trail)
                )
            # reset ants
            for ant in self.ants:
                ant.reset()

            if self.visualize:
                self.visualizer.update('Pheromone level iteration %d' % i)
                self.visualizer.save('%dth_iteration.png' % i)

        self.pool.close()
        self.pool.join()

        self.global_best = global_best
        return global_best

    def get_first_iteration_with_best_trail(self):
        trail_length = len(self.global_best.trail)

        for i, val in enumerate(self.iteration_best_trail):
            if val == trail_length:
                return i

if __name__ == '__main__':
    settings = {
        '../data/easy-maze.txt': dict(
            ant_count=10,
            evaportion=0.15,
            Q=50
        ),
        '../data/medium-maze.txt': dict(
            ant_count=15
        )

    }
    if len(sys.argv) > 1:
        filename = os.path.join('..', 'data', sys.argv[1])
        maze = Maze.from_file(filename)

        settings = settings[filename]
    else:
        maze = test_mazes('tour_detour')
        settings = dict(
            ant_count=10,
            Q=20
        )

    print maze
    print 'Maze "%s" (%d, %d)' % (maze.name, maze.width, maze.height)
    print 'start:', maze.start, 'end:', maze.end

    start_time = time.time()

    aco = ACO(maze, **settings)
    try:
        best = aco.run()
    except KeyboardInterrupt:
        aco.pool.close()
        aco.pool.join()
        print 'Interrupted'
        sys.exit()

    print
    print 'Done in %0.2fs' % (time.time() - start_time)
    print 'Best ant: ', len(best.trail)

    with open('output/solution_%d.txt' % len(best.trail), 'w') as out:
        out.write(best.trail_to_str())

    os.system('convert $(for a in output/*.png; do printf -- "-delay 80 %s " $a; done; ) ' +
              'output/sequence_%d.gif' % len(best.trail))
    os.system('rm output/*.png')
