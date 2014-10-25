# -*- coding: utf-8 -*-
"""
Created on Sun Oct 12 23:11:48 2014

@author: Daviid
"""
import pickle

with open('../assignment 3/data/hard-maze.txt.tsp-results.pickle') as f:
    results = pickle.load(f)

txtfile = open('steps.txt','w');


txtfile.write(str(int(results[0][19]['length'])))
txtfile.write(";\n0,0;\n")
for stapje in range(0,len(results[0][19]['trail'])):
    txtfile.write(str(int(results[0][19]['trail'][stapje])))
    txtfile.write(";\n")
    