import copy
import multiprocessing
import os
import random
import sys
import time

from maze import Maze, test_mazes
from visualize import Visualizer


def weighted_random_choice(choices, key):
    '''
    choose randomly from `choices` with probability in `key`
    '''
    total = sum(p[key] for p in choices)

    r = random.uniform(0, total)
    upto = 0
    for choice in choices:
        if upto + choice[key] > r:
            return choice
        upto += choice[key]


class Ant(object):

    def __init__(self, maze, start):
        self.maze = maze
        self.start = tuple(start)

        self.reset()

    def __str__(self):
        return 'Ant(%d, %d): t: %d' % (self.position + (len(self.trail), ))

    def __repr__(self):
        return self.__str__()

    def update_position(self, position):
        self.position = position
        self.position_list.append(position)

    def step(self):
        '''
        Choose from the list of possible moves with probability defined
        by the pheromone amounts
        '''

        options = self.maze.peek(self.position)
        if len(options) == 1 and self.position not in (self.start, self.maze.end):
            # position is only reachable from second to last position, so we can
            # disable it in the maze
            self.disable_positions.append(tuple(self.position))

        if len(self.position_list) > 2:
            options = [p for p in options if p[0] not in (self.position_list)]
            if len(options) is 0:
                options = self.maze.peek(self.position)

        selected = weighted_random_choice(options, 2)

        newPosition, direction, tau = selected

        self.trail.append(direction)
        self.update_position(newPosition)

        if newPosition == self.maze.end:
            # horay, found the end.
            self.done = True

    def reset(self):
        self.done = False

        self.position = tuple(self.start)
        self.position_list = [self.start]
        self.disable_positions = []
        self.trail = []

    def trail_to_str(self):
        '''
        Outputs prescribed format:

        len;
        (start x, y);
        step;step;step;step;
        '''
        return '%d;\n%d,%d;\n%s' % (
            len(self.trail), self.start[0], self.start[1], ';'.join(map(str, self.trail)),
        )


def compute_ant(ant):
    # TODO: magic number needs sane value!
    while not ant.done and len(ant.trail) < 10000:
        ant.step()

    if ant.done:
        print ' Ant found the end, trail length:', len(ant.trail)
    return ant


class ACO(object):
    '''
    Perform ACO on the maze.
    '''

    iterations = 20
    ant_count = 10

    evaporation = 0.3

    def __init__(self, maze):
        self.maze = maze
        self.ants = []

        # Inialize Q to a value close to
        self.Q = 1000

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
            print 'iteration', i

            # Make ants do their steps.
            self.ants = pool.map(compute_ant, self.ants)

            # disable the dead ends found by the ant
            for ant in self.ants:
                for p in ant.disable_positions:
                    self.maze.disable_at(p)

            # empty list of delta's
            delta_tau = map(list, [[0.0] * maze.width] * maze.height)

            # select the best ant:
            all_ants = self.ants + [global_best]
            # print '\n'.join(map(lambda x: str(x), all_ants))
            global_best = copy.deepcopy(min([a for a in all_ants if a is not None and a.done], key=lambda x: len(x.trail)))

            print 'Using the ant with trail length:', len(global_best.trail)

            # update pheromone in the maze, for unique positions
            best_position_list = list(set(global_best.position_list))
            delta_tau_k = self.Q / len(best_position_list)
            for x, y in best_position_list:
                delta_tau[y][x] += delta_tau_k

            maze.update_tau(delta_tau, evaporation=self.evaporation)

            # reset ants
            for ant in self.ants:
                ant.reset()

            if visualize:
                self.visualizer.update()
                self.visualizer.save('%dth_iteration.png' % i)

        pool.close()

        self.maze.disable_at((0, 0))
        self.visualizer.update()

        with open('output/solution.txt', 'w') as out:
            out.write(global_best.trail_to_str())
        # self.visualizer.wait()

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

    aco.run()

    print 'Done in %0.2fs' % (time.time() - start_time)

    os.system('convert $(for a in output/*.png; do printf -- "-delay 80 %s " $a; done; ) output/sequence.gif')
