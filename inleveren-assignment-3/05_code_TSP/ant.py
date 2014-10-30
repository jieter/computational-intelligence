import random
from maze import Maze


def compare_trails(maze, a, b):
    width = maze.width
    height = maze.height

    row = [' '] * width + ['|'] + [' '] * width + ['|'] + [' '] * width + ['|']

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


def weighted_random_choice(choices, weight_key):
    '''
    choose randomly from `choices` with probability in `key`
    '''
    if len(choices) == 1:
        return choices[0]

    total = sum(p[weight_key] for p in choices)

    r = random.uniform(0, total)
    upto = 0
    for choice in choices:
        if upto + choice[weight_key] > r:
            return choice
        upto += choice[weight_key]

    return False


class Ant(object):

    def __init__(self, maze, start):
        self.maze = maze
        self.start = tuple(start)

        self.reset()

    def __str__(self):
        return 'Ant(%d, %d): t: %d' % (self.position + (len(self.trail), ))

    def __repr__(self):
        return self.__str__()

    def update_position(self, position, direction):
        self.position = position
        self.position_list.append(position)
        self.trail.append(direction)

    def reset(self, maze=None):
        self.done = False
        self.failed = False

        self.previous_position = None
        self.position = tuple(self.start)
        self.position_list = [self.start]
        self.disable_positions = []
        self.trail = []

        if maze is not None:
            self.maze = maze

    def moves_are_corner(self, moves):
        moves = [m[1] for m in moves]
        if len(moves) != 2:
            return False

        northsouth = Maze.NORTH in moves or Maze.SOUTH in moves
        if Maze.EAST in moves and northsouth:
            return True
        if Maze.WEST in moves and northsouth:
            return True

        return False

    def corners_face_same_dir(self, a, b):
        if not (self.moves_are_corner(a) and self.moves_are_corner(b)):
            return False

        a_moves = [m[1] for m in a]
        b_moves = [m[1] for m in b]

        for d in Maze.DIRECTIONS:
            if d in a_moves and d in b_moves:
                return True

        return False

    def step(self):
        '''
        Choose from the list of possible moves with probability defined
        by the pheromone amounts
        '''

        # possible moves from postion in maze.
        moves = self.maze.peek(self.position)

        if len(moves) == 0:
            self.failed = True

        # We found the end.
        if self.maze.end in [x[0] for x in moves]:
            [selected] = (x for x in moves if x[0] == self.maze.end)

            newPosition, direction, _ = selected
            self.update_position(newPosition, direction)

            self.done = True
            return True

        # look for cells we can disable:
        disable = None
        if len(self.position_list) > 2:
            previous_1 = self.position_list[-2]
            previous_2 = self.position_list[-3]

            prev_moves_1 = self.maze.peek(previous_1)
            prev_moves_2 = self.maze.peek(previous_2)

            # disable dead ends.
            # position is only reachable from second to last position, so we can
            # disable it in the maze
            if len(prev_moves_1) == 1:
                disable = previous_1

            # disable open spaces
            if self.moves_are_corner(prev_moves_2) and previous_2 is not self.position:
                if self.maze.is_diagonal(previous_2, self.position):
                    if len(moves) == 4:
                        disable = previous_2

                    if self.corners_face_same_dir(prev_moves_1, prev_moves_2):
                        disable = previous_2

                    if len(moves) == 3 and len(prev_moves_1) == 4:
                        disable = previous_2

            if disable is not None:
                if disable not in self.maze.points_of_interest():
                    self.disable_positions.append(disable)
                    self.maze.disable_at(disable)
                # else:
                    # print 'not disabling', disable, 'it is in POI list:', self.maze.points_of_interest()

                moves = self.maze.peek(self.position)

        # We have more than one option
        if len(self.position_list) > 1:
            moves = [p for p in moves if p[0] not in (self.position_list)]
            if len(moves) is 0:
                moves = self.maze.peek(self.position)

        selected = weighted_random_choice(moves, weight_key=2)

        if not selected:
            return

        newPosition, direction, _ = selected
        self.update_position(newPosition, direction)

    def optimize_trail(self, quiet=False):
        '''
        Try to make this track shorter by unrolling loops.
        Returns the difference in length.
        '''
        old_len = len(self.trail)
        new = self._optimize_backwards(self.position_list)

        if old_len < len(new):
            return 0

        # if not self.maze.is_valid_position_list(new):
        #     print 'new position_list is not valid (maybe due to disabled cells?)'
        #     return 0

        # print 'Before optimizing, len(trail) = %d, valid = %s' % (old_len, self.is_valid())
        # print 'new len: %d, diff: %d' % (len(new), old_len - len(new))

        # if not quiet:
        # compare_trails(self.maze, self.position_list, new)
        self.update_position_list(new)
        # print 'valid: ', self.is_valid()

        return old_len - len(new)

    def _optimize_backwards(self, old_list):
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

        # assert self.is_valid()

    def get_trail(self, start=None, end=None):

        if start is None or start == self.start:
            return list(self.trail)
        else:
            # reverse trail.
            ant = self.clone()
            ant.maze = ant.maze.clone()
            ant.maze.set_start(start)
            ant.maze.set_end(end)

            ant.update_position_list(ant.position_list)
            ant.reverse()
            return list(ant.trail)

    def reverse(self):
        if not self.done:
            raise 'Only done ants can be reversed'

        new_list = list(self.position_list)
        new_list.reverse()
        new_start = new_list[0]

        self.update_position_list(new_list)
        self.start = new_start
        return self

    def is_valid(self):
        '''
        Check if trail is valid for this maze.
        '''
        return self.maze.is_valid_trail(self.start, self.trail)

    def trail_to_str(self):
        '''
        Outputs prescribed format:

        len;
        (start x, y);
        step;step;step;step;
        '''
        trail = self.get_trail()
        return '%d;\n%d,%d;\n%s;' % (
            len(trail), self.start[0], self.start[1], ';'.join(map(str, trail)),
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
