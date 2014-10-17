from random import randrange
import numpy as np
import matplotlib.pyplot as plt

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
        totaal = 0
        for col in range(0,len(matr[N])-1):
            totaal += Afstand[matr[row,col],matr[row,(col + 1)]]
        fitness.append(totaal)
    gesorteerd = sorted(fitness)
    average.append(sum(gesorteerd)/float(len(gesorteerd)))
    minima.append(min(gesorteerd))
    plaats = []
    toppers = np.zeros((10,(len(matr[N,:]))))
    for i in range(0,10):
        plaats = (fitness.index(gesorteerd[i]))
        toppers[i,:] = matr[plaats,:]
    return toppers
    

"""Nu is het tijd voor de selectie van de fitste chromosomen en evolutie"""
def calcNewFamily(matr):
    kinderen = np.zeros((noOfChroms,noOfItems))
    kindnr = 0
    toppers = np.zeros((10,len(matr[N,:])))
    toppers = calcFitness(matr)
    for i in range(0,len(toppers)):
        for j in range(0,len(toppers)):
            place1 = randrange(0,(len(toppers[i,:])-1))
            place2 = randrange(place1,len(toppers[i,:]))
            if(i == j):
                place1 = randrange(0,(len(toppers[i,:])-1))
                place2 = randrange(place1,len(toppers[i,:]))
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
    return(kinderen)

new = calcNewFamily(chromosomen)
xas = [0]
for a in range(1,101):
    new = calcNewFamily(new)
    xas.append(a)
print(average)
print(minima)

plt.plot(xas,average,'b',xas,minima,'r')
plt.show()
             
