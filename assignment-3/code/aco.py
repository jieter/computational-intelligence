from maze import test_mazes
from visualize import Visualizer

class Ant(object):

    def __init__(self, maze, start):
        self.maze = maze
        self.start = tuple(start)
        self.position = tuple(start)
        self.trail = []

    def __str__(self):
        return 'Ant(maze, (%d, %d))' % self.position

    def __repr__(self):
        return self.__str__()

    def step(self):
        '''
        Choose from the list of possible moves with probability defined
        by the pheromone amounts
        '''

    def trail_to_str(self):
        '''

        len;
        (start x, y);
        step;step;step;step;
        '''
        raise '%d;\n%d,%d;\n%s' % (len(self.trail)) + self.start + (
            ';'.join(self.trail)
        )



class ACO(object):
    '''
    Perform ACO on the maze.
    '''

    iterations = 10

    ant_count = 10

    evaporation = 0.1

    def __init__(self, maze):
        self.maze = maze
        self.ants = []

        self.visualizer = Visualizer(maze)

    def run(self, visualize=True):
        maze = self.maze

        # initialize ants
        for k in range(self.ant_count):
            self.ants.append(Ant(maze, maze.start))

        for i in range(self.iterations):

            for k, ant in enumerate(self.ants):
                pass

            self.visualize.update()

if __name__ == '__main__':

    maze = test_mazes('empty')

    aco = ACO(maze)

    aco.run()

    print aco.ants
