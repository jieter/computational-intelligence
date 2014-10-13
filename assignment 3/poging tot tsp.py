from random import randrange
import numpy as np

noOfItems = 18      #Het aantal items in de maze

""" Bereken de afstanden tussen alle punten"""



"""Hier worden de oerouders willekeurig geinitialiseerd."""
getal = 0
noOfChroms = 200    #De grootte van de populatie
chromosomen = np.zeros((noOfChroms,noOfItems))  #Hierin komt de hele populatie
for N in range(0,noOfChroms):
    chromosoom = [randrange(1,(noOfItems + 1))]
    vol = 1
    while vol < noOfItems:
        getal = randrange(1,(noOfItems + 1))
        if getal not in chromosoom:
            chromosoom.append(getal)
            vol += 1
    chromosomen[N,:] = chromosoom


