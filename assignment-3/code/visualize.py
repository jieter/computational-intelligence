import matplotlib.pyplot as plt
import numpy as np


class Visualizer(object):

    def __init__(self, maze):
        self.maze = maze

        plt.close('all')

        self.fig, self.ax = plt.subplots()
        self.ax.set_title(maze.name)
        plt.axis('off')

        self.update()


    def update(self):
        self.ax.imshow(self.maze.numerical(),
                  extent=[0, self.maze.width, 0, self.maze.height],
                  interpolation='nearest')

        plt.show()



if __name__ == '__main__':
    from maze import Maze

    maze = Maze.from_file('../data/easy-maze.txt')
    print maze
    Visualizer(maze)

