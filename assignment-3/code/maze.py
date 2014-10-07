#!/usr/bin/env python
# coding: utf-8


class Maze(object):

    def __init__(self, width, height, maze=None):
        self.width = int(width)
        self.height = int(height)

        self.maze = maze or []

    def add_row(self, row):
        assert len(self.maze) <= self.height, \
            'Height mismatch, len(self.maze) = %d, height = %d, %s' % (
                len(self.maze), self.height, self.ascii_formatted_maze()
            )
        assert len(row) == self.width, \
            'Width mismatch: len(row) = %d != %d' % (len(row), self.width)

        self.maze.append(map(int, row))

    def set_at(self, point, s):
        '''Set val `s` at `point`'''
        self.maze[point[1]][point[0]] = s

    def set_start(self, point):
        point = map(int, point)
        self.start = point
        self.set_at(point, 's')

    def set_end(self, point):
        point = map(int, point)
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

    @staticmethod
    def from_file(filename):
        with open(filename) as f:
            width, height = f.readline().split(' ')

            maze = Maze(width, height)
            for row in f:

                maze.add_row(row.split(' '))

        with open(filename.replace('maze.txt', 'coordinates.txt')) as f:
            maze.set_start(f.readline()[0:-2].split(','))
            maze.set_end(f.readline()[0:-2].split(','))

        return maze

if __name__ == '__main__':
    print Maze.from_file('../data/easy-maze.txt')
    print Maze.from_file('../data/medium-maze.txt')
    print Maze.from_file('../data/hard-maze.txt')
