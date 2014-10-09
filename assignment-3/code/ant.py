import random


def weighted_random_choice(choices, key):
    '''
    choose randomly from `choices` with probability in `key`
    '''
    total = sum(p[key] for p in choices)

    r = random.uniform(0, total)
    upto = 0
    for choice in choices:
        if upto + choice[key] > r:
            return choice
        upto += choice[key]


class Ant(object):

    def __init__(self, maze, start):
        self.maze = maze
        self.start = tuple(start)

        self.reset()

    def __str__(self):
        return 'Ant(%d, %d): t: %d' % (self.position + (len(self.trail), ))

    def __repr__(self):
        return self.__str__()

    def update_position(self, position):
        self.position = position
        self.position_list.append(position)

    def step(self):
        '''
        Choose from the list of possible moves with probability defined
        by the pheromone amounts
        '''

        # possible moves in maze.
        moves = self.maze.peek(self.position)

        if self.maze.end in [x[0] for x in moves]:
            [selected] = (x for x in moves if x[0] == self.maze.end)
            self.done = True
        else:
            # Dead end mitigation:
            # position is only reachable from second to last position, so we can
            # disable it in the maze
            if len(moves) == 1 and self.position not in (self.start):
                self.disable_positions.append(self.position)

                # When I turn this on, all kind of strange things happen
                # self.maze.disable_at(tuple(self.position))

            # We have more than one option
            if len(self.position_list) > 1:
                moves = [p for p in moves if p[0] not in (self.position_list)]
                if len(moves) is 0:
                    moves = self.maze.peek(self.position)

            selected = weighted_random_choice(moves, 2)

        newPosition, direction, tau = selected
        self.trail.append(direction)
        self.update_position(newPosition)

    def reset(self):
        self.done = False

        self.position = tuple(self.start)
        self.position_list = [self.start]
        self.disable_positions = []
        self.trail = []

    def trail_to_str(self):
        '''
        Outputs prescribed format:

        len;
        (start x, y);
        step;step;step;step;
        '''
        return '%d;\n%d,%d;\n%s' % (
            len(self.trail), self.start[0], self.start[1], ';'.join(map(str, self.trail)),
        )

    def clone(self):
        ant = Ant(self.maze, self.start)
        ant.done = self.done
        ant.position = self.position
        ant.position_list = self.position_list
        ant.trail = self.trail

        return ant

    def __lt__(self, other):
        return len(self.trail) < len(other.trail)
