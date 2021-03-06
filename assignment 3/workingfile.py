from random import randrange
import numpy as np
import matplotlib.pyplot as plt
import pickle

with open('../assignment-3/data/hard-maze.txt.tsp-results.pickle') as f:
    results = pickle.load(f)

noOfItems = 18      #Het aantal items in de maze
noOfChroms = 200

""" Bereken de afstanden tussen alle punten.
De nulde rij representeerd de afstand van het begin tot het eind en tot de items.
Dus Afstand[0,0] is afstand van beginpunt tot eindpunt. Afstand[0,5] is afstand 
van beginpunt tot item 5 en Afstand[3,0] is afstand van item 3 tot eindpunt """

Afstand = np.zeros(((noOfItems+1),(noOfItems+1)))
for row in range(len(Afstand)):
    for col in range(len(Afstand[row])):
        Afstand[row,col] = randrange(1,1001) 
        """CalcDist(row,col)"""


"""Hier worden de oerouders willekeurig geinitialiseerd."""
getal = 0
    
chromosomen = np.zeros((noOfChroms,noOfItems))  #Hierin komt de hele populatie
for N in range(0,noOfChroms):
    chromosoom = []
    vol = 0
    while vol < noOfItems:
        getal = randrange(1,(noOfItems + 1))
        if getal not in chromosoom:
            chromosoom.append(getal)
            vol += 1
    chromosomen[N,:] = chromosoom
average = []
minima = []
    
"""Hier wordt berekend wat de totale afstand is bij de verschillende chromosomen"""  
def calcFitness(matr):   
    fitness = []
    gesorteerd = 0
    for row in range(0,(len(matr))):
        totaal = results[0][int(matr[row,0])]['length'];
        for col in range(0,len(matr[N])-1):
            totaal += results[int(matr[row,col])][int(matr[row,(col + 1)])]['length']
        totaal += results[int(matr[row,(len(matr[N])-1)])][len(results)-1]['length'];
        fitness.append(totaal)
    gesorteerd = sorted(fitness)
    average.append(sum(gesorteerd)/float(len(gesorteerd)))
    minima.append(min(gesorteerd))
    plaats = []
    toppers = np.zeros((10,(len(matr[N,:]))))
    for i in range(0,10):
        plaats = (fitness.index(gesorteerd[i]))
        toppers[i,:] = matr[plaats,:]
    return toppers, fitness
    

"""Nu is het tijd voor de selectie van de fitste chromosomen en evolutie"""
def calcNewFamily(matr):
    kinderen = np.zeros((noOfChroms,noOfItems))
    kindnr = 0
    toppers = np.zeros((10,len(matr[N,:])))
    toppers, fitness = calcFitness(matr)
    for i in range(0,len(toppers)):
        for j in range(0,len(toppers)):
            place1 = randrange(0,(len(toppers[i,:])-1))
            place2 = randrange(place1,len(toppers[i,:]))
            if(i == j):
                deel = toppers[i,place1:place2]
                invdeel = []
                for k in reversed(deel):
                    invdeel.append(k)
                kinderen[kindnr,0:place1] = toppers[i,0:place1]
                kinderen[kindnr,place1:place2] = invdeel
                kinderen[kindnr,place2:(len(toppers[i,:]))] = toppers[i,place2:(len(toppers[i,:]))]
                kindnr += 1
                
                kinderen[kindnr,:] = toppers[i,:]
                kindnr += 1
            else:  
                deel1 = toppers[i,place1:place2]
                deel2 = toppers[j,place1:place2]
                kinderen[kindnr,place1:place2] = deel2
                kinderen[(kindnr + 1),place1:place2] = deel1
                rest = []
                for gene in toppers[i,:]:
                    if (gene not in kinderen[kindnr,:]):
                        rest.append(gene)
                kinderen[kindnr,0:place1] = rest[0:place1]
                kinderen[kindnr,place2:len(kinderen[kindnr])] = rest[place1:len(rest)]
                
                rest = []
                for gene in toppers[j,:]:
                    if (gene not in kinderen[kindnr + 1,:]):
                        rest.append(gene)
                kinderen[(kindnr + 1),0:place1] = rest[0:place1]
                kinderen[(kindnr + 1),place2:len(kinderen[(kindnr + 1)])] = rest[place1:len(rest)]
                kindnr += 2
    return kinderen, fitness

new, fitness = calcNewFamily(chromosomen)
xas = [0]
for a in range(1,100):
    xas.append(a)
    new, fitness = calcNewFamily(new)


plt.plot(xas,average,'b',xas,minima,'r')
plt.show()

with open('chromosomen.pickle','wb') as handle:
    pickle.dump(new,handle)

winnaar = new[fitness.index(min(fitness)),:]

steps = []
#results[0][int(winnaar[0])]['trail']
for gen in range(0,len(winnaar)-1):
    steps.append(results[int(winnaar[gen])][int(winnaar[(gen + 1)])]['trail'])
steps.append(results[int(winnaar[(len(winnaar)-1)])][(len(results)-1)]['trail'])

txtfile = open('steps.txt','w');

txtfile.write(str(int(min(fitness))))
txtfile.write(";\n")
txtfile.write("0, 0;\n")
#txtfile.write("take product #")
#txtfile.write(str(int(winnaar[0])))

for row in range(0,len(steps)):
    for col in range(0,len(steps[row])):
        txtfile.write(str(int(steps[row][col])))
        txtfile.write(";\n")
    #txtfile.write("take product #")
    #txtfile.write(str(int(winnaar[(row + 1)])))
    txtfile.write(";\n")

text_file = open('chromosomen.txt','w')
for row in range(0,len(new)):
    for col in range(0,len(new[row,:])):
        text_file.write(str(int(new[row,col])))
        text_file.write(", ")
    text_file.write("\n")
"""
txtfile.write(str(int(results[0][19]['length'])))
txtfile.write(";\n0,0;\n")
for stapje in range(0,len(results[0][19]['trail'])):
    txtfile.write(str(int(results[0][19]['trail'][stapje])))
    txtfile.write(";\n")
"""
