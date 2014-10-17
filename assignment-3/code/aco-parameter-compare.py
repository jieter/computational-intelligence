#!/usr/bin/env python

import pickle
import time
from numpy import arange
from pylab import *
import matplotlib.pyplot as plt

from aco import ACO
from maze import Maze

default_settings = dict(
    quiet=True,
    visualize=False,

    ant_count=20,
    evaportion=0.10,
    Q=50,
)

parameters = dict(
    evaporation=arange(0.05, 0.6, 0.05),
    Q=[10, 20, 30, 32, 34, 36, 37, 38, 39, 40, 41, 42, 44, 46, 48, 50, 60, 70, 80, 90, 100, 200],
    ant_count=[1, 2, 4, 8, 10, 12, 16, 20, 30, 50, 100, 200, 400],
    optimize_ants=[True, False],
)

def make_boxplot(basename, data, plot_title, xvalues, labelx, labely):
    print data
    figure()
    boxplot(data)
    title(plot_title)
    xticks(range(1, len(xvalues) + 1), xvalues)
    ylim([
        min([min(x) for x in data]) * 0.9,
        max([max(x) for x in data]) * 1.1
    ])

    xlabel(labelx)
    ylabel(labely)

    plt.savefig(basename + '.eps')
    plt.savefig(basename + '.png')
    print 'Saved figure %s ...' % basename

def parameter_compare(maze_name, vary_parameter, compute=True):
    filename = '../data/%s-maze.txt' % maze_name
    outputfile = 'compare-graphs/%s/param-compare-%%s.pickle' % maze_name

    iterations = 20

    if compute:
        start_time = time.time()
        print 'Running ACO %d times for each %d different values of %s: ' % (
            iterations,
            len(parameters[vary_parameter]),
            vary_parameter
        )
        print parameters[vary_parameter]

        results = []
        for param in parameters[vary_parameter]:
            print '%s = %s: ' % (vary_parameter, str(param)),

            param_result = dict(
                best_trail=[],
                best_at_iteration=[],
                running_time=[]
            )
            for i in range(iterations):
                settings = default_settings.copy()
                settings.update({
                    vary_parameter: param
                })
                aco_start = time.time()
                maze = Maze.from_file(filename)
                aco = ACO(maze=maze, **settings)
                best_ant = aco.run()
                print len(best_ant.trail),

                param_result['best_trail'].append(len(best_ant.trail))
                param_result['best_at_iteration'].append(aco.get_first_iteration_with_best_trail())
                param_result['running_time'].append(time.time() - aco_start)

            results.append(param_result)
            print

        print '%d runs done in %0.2fs' % (
            iterations * len(parameters[vary_parameter]),
            start_time - time.time()
        )
        with open(outputfile % vary_parameter, 'w') as f:
            pickle.dump(results, f)
    else:
        results = pickle.load(open(outputfile % vary_parameter))

    for metric, labely in (
            ('best_trail', 'Trail length of best trail'),
            ('best_at_iteration', 'First iteration best occurs'),
            ('running_time', 'Running time of ACO'), ):

        make_boxplot(
            basename='compare-graphs/' + maze_name + '/aco-compare-' + vary_parameter + '-' + metric,
            data=[x[metric] for x in results],
            plot_title='ACO on maze %s (%d times)' % (maze_name, iterations),
            xvalues=parameters[vary_parameter],
            labelx='Values for %s' % vary_parameter,
            labely=labely
        )

    return results

if __name__ == '__main__':
    start_time = time.time()
    for maze_name in ('easy', 'medium', 'hard'):
        for param in ('optimize_ants', 'ant_count', 'Q', 'evaporation'):
            parameter_compare(maze_name, param, compute=True)

    print 'all done in %ds' % (int(time.time(), start_time))
