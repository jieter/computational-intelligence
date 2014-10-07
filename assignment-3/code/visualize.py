import matplotlib.pyplot as plt
import numpy as np


def visualize_maze(maze):
    plt.close('all')
    fig, ax = plt.subplots()

    ax.imshow(maze.numerical(), extent=[0, maze.width, 0, maze.height],
              interpolation='nearest')
    ax.set_title(maze.name)

    plt.show()

if __name__ == '__main__':
    from maze import Maze

    maze = Maze.from_file('../data/easy-maze.txt')
    print maze
    visualize_maze(maze)

