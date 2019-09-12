# -*- coding: utf-8 -*-
"""
Created on Thu May 23 22:41:09 2019

@author: Emma
"""

### THIS IS THE COMPARTMENTAL MODEL ###

from utility import get_neighbours

#### COMPARTMENTAL MODEL CONSTANTS ###
fat_without = 0.31 #proportion of people dying without treatment
t_fat_without = 2.5 #time in weeks until death without treatment
t_rec_without = 2.85 #time in weeks until recovery without treatment
    
fat_with = 0.24 #proportion of people dying with treatment
t_fat_with = 2.5 #time in weeks until death with treatment
t_rec_with = 2.37 #time in weeks until recovery with treatment
safe_b_rate =0.64 #proportion of burials that are conducted safely
    
beta_d = 0.73

compartments = 6 #no. of compartments in the model
i_index = 1 #when listing the compartments, where the infected compartent is (starting from 0)
 

def calc_population(y,t, regions, travel_rate):
    
    dydt = []
    
    regions_list = [i for i in range(len(regions))]
    
    #we have a long list of regions, loop over them 
    for i in range(0,len(regions)):
    
        #here we grab the compartments for every region
        susceptible, infected, recovered, deceased, funeral, treated = y[i*compartments:i*compartments+compartments]
        
        #and get the (number of) neighbours
        neighbouring_regions = get_neighbours(i,regions_list)
        no_neighbours = len(neighbouring_regions)
        
        neighbours = 0;
        
        #how many infected individuals there are in the neighbouring regions
        for j in range(0,len(neighbouring_regions)):
            region = neighbouring_regions[j]
            
            no_region_neighbours = len(get_neighbours(region,regions_list))
            
            #not all travelling people will go to the one region, so divide by the number of neighbours
            neighbours += y[int(region*compartments+i_index)]/no_region_neighbours
            
        #grab the parameters from the region objects
        beta_i = regions[i].beta_i
        beta_d = regions[i].beta_d
        
        ETC_cap = regions[i].ETC_cap
        


        #update all the compartments of the region accordingly
        dsdt = f_dsdt(susceptible, infected, deceased, beta_i, beta_d)

        didt = f_didt(susceptible, infected, deceased, treated, neighbours, no_neighbours, beta_i, beta_d, travel_rate, ETC_cap)



        drdt = f_drdt(infected, treated)

        dddt = f_dddt(infected, deceased)
        dfdt = f_dfdt(deceased, treated)
            
        dtrdt = f_dtrdt(infected, treated, ETC_cap)
        #print(dtrdt)
        
        #and append the outcomes to the list that the function will return
        dydt.extend([dsdt,didt,drdt,dddt,dfdt,dtrdt])
        

    

    return dydt


### Helper functions for the Compartmental Model ###

#change in susceptible people
def f_dsdt(susceptible, infected, deceased, beta_i, beta_d):
    return -(beta_i*infected + beta_d*deceased) * (susceptible /(susceptible + infected))

#change in recovered people
def f_drdt(infected, treated):
    return ((1-fat_without)*infected) / t_rec_without + (1-fat_with)*treated / t_rec_with

#change in infected people
#with travelling
def f_didt(susceptible, infected, deceased, treated, neighbours, no_neighbours, beta_i, beta_d, travel_rate, ETC_cap):
    if treated < ETC_cap:
        return ((beta_i*infected + beta_d*deceased) * (susceptible /(susceptible + infected))
                + travel_rate * neighbours
                - travel_rate * infected
            - ((1 - fat_without)*infected) / t_rec_without
           - fat_without*infected / t_fat_without
            - min(ETC_cap - treated, infected)/0.001) 
    else:
        return ((beta_i*infected + beta_d*deceased) * (susceptible /(susceptible + infected))
                + travel_rate * neighbours
                - travel_rate * infected
               - ((1-fat_without)*infected) / t_rec_without
               - fat_without*infected / t_fat_without)

#change in treated people
def f_dtrdt(infected, treated, ETC_cap):
    if treated < ETC_cap:
        return min(ETC_cap - treated, infected)/0.001 -(1-fat_with)*treated / t_rec_with - fat_with*treated / t_fat_with
    else:
        return -(1-fat_with)*treated / t_rec_with - fat_with*treated / t_fat_with

    
#change in deceased people
def f_dddt(infected, deceased):
    return (fat_without*infected) / t_fat_without - deceased * safe_b_rate

def f_dfdt(deceased, treated):
    return deceased * safe_b_rate + fat_with*treated / t_fat_with