import random


def compare_trails(maze, a, b):
    width = maze.width
    height = maze.height

    row = [' '] * width + ['|'] + [' '] * width + ['|'] + [' '] * width

    m = map(list, [row] * height)

    for x, y in a:
        m[y][x] = '.'
        m[y][x + 2 + 2 * width] = '.'

    for x, y in b:
        m[y][x + width + 1] = 'o'
        m[y][x + 2 + 2 * width] = 'o'

    print ' a' + (' ' * (width - 2)) + '| b' + (' ' * (width - 2)) + '| beide'
    print
    for r in m:
        print ''.join(r)


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

    def optimize_trail(self):
        '''
        Try to make this track shorter by unrolling loops.
        '''
        old_len = len(self.trail)
        new = self.optimize_backwards(self.position_list)

        if old_len < len(new):
            return

        # print 'Before optimizing, len(trail) = %d, valid = %s' % (old_len, self.is_valid())
        # print 'new len: %d, diff: %d' % (len(new), old_len - len(new))

        # compare_trails(self.maze, self.position_list, new)
        self.update_position_list(new)

        # print 'valid: ', self.is_valid()

        return old_len - len(new)

    def optimize_backwards(self, old_list):
        maze = self.maze
        new_list = []

        i = len(old_list) - 1
        while i >= 0:
            p = old_list[i]

            if maze.end == p:
                new_list.append(p)
                i -= 1
                continue

            if maze.start == p:
                new_list.append(p)
                break

            remainder = old_list[:-i]

            # look if we can bridge to the remainder.
            if p in remainder:
                p_index = remainder.index(p)

                new_list.append(p)

                i = p_index - 1
                continue

            # look if we can take a shortcut to a position in the remainder
            options = maze.peek(p)
            if self.start in options:
                new_list.append(self.start)
                break
            # insert check for each option in options to remainder

            # if we come here, no optimisation for this point...
            i -= 1
            new_list.append(p)

        new_list.reverse()
        return new_list

    def update_position_list(self, new_list):
        '''
        Update position_list and trail with positon list in new_list
        '''
        new_trail = []

        for i in range(1, len(new_list)):
            a = new_list[i - 1]
            b = new_list[i]
            new_trail.append(self.maze.move_direction(a, b))

        assert len(new_trail) + 1 == len(new_list)

        self.position_list = new_list
        self.trail = new_trail

        assert self.is_valid()

    def is_valid(self):
        '''
        Check if trail is valid for this maze.
        '''
        position = self.start
        maze = self.maze

        for move in self.trail:
            n = maze.peek_dir(position, move)

            if n is None:
                return False
            else:
                position = n[0]

        return position == maze.end

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
