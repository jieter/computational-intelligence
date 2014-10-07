#!/usr/bin/env python
# coding: utf-8

class Maze(object):

    def __init__(self, width, height, maze=[]):
        self.width = int(width)
        self.height = int(height)

        self.maze = maze

    def add_row(self, row):
        assert len(self.maze) <= self.height
        assert len(row) == self.width, 'Width mismatch: len(row) = %d != %d' % (len(row), self.width)

        self.maze.append(map(int, row));

    def formatted_maze(self):
        wall = lambda x: ' ' if x == 1 else '▓'
        edge = '▒'

        # format inner walls
        maze = [''.join(map(wall, x)) for x in self.maze]
        # top and bottom outer wall
        maze = [edge * self.width] + maze + [edge * self.width]
        # left and right outer wall
        maze = map(lambda x: edge + x + edge, maze)

        return '\n'.join(maze)


    def __str__(self):
        return 'Maze [%dx%d]:\n%s' % (self.width, self.height, self.formatted_maze())

    @staticmethod
    def from_file(filename):
        with open(filename, 'r') as f:
            width, height = f.readline().split(' ')

            maze = Maze(width, height)
            for row in f:
                maze.add_row(row.split(' '))

        return maze


if __name__ == '__main__':
    maze = Maze.from_file('../data/easy-maze.txt');

    print maze

