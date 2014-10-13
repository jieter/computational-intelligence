#!/usr/bin/env python
# coding: utf-8

import numpy as np


class Maze(object):

    EAST = 0
    NORTH = 1
    WEST = 2
    SOUTH = 3

    START = 's'
    END = 'e'
    WALL = 0
    PATH = 1
    WALKABLE = (PATH, START, END)

    start = None
    end = None

    def __init__(self, size=None, maze=None, start=None, end=None, name=None):
        # if size not defined, use input size.
        if size is None:
            assert maze is not None, 'supply size or maze'
            self.height = len(maze)
            self.width = len(maze[0])
        else:
            self.width, self.height = map(int, size)

        self.maze = [] if maze is None else list(map(list, maze))

        self.name = name or 'Maze [%dx%d]' % (self.width, self.height)

        if start is not None:
            self.set_start(start)
        if end is not None:
            self.set_end(end)

        if maze is not None and not self.find_start_end():
            raise ValueError(
                'Start & end must be defined in maze or explicitly'
            )

        self.pheromone = np.full((self.height, self.width), 0.01)

        if self.end is not None:
            self.pheromone[self.end[1]][self.end[0]] = 0.02

    def get_at(self, point):
        return self.maze[point[1]][point[0]]

    def set_at(self, point, s):
        '''
        Set val `s` at coordinate `point` in the maze
        '''
        self.maze[point[1]][point[0]] = s

    def disable_at(self, point):
        self.set_at(point, Maze.WALL)

    def walkable(self, point):
        return (
            -1 < point[0] < self.width and
            -1 < point[1] < self.height and
            self.get_at(point) in Maze.WALKABLE
        )

    def tau(self, point):
        return self.pheromone[point[1]][point[0]]

    def increase_tau(self, point, amount):
        self.pheromone[point[1]][point[0]] += float(amount)

    def update_tau(self, delta_tau, evaporation):
        self.pheromone *= (1 - evaporation)
        self.pheromone += delta_tau

    def peek(self, point):
        '''
        returns a set of (point, direction, pheromone)-tuples reachable from
        `point`, an empty list if `point` is not walkable.
        '''
        if not self.walkable(point):
            return []

        x, y = point
        moves = [
            ((x + 1, y), Maze.EAST),
            ((x, y - 1), Maze.NORTH),
            ((x - 1, y), Maze.WEST),
            ((x, y + 1), Maze.SOUTH)
        ]
        return [
            (p[0], p[1], self.tau(p[0]))
            for p in moves if self.walkable(p[0])
        ]

    def peek_dir(self, point, direction):
        '''
        Peek in direction
        '''
        moves = self.peek(point)
        if len(moves) is 0:
            return None

        return next([m for m in moves if m[3] == direction])

    def set_start(self, point):
        '''
        Set start point if it fits in the maze
        '''
        point = map(int, point)
        assert point[0] < self.width, 'Point exceeds width'
        assert point[1] < self.height, 'Point exceeds height'

        # clear old start in maze
        if self.start is not None:
            self.set_at(self.start, Maze.PATH)

        self.start = tuple(point)
        self.set_at(point, Maze.START)

    def set_end(self, point):
        '''
        Set end point if it fits in the maze
        '''
        point = map(int, point)
        assert point[0] < self.width, 'Point exceeds width'
        assert point[1] < self.height, 'Point exceeds height'

        # clear old end in maze
        if self.end is not None:
            self.set_at(self.end, Maze.PATH)

        self.end = tuple(point)
        self.set_at(point, Maze.END)

    def find_start_end(self):
        '''
        Look in the maze for 's' and 'e' positions and save to self.start/end
        '''
        if self.start and self.end:
            return True

        for y in range(self.height):
            for x in range(self.width):
                if self.get_at((x, y)) is Maze.START:
                    self.start = (x, y)
                elif self.get_at((x, y)) == Maze.END:
                    self.end = (x, y)

        return self.start is not None and self.end is not None

    def ascii_formatted(self):
        '''
        Return a ascii representation of the maze, with start
        and end points.
        '''
        wall = lambda x: ' ' if x == 1 else \
                         '▓' if x == 0 else x
        edge = '▒'

        # format inner walls
        maze = [''.join(map(wall, x)) for x in self.maze]
        # top and bottom outer wall
        maze = [edge * self.width] + maze + [edge * self.width]
        # left and right outer wall
        maze = map(lambda x: edge + x + edge, maze)

        return '\n'.join(maze)

    def numerical(self):
        '''
        Return an NxM array of floats representing the maze
        '''
        wall = -1.0
        empty = 2.0
        start_end = 0
        convert = lambda x: (
            wall if x == 0 else
            empty if type(x) is int else start_end
        )

        convert_row = lambda y: list(convert(b) for b in y)
        return map(convert_row, self.maze)

    def __str__(self):
        return 'Maze %s:\n%s' % (
            self.name, self.ascii_formatted()
        )

    def to_file(self):
        '''
        Write maze to file specified by assignment
        '''
        convert = lambda x: '1' if x in Maze.WALKABLE else '0'
        return '%d %d\n%s' % (
            self.width,
            self.height,
            '\n'.join([' '.join(map(convert, x)) for x in self.maze])
        )

    @staticmethod
    def from_file(filename):
        '''
        Read maze from file in format specified by assignment.
        Assumes a second file exists with two coordinates for start
        and end points.
        '''
        with open(filename) as mazefile:
            with open(filename.replace('maze.txt', 'coordinates.txt')) as coords:
                maze = Maze(
                    size=mazefile.readline().split(' '),
                    name=filename,
                    maze=[map(int, row.split(' ')) for row in mazefile],
                    start=coords.readline()[0:-2].split(','),
                    end=coords.readline()[0:-2].split(',')
                )

        return maze


def test_mazes(name):
    street_in_middle = [0] * 4 + [1] + [0] * 5
    loop_row1 = [1] + [0] * 4 + [1] + [0] * 4
    loop_row2 = [0] * 5 + [1] + [0] * 3 + [1]

    stringloader = lambda x: [
        (int(c) if c in ('1', '0') else c)
        for c in list(x)
    ]

    # Some test mazes.
    mazes = {
        'empty': dict(
            name='Empty 10x10 maze',
            maze=[[1] * 10] * 10,
            start=(0, 0),
            end=(9, 9)
        ),
        'street': dict(
            name='Single street',
            maze=[[0] * 10, ['s'] + [1] * 8 + ['e'], [0] * 10]
        ),
        'street_with_junctions': dict(
            name='Single street with junctions',
            maze=map(stringloader, [
                '00100100100',
                's111111111e',
                '00010010100'
            ])
        ),
        'corner': dict(
            name='Corner',
            maze=[['s'] + [1] * 4,
                  [0] * 4 + [1],
                  [0] * 4 + [1],
                  [0] * 4 + [1],
                  [0] * 4 + ['e']],
        ),
        'cross': dict(
            name='dict with a cross',
            maze=[street_in_middle, street_in_middle,
                  street_in_middle, street_in_middle,
                  [1] * 10, street_in_middle,
                  street_in_middle, street_in_middle,
                  street_in_middle, street_in_middle],
            start=(0, 4),
            end=(9, 4)
        ),
        'loop': dict(
            name='Two roads with equal length',
            maze=[['s'] + [1] * 5 + [0] * 4,
                  loop_row1, loop_row1, loop_row1, loop_row1, [1] * 10,
                  loop_row2, loop_row2, loop_row2,
                  [0] * 5 + [1] * 4 + ['e']]
        ),
        'tour_detour': dict(
            name='Simple with obstacle',
            maze=[
                [1] * 10, [1] * 10,
                [1] * 4 + [0] * 2 + [1] * 4,
                [1] * 4 + [0] * 2 + [1] * 4,
                ['s'] + [1] * 3 + [0] * 2 + [1] * 3 + ['e'],
                [1] * 4 + [0] * 2 + [1] * 4,
                [1] * 4 + [0] * 2 + [1] * 4,
                [1] * 4 + [0] * 2 + [1] * 4,
                [1] * 10, [1] * 10]
        ),
        'chicane': dict(
            name='Chicane',
            maze=map(stringloader, [
                's10011111100e1',
                '11001100110011',
                '11001100110011',
                '11001100110011',
                '11111100111111'
            ])
        ),
        'chicane2': dict(
            name='Chicane 2',
            maze=map(stringloader, [
                's11101111111e1',
                '11010100100011',
                '10110100100001',
                '10110100100011',
                '10110111100010',
                '11111111111111'
            ])
        )

    }

    return Maze(**mazes[name])


if __name__ == '__main__':
    print Maze.from_file('../data/easy-maze.txt')
    # print Maze.from_file('../data/medium-maze.txt')
    # print Maze.from_file('../data/hard-maze.txt')

    maze = test_mazes('empty')
    print maze

    print maze.peek((4, 4))
