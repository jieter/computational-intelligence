import copy
import itertools
import multiprocessing
import os
import sys
import time

from ant import Ant
from maze import Maze, test_mazes
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

    iterations = 30
    ant_count = 15

    evaporation = 0.25

    # Initialize Q to high value
    Q = 1000

    # Number of steps an ant may wander before it is terminated for that
    # iterations.
    ant_max_steps = 10000

    def __init__(self, maze):
        self.maze = maze
        self.ants = []

        self.visualizer = Visualizer(maze)
        self.visualizer.save('0_initial.png')

    def run(self, visualize=True):
        maze = self.maze
        pool = multiprocessing.Pool()

        # initialize ants
        for k in range(self.ant_count):
            self.ants.append(Ant(maze, maze.start))

        global_best = None
        for i in range(self.iterations):
            print '\nIteration: %d, Q: %d, max_steps: %d' % (i, self.Q, self.ant_max_steps)

            # Make ants do their steps.
            self.ants = pool.map(ant_loop_apply, itertools.izip(self.ants, [self.ant_max_steps] * self.ant_count))

            done_ants = [a for a in self.ants if a is not None and a.done]
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

            print 'Using the ant with trail length:', len(global_best.trail)

            # update pheromone in the maze, for unique positions
            best_position_list = list(set(global_best.position_list))
            delta_tau_k = self.Q / len(best_position_list)

            # empty list of delta's
            delta_tau = map(list, [[0.0] * maze.width] * maze.height)
            for x, y in best_position_list:
                delta_tau[y][x] += delta_tau_k

            maze.update_tau(delta_tau, evaporation=self.evaporation)

            # update ant_max_steps to the max value of this iteration
            ants_done = [x for x in self.ants if x.done]
            if len(ants_done) > 3:
                try:
                    self.ant_max_steps = max(len(x.trail) for x in ants_done if len(x.trail) < self.ant_max_steps)
                except:
                    #
                    pass
                self.Q = min(min(len(x.trail) for x in self.ants), self.Q)

            # reset ants
            for ant in self.ants:
                ant.reset()

            if visualize:
                self.visualizer.update('Pheromone level iteration %d' % i)
                self.visualizer.save('%dth_iteration.png' % i)

        pool.close()

        return global_best

if __name__ == '__main__':
    if len(sys.argv) > 1:
        maze = Maze.from_file(os.path.join('..', 'data', sys.argv[1]))
    else:
        maze = test_mazes('street_with_junctions')
        print maze
        # maze = Maze.from_file('../data/easy-maze.txt')

    print 'Maze "%s" (%d, %d)' % (maze.name, maze.width, maze.height)
    print 'start:', maze.start, 'end:', maze.end

    start_time = time.time()

    aco = ACO(maze)
    best = aco.run()

    print 'Done in %0.2fs' % (time.time() - start_time)

    with open('output/solution_%d.txt' % len(best.trail), 'w') as out:
        out.write(best.trail_to_str())

    os.system('convert $(for a in output/*.png; do printf -- "-delay 80 %s " $a; done; ) ' +
              'output/sequence_%d.gif' % len(best.trail))

