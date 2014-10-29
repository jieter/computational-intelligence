# -*- coding: utf-8 -*-
"""
Created on Sun Oct 12 23:11:48 2014

@author: Daviid
"""
import pickle

with open('../assignment-3/data/hard-maze.txt.tsp-results.pickle') as f:
    results = pickle.load(f)
eind = 11
txtfile = open('steps.txt','w');

txtfile.write(str(int(results[0][eind]['length'])))
txtfile.write(";\n0,0;\n")
for i in range(0,(results[0][eind]['length'])):
    txtfile.write(str(int(results[0][eind]['trail'][i])))
    txtfile.write(";\n")
#14