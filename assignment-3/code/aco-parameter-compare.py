#!/usr/bin/env python

import pickle
import time
from numpy import arange

from aco import ACO
from maze import Maze

filename = '../data/easy-maze.txt'
outputfile = 'output/param-compare.pickle'

base_settings = dict(
    quiet=True,
    visualize=False,

    ant_count=10,
    evaportion=0.10,
    Q=50,

)

parameters = dict(
    evaporation=arange(0.05, 0.4, 0.025),
    Q=range(10, 100, 10),
)

vary_parameter = 'evaporation'

iterations = 20

if True:
    start_time = time.time()
    print 'Running ACO %d times for each value of %s: ' % (
        iterations, vary_parameter)
    print parameters[vary_parameter]

    results = []
    for param in parameters[vary_parameter]:
        print '%s = %f: ' % (vary_parameter, param),

        param_result = dict(
            best_trail=[],
            best_at_iteration=[],
        )
        for i in range(iterations):
            settings = base_settings.copy()
            settings.update({
                vary_parameter: param
            })
            maze = Maze.from_file(filename)
            aco = ACO(maze=maze, **settings)
            best_ant = aco.run()
            print len(best_ant.trail),

            param_result['best_trail'].append(len(best_ant.trail))
            param_result['best_at_iteration'].append(aco.get_first_iteration_with_best_trail())

        results.append(param_result)
        print

    print 'Done in %0.2fs' % (time.time() - start_time)
    with open(outputfile, 'w') as f:
        pickle.dump(results, f)
else:
    results = pickle.load(open(outputfile))


from pylab import *
import matplotlib.pyplot as plt

# prepare data
data = [x['best_trail'] for x in results]
ymin = min([min(x) for x in data]) * 0.9
ymax = max([max(x) for x in data]) * 1.1

# plot
figure(1)
boxplot(data)
title('ACO on maze %s (%d times)' % (filename, iterations))
xticks(range(1, len(parameters[vary_parameter]) + 1), parameters[vary_parameter], rotation=90)
xlabel('Values for %s' % vary_parameter)
ylim([ymin, ymax])
ylabel('Trail length of best ant')


plt.savefig('output/aco-compare-%s.eps' % vary_parameter)
print 'Save figure...'
