#!/usr/bin/env python
# coding: utf-8

DIRECTIONS = {
    'east': 0,
    'north': 1,
    'west': 2,
    'south': 3
}


class Maze(object):
    START = 's'
    END = 'e'
    WALKABLE = (1, START, END)

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

        self.pheromone = [[0.0] * self.width] * self.height

    def add_row(self, row):
        assert len(self.maze) <= self.height, \
            'Height mismatch, len(self.maze) = %d, height = %d, %s' % (
                len(self.maze), self.height, self.ascii_formatted_maze()
            )
        assert len(row) >= self.width, \
            'Width mismatch: len(row) = %d != %d' % (len(row), self.width)

        self.maze.append(map(int, row))

    def get_at(self, point):
        return self.maze[point[1]][point[0]]

    def set_at(self, point, s):
        '''
        Set val `s` at coordinate `point` in the maze
        '''
        self.maze[point[1]][point[0]] = s

    def walkable(self, point):
        return (
            -1 < point[0] < self.width and
            -1 < point[1] < self.height and
            self.get_at(point) in Maze.WALKABLE
        )

    def peek(self, point):
        '''
        returns a set of points reachable from `point`,
        an empty list if `point` is invalid
        '''
        if not self.walkable(point):
            return []

        x, y = point
        options = [
            (x - 1, y),
            (x, y - 1),
            (x + 1, y),
            (x, y + 1)
        ]
        return [p for p in options if self.walkable(p)]

    def set_start(self, point):
        '''
        Set start point if it fits in the maze
        '''
        point = map(int, point)
        assert point[0] < self.width, 'Point exceeds width'
        assert point[1] < self.height, 'Point exceeds height'

        self.start = point
        self.set_at(point, Maze.START)

    def set_end(self, point):
        '''
        Set end point if it fits in the maze
        '''
        point = map(int, point)
        assert point[0] < self.width, 'Point exceeds width'
        assert point[1] < self.height, 'Point exceeds height'

        self.end = map(int, point)
        self.set_at(point, Maze.END)

    def find_start_end(self):
        '''
        Look in the maze for 's' and 'e' positions and save to self.start/end
        '''
        for y in range(self.height):
            for x in range(self.width):
                if self.get_at((x, y)) == Maze.START:
                    self.start = (x, y)
                elif self.get_at((x, y)) == Maze.END:
                    self.end = (x, y)

        return self.start is not None and self.end is not None

    def ascii_formatted_maze(self):
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
        convert = lambda x: -1.0 if x == 0 else (float(x) if type(x) is int else 2)

        convert_row = lambda y: list(convert(b) for b in y)
        return map(convert_row, self.maze)

    def __str__(self):
        return 'Maze %s:\n%s' % (
            self.name, self.ascii_formatted_maze()
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
        with open(filename) as f:
            maze = Maze(size=f.readline().split(' '), name=filename)
            for row in f:
                maze.add_row(row.split(' '))

        '''Read start and end coordinates'''
        with open(filename.replace('maze.txt', 'coordinates.txt')) as f:
            maze.set_start(f.readline()[0:-2].split(','))
            maze.set_end(f.readline()[0:-2].split(','))

        return maze


def test_mazes(name):
    street_in_middle = [0] * 4 + [1] + [0] * 5
    loop_row1 = [1] + [0] * 4 + [1] + [0] * 4
    loop_row2 = [0] * 5 + [1] + [0] * 3 + [1]

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
        )
    }

    return Maze(**mazes[name])


if __name__ == '__main__':
    print Maze.from_file('../data/easy-maze.txt')
    # print Maze.from_file('../data/medium-maze.txt')
    # print Maze.from_file('../data/hard-maze.txt')

    maze = test_mazes('street')
    print maze