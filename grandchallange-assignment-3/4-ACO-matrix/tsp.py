#!/usr/bin/env python

from random import randrange, shuffle
import pickle
import matplotlib.pyplot as plt

from util import mean

with open('../data/gc-maze.txt.tsp-results.pickle') as f:
    results = pickle.load(f)

# settings
noOfItems = len(results) - 2      # Het aantal items in de maze
noOfChroms = 200
startlocation = (0, 0)
write_startlocation = True

INFINITY = 999999

average = []
minima = []


def path_length(a, b):
    try:
        return results[a][b]['length']
    except KeyError:
        # print 'length not found for path %d -> %d, returning %d' % (a, b, INFINITY)
        return INFINITY


def path_trail(a, b):
    return results[a][b]['trail']


def fitness(chromosoom):
    # paarsgewijs vergelijken start + locaties + einde voor totale padlengte
    ret = 0
    location_list = [0, ] + chromosoom + [len(results) - 1, ]
    for i, j in zip(location_list, location_list[1:]):
        ret += path_length(i, j)
    return ret


def calcFitness(population, topper_count=10):
    '''
    Bereken de fitness voor de hele populatie en selecteer een aantal toppers
    '''
    population_with_fitness = []
    fitness_list = []

    for solution in population:
        fit = fitness(solution)
        population_with_fitness.append((fit, solution))
        fitness_list.append(fit)

    average.append(mean(fitness_list))
    minima.append(min(fitness_list))

    # sort the population by reversed fitness and get the first `topper_count`
    sorted_list = sorted(population_with_fitness, key=lambda x: x[0])
    toppers = [f[1] for f in sorted_list[0:topper_count]]

    return toppers, fitness_list


def select_best(population):
    toppers, _ = calcFitness(new_generation)
    return toppers[1]


def calcNewFamily(population):
    '''
    Genereer een nieuwe generatie
    '''
    kinderen = [[]] * noOfChroms
    kindnr = 0

    topper_count = 10
    toppers, _ = calcFitness(population, topper_count=topper_count)

    for i in range(topper_count):
        for j in range(topper_count):

            place1 = randrange(0, len(toppers[i]) - 1)
            place2 = randrange(place1, len(toppers[i]))

            if (i == j):
                deel = toppers[i][place1:place2]
                invdeel = []
                for k in reversed(deel):
                    invdeel.append(k)
                kinderen[kindnr][0:place1] = toppers[i][0:place1]
                kinderen[kindnr][place1:place2] = invdeel
                kinderen[kindnr][place2:(len(toppers[i]))] = toppers[i][place2:(len(toppers[i]))]
                kindnr += 1

                kinderen[kindnr] = toppers[i]
                kindnr += 1
            else:
                deel1 = toppers[i][place1:place2]
                deel2 = toppers[j][place1:place2]
                kinderen[kindnr][place1:place2] = deel2
                kinderen[(kindnr + 1)][place1:place2] = deel1
                rest = []
                for gene in toppers[i]:
                    if (gene not in kinderen[kindnr]):
                        rest.append(gene)
                kinderen[kindnr][0:place1] = rest[0:place1]
                kinderen[kindnr][place2:len(kinderen[kindnr])] = rest[place1:len(rest)]

                rest = []
                for gene in toppers[j]:
                    if (gene not in kinderen[kindnr + 1]):
                        rest.append(gene)
                kinderen[(kindnr + 1)][0:place1] = rest[0:place1]
                kinderen[(kindnr + 1)][place2:len(kinderen[(kindnr + 1)])] = rest[place1:len(rest)]
                kindnr += 2
    return kinderen


def trail_string(a, b):
    return ';'.join(map(str, path_trail(a, b))) + ';'


def write_solution(solution, filename='output/05_actions_TSP.txt'):
    print 'Writing to %s...' % filename
    FORMAT = 'take product #%d;'

    steps = []
    step_list = [(0, solution[0])] + zip(solution, solution[1:])
    for i, (a, b) in enumerate(step_list):
        steps.append(trail_string(a, b))
        steps.append(FORMAT % solution[i])

    steps.append(trail_string(solution[-1], len(results) - 1))

    with open(filename, 'w') as txtfile:
        # lengte totale route:
        txtfile.write('%d;\n' % (fitness(solution) + noOfItems))
        if write_startlocation:
            txtfile.write("%d, %d;\n" % startlocation)

        txtfile.write('\n'.join(steps))

        txtfile.write('\n')


def make_plot(xas):
    plt.plot(xas, average, 'b', label='average')
    plt.plot(xas, minima, 'r', label='minimum')

    plt.ylabel('fitness')
    plt.title('Evolution TSP, fitness over the generations')
    plt.ylim([0, max(average)])
    plt.xlabel('Generations')
    plt.legend()

    plt.savefig('output/TSP-evolution.eps')
    plt.savefig('output/TSP-evolution.png')

    # plt.show()




if __name__ == '__main__':

    iterations = 100
    generations = 500
    outcomes = []
    for i in range(iterations):
        chromosomen = []
        locations = range(1, noOfItems + 1)
        for N in range(noOfChroms):
            shuffle(locations)
            chromosomen.append(list(locations))

        # first
        new_generation = calcNewFamily(chromosomen)

        for a in range(1, generations):
            new_generation = calcNewFamily(new_generation)

        winner = select_best(new_generation)

        outcomes.append(fitness(winner))
        print 'finished try', i

    from pylab import figure, boxplot, title, xticks, ylim, xlabel, ylabel
    import matplotlib.pyplot as plt

    figure()
    boxplot([outcomes])
    ylabel('Fitness after %d generations' % generations)
    title('spreiding TSP (%d iterations)' % iterations)

    plt.savefig('spreiding-tsp.png')
    plt.savefig('spreiding-tsp.eps')


    # print 'Initialise initial population of %d chromosomen' % noOfChroms
    # chromosomen = []
    # locations = range(1, noOfItems + 1)
    # for N in range(noOfChroms):
    #     shuffle(locations)
    #     chromosomen.append(list(locations))
    # new_generation = calcNewFamily(chromosomen)
    # xas = [0]
    # for a in range(1, 500):
    #     xas.append(a)
    #     new_generation = calcNewFamily(new_generation)

    # # plotje
    # make_plot(xas)
    # winner = select_best(new_generation)
    # print 'Beste oplossing uit deze populatie'
    # print fitness(winner), winner

    # write_solution(winner)


