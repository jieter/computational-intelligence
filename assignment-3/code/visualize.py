import os
import matplotlib.pyplot as plt


class Visualizer(object):

    def __init__(self, maze):
        self.maze = maze

        plt.close('all')

        self.fig, (self.ax1, self.ax2) = plt.subplots(nrows=2)

        self.ax1.set_title(maze.name)
        self.ax2.set_title('pheromone')

        self.update()
        plt.ion()
        plt.show()

    def update(self):
        extent = [0, self.maze.width, 0, self.maze.height]

        self.ax1.imshow(self.maze.numerical(),
                        extent=extent,
                        interpolation='nearest')

        pher = self.ax2.imshow(
            self.maze.pheromone,
            extent=extent,
            interpolation='nearest'
        )
        plt.draw()

        # plt.colorbar(pher, ax=self.ax2)
        plt.axis('off')

    def wait(self):
        print 'Waiting for image to be closed...'
        plt.ioff()
        plt.show()

    def save(self, filename):
        plt.savefig(os.path.join('output', filename))

if __name__ == '__main__':
    from maze import Maze

    maze = Maze.from_file('../data/easy-maze.txt')
    print maze
    Visualizer(maze)
