# -*- coding: utf-8 -*-
"""
Created on Thu May 23 22:38:39 2019

@author: Emma
"""

### THESE ARE ALL THE FUNCTIONS THAT CALCULATE THE SCORE ON THE OBJECTIVES]

def effectiveness(regions, compartments, no_response_results):
    deaths_prevented = 0
    total_no_response_deaths = 0
    
    for i in range(0,len(regions)):
        no_response_deaths = no_response_results[i*compartments+3] + no_response_results[i*compartments+4]
        response_deaths = regions[i].deceased[-1] + regions[i].funeral[-1]

        total_no_response_deaths += no_response_deaths
        
        #because the no response model does not incorporate random travelling, sometimes you have negative prevented deaths
        #We don't consider these in the prevented deaths
        if no_response_deaths - response_deaths > 0:
            deaths_prevented += no_response_deaths - response_deaths
    
    perc_deaths_prevented = (deaths_prevented) / total_no_response_deaths
    
    return perc_deaths_prevented


def efficiency(regions, compartments, no_response_results, timesteps):
    deaths_prevented = 0
    
    for i in range(0,len(regions)):
        no_response_deaths = no_response_results[i*compartments+3] + no_response_results[i*compartments+4]
        response_deaths = regions[i].deceased[-1] + regions[i].funeral[-1]
        
        #because the no response model does not incorporate random travelling, sometimes you have negative prevented deaths
        #We don't consider these in the prevented deaths
        if no_response_deaths - response_deaths > 0:
            deaths_prevented += no_response_deaths - response_deaths
    
    total_cost = 0
    for region in regions:
        for ETC in region.ETCs:
            total_cost += ETC.calc_cost(timesteps)
            
        if region.ST:
            total_cost += 1125 + 564
    
    if deaths_prevented == 0:
        return total_cost
    else:            
        return total_cost / deaths_prevented

def speed(regions,timesteps):
    for i in range (0,timesteps):
        total_T = 0
        total_I = 0
        for region in regions:
            total_T += region.treated[i]
            total_I += region.infected[i]
        
        if not (total_T + total_I) == 0:

            if total_T / (total_T + total_I) >= 0.7:
                return i
        
    return timesteps

def equity_demand(regions):
    
    met_demand =  []
    
    for region in regions:
        total_infected = region.infected[-1] + region.treated[-1] + region.deceased[-1] + region.funeral[-1] + region.recovered[-1]
        
        if total_infected > 0:
            cummulative_patients = region.cummulative_patients

            met_demand.append(cummulative_patients / total_infected)

        
    average = sum(met_demand) / len(met_demand)
    
    difference = 0
    
    for entry in met_demand:
        difference += (entry - average)**2
    
    #you want this to be as small as possible (because smallest differency -> highest equity)
    return difference


def equity_arrival(regions, timesteps):
    
    time_until_arrival = []
    
    for region in regions:
        
        first_infected = None
        for i in range(len(region.infected)):
            if region.infected[i] > 0:
                first_infected = i
                break
        
        #no infections means no demand
        if first_infected is not None:

            #if no ETCs were ever placed
            #now just the time until the simulation ends
            if not region.ETCs:

                time_until_arrival.append(timesteps - 1 - first_infected)
            else:  

                first_ETC = region.ETCs[0]
                first_help = first_ETC.timestep_opened
                time_until_arrival.append(first_help - first_infected)


    average = sum(time_until_arrival) / len(time_until_arrival)
    
    difference = 0
    
    for entry in time_until_arrival:
        difference += (entry - average)**2
    
    #you want this to be as small as possible (because smallest differency -> highest equity)
    return difference
 