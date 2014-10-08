import matplotlib.pyplot as plt


class Visualizer(object):

    def __init__(self, maze):
        self.maze = maze

        plt.close('all')

        self.fig, (self.ax1, self.ax2) = plt.subplots(nrows=2)

        self.ax1.set_title(maze.name)
        self.ax2.set_title('pheromone')

        self.update()

    def update(self):
        extent = [0, self.maze.width, 0, self.maze.height]

        self.ax1.imshow(self.maze.numerical(),
                        extent=extent,
                        interpolation='nearest')

        self.ax2.imshow(self.maze.pheromone,
                        extent=extent,
                        interpolation='nearest')

        plt.axis('off')
        plt.show()


if __name__ == '__main__':
    from maze import Maze

    maze = Maze.from_file('../data/easy-maze.txt')
    print maze
    Visualizer(maze)
