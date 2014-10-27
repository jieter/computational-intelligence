from random import randrange
from random import gauss
import numpy as np
import matplotlib.pyplot as plt
import pickle

with open('../assignment-3/data/hard-maze.txt.tsp-results.pickle') as f:
    results = pickle.load(f)

noOfItems = 18      #Het aantal items in de maze
noOfChroms = 200    #Het aantal in de populatie
stddeviation = 5
""" Bereken de afstanden tussen alle punten.
De nulde rij representeerd de afstand van het begin tot het eind en tot de items.
Dus Afstand[0,0] is afstand van beginpunt tot eindpunt. Afstand[0,5] is afstand 
van beginpunt tot item 5 en Afstand[3,0] is afstand van item 3 tot eindpunt """


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
            #Als het getal nog niet in het chromosoom zit, wordt deze toegevoegd.
            vol += 1 #Als deze het aantal items is, stopt deze iteratie.
    chromosomen[N,:] = chromosoom #het chromosoom wordt aan de populatie toegevoegd
average = []
minima = []


    
"""Hier wordt berekend wat de totale afstand is bij de verschillende chromosomen"""  
def calcFitness(matr):   
    fitness = []
    gesorteerd = 0
    for row in range(0,(len(matr))):
        totaal = results[0][int(matr[row,0])]['length']; #afstand van beginpunt tot eerste item
        for col in range(0,len(matr[N])-1):
            totaal += results[int(matr[row,col])][int(matr[row,(col + 1)])]['length']
            #De afstanden tussen de items in het chromosoom worden berekend
        totaal += results[int(matr[row,(len(matr[N])-1)])][len(results)-1]['length']
            #De afstand van het laatste item tot het eindpunt wordt toegevoegd.
        fitness.append(totaal) #Totale afstand wordt toegevoegd aan lijst.
    fitnesstosort = []
    for fthd in fitness:
        fitnesstosort.append(fthd)
    gesorteerd = sorted(fitness)
    sortedmatr = np.zeros((noOfChroms,noOfItems))
    for i in range(0,len(sortedmatr)):
        sortedmatr[i,:] = matr[fitnesstosort.index(gesorteerd[i]),:]
        fitnesstosort[fitnesstosort.index(gesorteerd[i])] = 0
    average.append(int(sum(fitness)/float(len(fitness))))
    minima.append(min(fitness))
    
    return sortedmatr, fitness
    

"""Nu is het tijd voor de selectie van de fitste chromosomen en evolutie"""
def calcNewFamily(matr):
    kinderen = np.zeros((noOfChroms,noOfItems))
    kindnr = 0 #initialiseert op welke plaats in de populatie de kinderen terechtkomen
    gesorteerd, fitness = calcFitness(matr)
    while kindnr < 200:
            keus1 = (int(abs(gauss(0,stddeviation)) + 0.5))
            keus2 = (int(abs(gauss(0,stddeviation)) + 0.5))
            place1 = randrange(0,(len(gesorteerd[keus1,:])-1))
            place2 = randrange((place1+1),len(gesorteerd[keus1,:]))
            if kindnr >= 150:
                deel = gesorteerd[keus1,place1:place2]
                invdeel = []
                for k in reversed(deel):
                    invdeel.append(k)
                kinderen[kindnr,0:place1] = gesorteerd[kindnr,0:place1]
                kinderen[kindnr,place1:place2] = invdeel
                kinderen[kindnr,place2:(len(gesorteerd[kindnr,:]))] = gesorteerd[keus1,place2:(len(gesorteerd[kindnr,:]))]
                kindnr += 1
                
            else:
                deel1 = gesorteerd[keus1,place1:place2]
                deel2 = gesorteerd[keus2,place1:place2]
                kind1 = np.zeros((1,18))
                kind2 = np.zeros((1,18))
                kind1[0,place1:place2] = deel2
                kind2[0,place1:place2] = deel1
                rest = []
                for gene in gesorteerd[keus1,:]:
                    if (gene not in kind1):
                        rest.append(gene)
                kind1[0,0:place1] = rest[0:place1]
                """ print("heeeeee")
                print(len(kinderen[kindnr]))
                print(len(rest))
                print(rest)
                print(kinderen[kindnr])
                print((len(rest)-place1)-(len(kinderen[kindnr])-place2))"""
                kind1[0,place2:len(kinderen[kindnr])] = rest[place1:len(rest)]
                
                rest = []
                for gene in gesorteerd[keus2,:]:
                    if (gene not in kind2):
                        rest.append(gene)
                kind2[0,0:place1] = rest[0:place1]
                kind2[0,place2:len(kinderen[kindnr+1])] = rest[place1:len(rest)]
                kinderen[kindnr,:] = kind1
                kinderen[(kindnr+1),:] = kind2
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
    pickle.dump(chromosomen,handle)

winnaar = new[fitness.index(min(fitness)),:]

steps = []
#steps.append(results[0][int(winnaar[0])]['trail'])
for gen in range(0,len(winnaar)-1):
    steps.append(results[int(winnaar[gen])][int(winnaar[(gen + 1)])]['trail'])
steps.append(results[int(winnaar[(len(winnaar)-1)])][(len(results)-1)]['trail'])

txtfile = open('steps.txt','w');

txtfile.write(str(int(min(fitness) - results[0][int(winnaar[0])]['length'])))
#This is the amount of steps taken
txtfile.write(";\n")
txtfile.write("0, 19;\n") #Starting position


for row in range(0,len(steps)): #for the paths between different items
    for col in range(0,len(steps[row])): #for every step of these paths
        txtfile.write(str(int(steps[row][col]))) #write the step
        txtfile.write(";\n") #close line and start a new one.
    

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
