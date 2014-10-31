#!/usr/bin/env python

import itertools
import multiprocessing
import numpy as np
import os
import sys
import time
import traceback

from ant import Ant, compare_trails
from maze import Maze, test_mazes
from util import mean
from visualize import Visualizer


def ant_loop(ant, threshold):
    '''
    Ant loop is exited when the ants takes too much time.
    '''
    try:
        while not ant.done and not ant.failed and len(ant.trail) < threshold:
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

    multiprocessing = True

    do_reconnaissance = 4000

    maze_elimination = True

    def __init__(self, maze, **settings):
        self.maze = maze
        self.ants = []

        for name, value in settings.items():
            setattr(self, name, value)

        if self.visualize:
            self.visualizer = Visualizer(maze)
            self.visualizer.save('tmp/0_initial.png')

        if self.multiprocessing:
            self.pool = multiprocessing.Pool()

    def delta_matrix(self, ant):
        delta_tau = np.zeros((self.maze.height, self.maze.width))

        unique_positions = list(set(ant.position_list))
        delta_tau_k = self.Q / len(unique_positions)

        for x, y in unique_positions:
            delta_tau[y][x] += delta_tau_k

        return delta_tau

    def reconnaissance(self, iterations=1):
        maze = self.maze
        if self.do_reconnaissance < 1:
            return maze

        print 'performing reconnaissance with %d ants for %d steps in %d iterations' % (
            self.ant_count, self.do_reconnaissance, iterations
        )

        disabled = set()
        start_time = time.time()
        for iteration in range(iterations):
            ants = []
            for i in range(self.ant_count):
                ants.append(Ant(maze, maze.start))

            results = self.pool.map_async(
                ant_loop_apply, itertools.izip(ants, [self.do_reconnaissance] * self.ant_count)
            ).get(999999)

            for ant in results:
                for disable in ant.disable_positions:
                    maze.disable_at(disable)
                    disabled.add(disable)

        print 'Reconnaissance done, %d cells disabled in %0.2fs' % (
            len(disabled),
            time.time() - start_time
        )
        return maze

    def run(self):
        if not self.quiet:
            print 'starting with ACO with %d ants for %d iterations' % (
                self.ant_count, self.iterations
            )
        maze = self.maze

        self.iteration_best_trail = []

        # initialize ants
        for k in range(self.ant_count):
            self.ants.append(Ant(maze, maze.start))

        global_best = iteration_best = None
        for i in range(self.iterations):
            if not self.quiet:
                print '\nIteration: %d, Q: %d, max_steps: %d' % (i, self.Q, self.ant_max_steps)

            if self.multiprocessing:
                # Make ants do their steps.
                self.ants = self.pool.map_async(
                    ant_loop_apply, itertools.izip(self.ants, [self.ant_max_steps] * self.ant_count)
                ).get(9999999)
            else:
                print 'Stepping...'
                for ant in self.ants:
                    i = 0
                    while not ant.done and len(ant.trail) < self.ant_max_steps:
                        ant.step()

                        i += 1
                        if i % 1000 == 1:
                            self.visualizer.update('stepping: %d' % i)

                    if not ant.done:
                        print 'moving to next ant, this one stuck in', ant.position

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
            if self.maze_elimination:
                for ant in self.ants:
                    if ant is not None:
                        for p in ant.disable_positions:
                            self.maze.disable_at(p)

            # select the best ant:
            if len(done_ants) > 0:
                iteration_best = min(done_ants)

                # if global_best becomes invalid, forget it.
                # if global_best is not None:
                #     global_best.maze = self.maze
                #     if not global_best.is_valid():
                #         global_best = None
                #         if not self.quiet:
                #             print 'Forgot global best!'

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
                self.iteration_best_trail.append(len(iteration_best.trail))
            else:
                self.iteration_best_trail.append(None)

            maze.update_tau(delta_tau=deltas, evaporation=self.evaporation)

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
                if iteration_best is not None and global_best is not None:
                    print 'Best ant: %d, iteration best: %d' % (
                        len(global_best.trail),
                        len(iteration_best.trail)
                    )
                else:
                    print 'None of the ants finished stepping'

            # reset ants
            for ant in self.ants:
                ant.reset(maze)

            if self.visualize:
                self.visualizer.update('Pheromone level iteration %d' % i)
                self.visualizer.save('tmp/%dth_iteration.png' % i)

        if self.multiprocessing:
            self.interrupt()

        self.global_best = global_best
        return global_best

    def interrupt(self):
        if self.multiprocessing:
            self.pool.close()
            self.pool.join()

    def get_first_iteration_with_best_trail(self):
        trail_length = len(self.global_best.trail)

        for i, val in enumerate(self.iteration_best_trail):
            if val == trail_length:
                return i

if __name__ == '__main__':
    settings = {
        'easy': dict(
            ant_count=10,
            evaporation=0.15,
            iterations=10,
            Q=50,
            maze_elimination=False,
        ),
        'medium': dict(
            ant_count=20,
            Q=300,
            do_reconnaissance=0,
            maze_elimination=False
        ),
        'hard': dict(
            Q=4000,
            iterations=30,
            ant_count=40,
            evaporation=0.6,
            do_reconnaissance=8000,
            maze_elimination=False,
        ),
        'insane': dict(
            Q=1000,
            do_reconnaissance=10000,
            evaporation=0.6,
            iterations=20,
            ant_count=50,
        ),
        'test2': dict(
            Q=100,
            iterations=20,
        )
    }

    if len(sys.argv) > 1:
        maze_name = sys.argv[1]
    else:
        maze_name = 'test2'

    maze = test_mazes(maze_name)
    if maze is None:
        maze = Maze.from_file(os.path.join('..', 'data', '%s-maze.txt' % maze_name), name=maze_name)

    print '"%s"' % maze_name
    if maze_name in settings:
        settings = settings[maze_name]
    else:
        settings = dict()

    print 'Maze "%s" (%d, %d)' % (maze.name, maze.width, maze.height)
    print 'start:', maze.start, 'end:', maze.end

    start_time = time.time()

    aco = ACO(maze, **settings)
    aco.reconnaissance(iterations=2)
    aco.visualizer.update('Maze after reconnaissance')
    # print maze

    try:
        best = aco.run()
    except KeyboardInterrupt:
        aco.interrupt()
        print 'Interrupted'
        sys.exit()

    print
    print 'Best ant is_valid:', best.is_valid()
    print 'Done in %0.2fs' % (time.time() - start_time)
    print 'Best ant: ', len(best.trail)

    print maze

    if maze_name == 'test2':
        compare_trails(maze, best.get_trail(maze.start), best.get_trail(maze.end))

    with open('output/%s-solution_%d.txt' % (maze.name, len(best.trail)), 'w') as out:
        out.write(best.trail_to_str())

    os.system('convert $(for a in output/tmp/*.png; do printf -- "-delay 80 %s " $a; done; ) ' +
              'output/%s-sequence_%d.gif' % (maze.name, len(best.trail)))
    os.system('rm output/tmp/*.png')
