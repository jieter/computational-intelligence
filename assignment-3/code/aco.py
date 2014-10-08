import random

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
        return 'Ant(maze, (%d, %d))' % self.position

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
        self.trail = []

    def trail_to_str(self):
        '''
        Outputs prescribed format:

        len;
        (start x, y);
        step;step;step;step;
        '''
        raise '%d;\n%d,%d;\n%s' % (len(self.trail)) + self.start + (
            ';'.join(self.trail)
        )

import multiprocessing

def compute_ant(ant):
    while not ant.done and len(ant.trail) < 10000:
        ant.step()

    print ' Ant found the end, trail length:', len(ant.trail)
    return ant

class ACO(object):
    '''
    Perform ACO on the maze.
    '''

    iterations = 10
    ant_count = 10

    evaporation = 0.1


    def __init__(self, maze):
        self.maze = maze
        self.ants = []

        # Inialize Q to a value close to
        self.Q = maze.width * maze.height

        self.visualizer = Visualizer(maze)

    def run(self, visualize=True):
        maze = self.maze

        # initialize ants
        for k in range(self.ant_count):
            self.ants.append(Ant(maze, maze.start))

        for i in range(self.iterations):
            print 'iteration', i

            pool = multiprocessing.Pool()
            self.ants = pool.map(compute_ant, self.ants)
            # for k, ant in enumerate(self.ants):
            #     while not ant.done:
            #         ant.step()
            #     print 'Ant found the end, trail length:', len(ant.trail)

            delta_tau = map(list, [[0.0] * maze.width] * maze.height)

            # select the best ant:
            best = min([a for a in self.ants if a.done], key=lambda x: len(x.trail))
            print 'Using the ant with trail length:', len(best.trail)

            # update pheromone in the maze, for unique positions
            best_position_list = list(set(best.position_list))
            delta_tau_k = self.Q / len(best_position_list)
            for x, y in best_position_list:
                delta_tau[y][x] += delta_tau_k

            maze.update_tau(delta_tau, evaporation=self.evaporation)
            # reset ants
            for ant in self.ants:
                ant.reset()

            if visualize:
                self.visualizer.update()
                self.visualizer.save('after_%d.png' % i)


        self.visualizer.update()
        self.visualizer.wait()

if __name__ == '__main__':

    import sys
    import os
    import time

    if len(sys.argv) > 1:
        maze = Maze.from_file(os.path.join('..', 'data', sys.argv[1]))
    else:
        maze = test_mazes('chicane2')
        print maze
        # maze = Maze.from_file('../data/easy-maze.txt')

    print 'Maze "%s" (%d, %d)' % (maze.name, maze.width, maze.height)
    print 'start:', maze.start, 'end:', maze.end
    start_time = time.time()
    aco = ACO(maze)

    aco.run()

    print 'Done in %0.2fs' % (time.time() - start_time)
