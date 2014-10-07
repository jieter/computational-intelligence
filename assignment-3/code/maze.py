#!/usr/bin/env python
# coding: utf-8


class Maze(object):
    WALKABLE = (1, 's', 'e')

    def __init__(self, size=None, maze=None, start=None, end=None):
        print 'start new Maze'
        # if size not defined, use input size.
        if size is None:
            assert maze is not None, 'supply size or maze'
            self.height = len(maze)
            self.width = len(maze[0])
        else:
            self.width, self.height = map(int, size)

        self.maze = list(map(list, maze)) or []

        print self.maze

        if start is not None:
            self.set_start(start)

        if end is not None:
            self.set_end(end)

    def add_row(self, row):
        assert len(self.maze) <= self.height, \
            'Height mismatch, len(self.maze) = %d, height = %d, %s' % (
                len(self.maze), self.height, self.ascii_formatted_maze()
            )
        assert len(row) >= self.width, \
            'Width mismatch: len(row) = %d != %d' % (len(row), self.width)

        self.maze.append(map(int, row))

    def set_at(self, point, s):
        '''Set val `s` at `point`'''
        print 'set_at', point, s
        self.maze[point[1]][point[0]] = s

    def walkable(self, point):
        return self.maze[point[1]][point[0]] in Maze.WALKABLE

    def set_start(self, point):
        point = map(int, point)
        assert point[0] < self.width, 'Point exceeds width'
        assert point[1] < self.height, 'Point exceeds height'

        self.start = point
        self.set_at(point, 's')

    def set_end(self, point):
        point = map(int, point)
        assert point[0] < self.width, 'Point exceeds width'
        assert point[1] < self.height, 'Point exceeds height'

        self.end = map(int, point)
        self.set_at(point, 'e')

    def ascii_formatted_maze(self):
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

    def __str__(self):
        return 'Maze [%dx%d]:\n%s' % (
            self.width, self.height, self.ascii_formatted_maze()
        )

    def to_file(self):
        conv = lambda x: '1' if x in Maze.WALKABLE else '0'
        return '%d %d\n%s' % (
            self.width,
            self.height,
            '\n'.join([' '.join(map(conv, x)) for x in self.maze])
        )

    @staticmethod
    def from_file(filename):
        with open(filename) as f:
            maze = Maze(f.readline().split(' '))
            for row in f:
                maze.add_row(row.split(' '))

        '''Read start and end coordinates'''
        with open(filename.replace('maze.txt', 'coordinates.txt')) as f:
            maze.set_start(f.readline()[0:-2].split(','))
            maze.set_end(f.readline()[0:-2].split(','))

        return maze


street_in_middle = [0] * 4 + [1] + [0] * 5
loop_top = [1] * 6 + [0] * 4
loop_row1 = [1] + [0] * 4 + [1] + [0] * 4
loop_row2 = [0] * 5 + [1] + [0] * 3 + [1]

testMazes = {
    'empty': Maze(
        maze=[[1] * 10] * 10,
        start=(0, 0),
        end=(9, 9)
    ),
    'street': Maze(
        maze=[[0] * 10, [1] * 10, [0] * 10],
        start=(0, 1),
        end=(9, 1)
    ),
    'cross': Maze(
        maze=[street_in_middle, street_in_middle,
              street_in_middle, street_in_middle,
              [1] * 10, street_in_middle,
              street_in_middle, street_in_middle,
              street_in_middle, street_in_middle],
        start=(0, 4),
        end=(9, 4)
    ),
    'loop': Maze(
        maze=[loop_top, loop_row1, loop_row1, loop_row1, loop_row1, [1] * 10,
              loop_row2, loop_row2, loop_row2, [0] * 5 + [1] * 5],
        start=(0, 0),
        end=(9, 9)
    )
}


if __name__ == '__main__':
    # print Maze.from_file('../data/easy-maze.txt')
    # print Maze.from_file('../data/medium-maze.txt')
    # print Maze.from_file('../data/hard-maze.txt')

    print testMazes['empty']
