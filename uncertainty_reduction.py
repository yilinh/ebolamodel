# -*- coding: utf-8 -*-
"""
Created on Thu May 23 22:52:10 2019

@author: Emma
"""

### Functions for the Uncertainty Reduction ###
import math

def total_uncertainty(regions):
    #when regions are hidden, uncertainty level is at 1.5 + 1.5 = 3
    max_uncertainty = len(regions) * 3
    
    current_uncertainty = 0
    
    for region in regions:
        current_uncertainty += region.uncertainty_level[-1]
    
    #return the percentage of uncertainty remaining in the system
    return current_uncertainty / max_uncertainty

def unc_infected(region, timestep):
    

    ETC_100 = [1.0, 0.95, 0.90, 0.85, 0.75, 0.7,0.5,0.325,0.25,0.225,0.21,0.2]
    ETC_50 = [1.0,0.95,0.85,0.7,0.5,0.325,0.25,0.225,0.21,0.2]
    ETC_10 = [1.0,0.95,0.7,0.55,0.45,0.375,0.325,0.30]

    perc_reduced = 1.0
    ETCs = region.ETCs
    for ETC in ETCs:
        if ETC.capacity == 50:
            weeks = timestep - ETC.timestep_placed
            
            if weeks >= len(ETC_50):
                percentage = ETC_50[-1]
            else:
                percentage = ETC_50[weeks]
                
            if perc_reduced > percentage:
                perc_reduced = percentage
         
        elif ETC.capacity == 100:
            weeks = timestep - ETC.timestep_placed
            
            if weeks >= len(ETC_100):
                percentage = ETC_100[-1]
            else:
                percentage = ETC_100[weeks]
                
            if perc_reduced > percentage:
                perc_reduced = percentage
            
        elif ETC.capacity == 10:
            weeks = timestep - ETC.timestep_placed
            
            if weeks >= len(ETC_10):
                percentage = ETC_10[-1]
            else:
                percentage = ETC_10[weeks]
                
            if perc_reduced > percentage:
                perc_reduced = percentage

    return perc_reduced
        

def unc_transmission(cumm_patients):
    if cumm_patients > 100:
        return 0
    else:
        return math.e**(-cumm_patients/15)