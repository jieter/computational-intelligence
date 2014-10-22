#!/usr/bin/env python
# coding: utf-8

import numpy as np


class Maze(object):

    EAST = 0
    NORTH = 1
    WEST = 2
    SOUTH = 3

    DIRECTIONS = [EAST, NORTH, WEST, SOUTH]

    PATH = 1
    START = 's'
    END = 'e'
    WALKABLE = (PATH, START, END)

    WALL = 0
    DISABLED = -1

    start = None
    end = None

    def __init__(self, maze, size=None, start=None, end=None, name=None):
        # if size not defined, use input size.
        if size is None:
            self.height = len(maze)
            self.width = len(maze[0])
        else:
            self.width, self.height = map(int, size)

        self.original_maze = maze
        self.set_maze(maze)

        self.name = name or 'Maze [%dx%d]' % (self.width, self.height)

        if start is not None:
            self.set_start(start)
        if end is not None:
            self.set_end(end)

        if maze is not None and not self.find_start_end():
            raise ValueError(
                'Start & end must be defined in maze or explicitly'
            )
        self.reset_pheromone()

        self.products = []

    def reset_pheromone(self):
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
        if point in self.points_of_interest():
            return

        self.set_at(point, Maze.DISABLED)
        self.pheromone[point[1]][point[0]] = 0

    def points_of_interest(self):
        return [self.start, self.end] + self.products

    def walkable(self, point):
        return (
            -1 < point[0] < self.width and
            -1 < point[1] < self.height and
            self.get_at(point) in Maze.WALKABLE
        )

    def tau(self, point):
        return self.pheromone[point[1]][point[0]]

    def update_tau(self, delta_tau, evaporation):
        self.pheromone *= (1 - evaporation)
        self.pheromone += delta_tau

        # self.pheromone[self.start] = 0

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
        if len(moves) == 0:
            return None

        move_direction = [m for m in moves if m[1] == direction]

        if len(move_direction) == 1:
            return move_direction[0]
        else:
            return None

    def is_diagonal(self, a, b):
        xdiff = abs(b[0] - a[0])
        ydiff = abs(b[1] - a[1])

        return xdiff == 1 and ydiff == 1

    def move_direction(self, a, b):
        '''
        give the direction of the move between a and b,
        return None if move is not possible.
        '''
        if self.walkable(a) and self.walkable(b):
            xdiff = b[0] - a[0]
            ydiff = b[1] - a[1]

            if xdiff != 0 and ydiff != 0:
                # diagonal move, illegal
                return None

            if xdiff == 1:
                return Maze.EAST
            elif xdiff == -1:
                return Maze.WEST
            elif ydiff == 1:
                return Maze.SOUTH
            elif ydiff == -1:
                return Maze.NORTH

        return None

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

    def set_maze(self, maze):
        self.maze = list(map(list, maze))

    def reset_start_end(self, start, end):
        # self.set_maze(self.original_maze)
        self.reset_pheromone()

        self.set_start(start)
        self.set_end(end)

    def is_valid_trail(self, start, trail):
        '''
        Check if trail is valid for this maze.
        '''
        position = start

        for move in trail:
            n = self.peek_dir(position, move)

            if n is None:
                return False
            else:
                position = n[0]

        return position == self.end

    def is_valid_position_list(self, positions):
        if positions[0] != self.start or positions[-1] != self.end:
            return False

        prev = self.start
        for p in positions[1:]:
            xdiff = abs(p[0] - prev[0])
            ydiff = abs(p[1] - prev[1])

            if (xdiff == 1 and ydiff == 1) or (xdiff == 0 and ydiff == 0):
                return False

            if not self.walkable(p):
                return False

            prev = p

        return True

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
                         '▓' if x == Maze.WALL else \
                         'x' if x == Maze.DISABLED \
                         else x
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
        disabled = -2
        wall = -1.0
        empty = 2.0
        start_end = 0
        convert = lambda x: (
            wall if x == Maze.WALL else
            disabled if x == Maze.DISABLED else
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

    def load_products(self, filename='../data/tsp-products.txt'):
        with open(filename) as products:
            self.product_count = int(products.readline()[0:-2])

            # save all products to a dictionary
            self.products_dict = {
                int(product): tuple(map(int, location.split(',')))
                for product, location in
                [row[0:-2].split(':') for row in products]
            }
            self.products = self.products_dict.values()

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

        if 'hard-maze.txt' in filename:
            maze.load_products(filename.replace('hard-maze.txt', 'tsp-products.txt'))

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
            maze=map(stringloader, [
                '1111111111100111111',
                '1111111111100111111',
                '1111111001100111111',
                '1111111001100111111',
                '1111111011100001111',
                's111111001111111111',
                '1111111001111111111',
                '1111111001110000111',
                '1111111001110000000',
                '1111111001111111111',
                '1111111111111110000',
                '0000000000000011111',
                '1111111111111111111',
                '1110000000000000000',
                '1111111111111111111',
                '1110000000000000000',
                '1111111111111111111',
                '111111111110e111111',
                '0100010100001111111',
                '0110110111111111111',
                '0011100010001111111',
                '0001000011111111111',
            ]),
        ),
        'test2': dict(
            name='Test2',
            maze=map(stringloader, [
                's110000000001111111',
                '111111111110e111111',
                '0100010100001111111',
                '0110110111111111111',
                '0011100010001111111',
                '0001000011111111111',
            ])
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

    options = maze.peek((4, 4))

    for position, direction, pher in options:
        print position, direction, maze.move_direction((4, 4), position)

    print maze.is_diagonal((0, 0), (1, 1))
    print maze.is_diagonal((1, 1), (0, 0))
