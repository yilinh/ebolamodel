# -*- coding: utf-8 -*-
"""
Created on Thu May 23 22:45:36 2019

@author: Emma
"""


### UTILITY FUNCTIONS ####

import math

def get_neighbours(i,square_list):
    l = len(square_list)
    row = math.sqrt(l)

    if(i < row):
            #this is the top row

        if(i == 0):
            #it's the first entry of the row
            neighbours = [i+1,i+row]
        elif(i == row-1):
            #it's the last entry of the row
            neighbours = [i-1,i+row]
        else:
            neighbours = [i-1, i+1, i+row]
            
    elif(i > l-1-row):
            #this is the bottom row

        if(i == l-row):
            #it's the first entry of the row
            neighbours = [i+1, i-row]
        elif (i == l-1):
            #it's the last entry of the row
            neighbours = [i-1, i-row]
        else:
            neighbours = [i-1, i+1, i-row]

    else:
            #it's a middle row 

        if (i % row == 0):    
            #it's the first entry of a row
            neighbours = [i+1, i-row, i+row]
        elif (i % row == (row-1)):
            #it's the last entry of a row
            neighbours = [i-1, i-row, i+row]
        else:
            #it's a "middle" entry
            neighbours = [i-1,i+1,i-row,i+row]
    
    return neighbours
        
import random

def random_travelling(regions, population, compartments, i_index):
    
    population = population 
    
    total_infected = 0
    
    regions_list = [i for i in range(len(regions))]

    #there needs to be at least one region with at least one person for this to work
    at_least_one = False
    
    for i in range(0,len(regions)):
        total_infected += population[i*compartments+i_index]
        if population[i*compartments+i_index] >= 1:
            at_least_one = True

    if at_least_one == False:
        return population
    
    #the "probability" of having one or more random travellers is dependent on the number of infected people
    p = total_infected*0.005
    
    #print(total_infected,p)
    
    #if p > 1 then we have at least 1 traveller
    travellers = int(p)
    
    #if there are more than the int travelers is determined with some probability
    if p > 1:
        if p - travellers > random.uniform(0,1):
            travellers += 1
    else:
        if p > random.uniform(0,1):
            travellers += 1
    
    #now every traveller needs to travel
    for i in range(travellers):
    
        #for every traveller we need to have a region of departure. There need to be infected people in this region
        infected_region = False
        while infected_region == False:
            random_departure_region = random.choice(regions)
            if population[random_departure_region.number*compartments+i_index] >= 1:
                infected_region = True
                
        neighbouring_regions = get_neighbours(random_departure_region.number,regions_list)
        
        #the destination region needs to be a non-neighbouring region (And also not the region of departure)
        suitable_destination = False
        while suitable_destination == False:
            random_destination = random.choice(regions)
            if random_destination.number != random_departure_region.number and not random_destination.number in neighbouring_regions:
                suitable_destination = True
                    
        #print("A person is moving from region ", random_departure_region.number)
        #print("to region ", random_destination.number)
        #remove the person from the region of origin and add them to the destination
        population[(random_departure_region.number)*compartments+i_index] -= 1
        population[(random_destination.number)*compartments+i_index] += 1
        
    
    return population