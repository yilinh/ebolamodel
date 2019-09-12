# -*- coding: utf-8 -*-
"""
Created on Thu May 23 22:21:29 2019

@author: Emma
"""

from scipy.integrate import odeint
import numpy as np
import random
import pandas as pd
import datetime

import objective_functions
from compartmental_model import calc_population
import decision_making
from utility import random_travelling
import uncertainty_reduction

from objects import  Region



    
compartments = 6 #no. of compartments in the model
i_index = 1 #when listing the compartments, where the infected compartent is (starting from 0)
    
#THE GRID HAS TO BE SQUARE 
no_regions = 16
regions_list = [i for i in range(no_regions)] #list of the regions

### REGION POPULATION ###
region_population = [345474, 303272, 204686, 204686,
              615376, 303272, 531435, 506100,
              1055964, 444270, 318588, 575478,
              200781, 346461, 609893, 526379]
    
    
### RESOURCES AVAILABLE ###
surveillance_capacity = 6 #Assumption, takes +5 weeks to search all regions
bed_capacity = 900   #From WHO DATA
    
    
### TIMESTEPS ###
timesteps = 26



def ebola_model(I4 =3,
                I14 = 25,
                I15 = 32,
                beta_i = 0.32,
                beta_d = 0.73,
                travel_rate = 0.05,
                exploration_ratio = 0.5,
                store_data = False):
    
    
    #Time vector to feed into odeint, one timestep each iteration
    time_vec = np.linspace(0,1,2)
     
    #Setting up all the region objects      
    regions = []
    
    #setting up the model outcome of uncertainty over time
    uncertainty_over_time = []
    
    #setting up the model outcomes for allocation decisions over time
    decisions_over_time = []
    chosen_regions = []
    
    
    for entry in regions_list:
        if entry == 4:
            region = Region(entry, region_population[entry], I4, 0, (I4/4), 0, 0, beta_i, beta_d)
        elif entry == 14:
            region = Region(entry, region_population[entry], I14, 0, (I14/4), 0, 0, beta_i, beta_d)
        elif entry == 15:
            region = Region(entry, region_population[entry], I15, 0, (I15/4), 0, 0, beta_i, beta_d)
        else:
            region = Region(entry, region_population[entry], 0, 0, 0, 0, 0, beta_i, beta_d)
            
        regions.append(region)
    

    
    y0 = []
    
    for region in regions:
        y0.extend([region.susceptible[0], region.infected[0], region.recovered[0], region.deceased[0], region.funeral[0], region.treated[0]])

        
    no_response_t = np.linspace(0, timesteps, timesteps)
    no_response_population = odeint(calc_population, y0, t=no_response_t, args=(regions, travel_rate))
    
    pd.DataFrame(no_response_population).to_csv("no_response_data.csv")
    
    no_response_results = no_response_population[-1]
    
    
    for x in range (0,timesteps):
        
        #print("Timestep ", x)
        
        for region in regions:
            
            #in some "hidden" regions, the # of patients may be so high we hear about it spontaneously
            if region.hidden == True:
                region.spontaneous_news()
            
            #update uncertainties
            if region.uncertain_I.percentage > uncertainty_reduction.unc_infected(region,x):
                region.uncertain_I.reduce_uncertainty(uncertainty_reduction.unc_infected(region, x))
                
            if region.uncertain_bi.percentage > uncertainty_reduction.unc_transmission(region.cummulative_patients_prev):
                region.uncertain_bi.reduce_uncertainty(uncertainty_reduction.unc_transmission(region.cummulative_patients_prev))
        
        #right here you have the level of uncertainty experienced by the decision maker when they make a decision
        #store that as an outcome
        uncertainty_over_time.append(uncertainty_reduction.total_uncertainty(regions))
        
        #make decisions
        decision_type  = random.uniform(0,1)
        
        if decision_type < exploration_ratio:
            
            #take an explorative action
            decisions_over_time.append(1)
            decision_making.explorative_decision(regions,x, surveillance_capacity, bed_capacity, chosen_regions)

        else:
            #take an exploitative action
            decisions_over_time.append(0)
            decision_making.exploitative_decision(regions,x, bed_capacity, chosen_regions)

        
        #See if any resources can be freed for the next timestep:
        
        #check if any ETCs can be closed down
        decision_making.check_for_removal(regions,x)
        
        #check if any surveillance teams are "done"
        decision_making.check_surveillance_removal(regions,x)
        
        #update the ETC capacity of each region
        for region in regions:
            region.calculate_capacity(x, regions)
            
        
        #Run the compartmental model for 1 timestep                                                                                  
        population = odeint(calc_population, y0, t=time_vec, args=(regions, travel_rate))
        
        #random travelling takes place here. The function returns the new list of the population, regardless of whether random travel occured
        y0 = random_travelling(regions, population.T[:,1], compartments, i_index)

        
        #store the results and update the region objects
        for i in range(0,len(regions)):
            regions[i].update(y0[i*compartments:i*compartments+compartments])
            regions[i].update_cummulative_patients()

        
    objective_1 = -objective_functions.effectiveness(regions, compartments, no_response_results)
    objective_2 = objective_functions.speed(regions,timesteps)
    objective_3 = objective_functions.equity_demand(regions)
    objective_4 = objective_functions.equity_arrival(regions,timesteps)
    objective_5 = objective_functions.efficiency(regions, compartments, no_response_results, timesteps)
    results = {'Effectiveness': objective_1, 
               'Time until Containment': objective_2, 
               'Difference in Met Demand': objective_3, 
               'Difference in Arrival Time': objective_4, 
               'Cost per Death Prevented': objective_5, 
               'Uncertainty over Time': uncertainty_over_time, 
               'Decision Types': decisions_over_time, 
               'Chosen Regions': chosen_regions}
    
    if store_data:
        df = pd.DataFrame()
        
        for region in regions:
            data = pd.DataFrame({'S': region.susceptible, 
                                 'I': region.infected,
                                 'R': region.recovered,
                                 'D': region.deceased,
                                 'F': region.funeral,
                                 'T': region.treated,
                                 'Uncertainty': region.uncertainty_level,
                                 'Observed I': region.observed_infected,
                                 'Capacity': region.capacity_over_time})
    
            df = df.append(data)
            
        #file_name = datetime.datetime.now() 
        df.to_csv('save_test.csv')
        
        df2 = pd.DataFrame(results)
        df2.to_csv('result_test.csv')
    
    return results
