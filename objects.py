# -*- coding: utf-8 -*-
"""
Created on Thu May 23 22:53:41 2019

@author: Emma
"""

import random
import math

from utility import get_neighbours

class Uncertain_Constant:
    def __init__(self, ground_truth, variable_range):
        self.ground_truth = ground_truth
        self.variable_range = variable_range  #[value, value]
        self.original_range = variable_range
        self.percentage = 1.0
                
        
    def fuzzifier(self):
        
        if(self.percentage == 0):
            self.variable_range = [self.ground_truth, self.ground_truth]
        
        else:
            new_width = (self.original_range[1] - self.original_range[0]) * self.percentage
            
            in_current_range = False


            while in_current_range == False:
                z = new_width * random.uniform(0,1)
                new_range = [self.ground_truth - (new_width - z), self.ground_truth + z]


                if new_range[0] >= 0:
                    self.variable_range = new_range
                    in_current_range = True
                    
                
    def reduce_uncertainty(self, percentage):
        self.percentage = percentage
        self.fuzzifier()

        
        
class Uncertain_Variable:
    def __init__(self, ground_truth, variable_width):
        self.ground_truth = ground_truth
        self.variable_width = variable_width
        self.percentage = 1.0
        self.current_range = 0
        
        self.fuzzifier()
        
    def fuzzifier(self):
        
        if(self.percentage == 0):
            self.current_range = [self.ground_truth, self.ground_truth]
        
        else:
            new_range_width = self.variable_width * self.percentage * self.ground_truth
            valid_range = False
            while valid_range == False:
                z = new_range_width * random.uniform(0,1)
                new_range  = [self.ground_truth - (new_range_width - z), self.ground_truth + z]

                if new_range[0] >= 0:
                    self.current_range = new_range
                    valid_range = True
                    
                
    def reduce_uncertainty(self, percentage):
        self.percentage = percentage
        self.fuzzifier()
        
        
    def new_truth(self, ground_truth):
        self.ground_truth = ground_truth
        self.fuzzifier()
        


from compartmental_model import fat_with, t_fat_with, t_rec_with 
        
class Region:
    def __init__(self, number, susceptible, infected, recovered, deceased, funeral, treated, 
                 beta_i, beta_d):
        self.number = number
        self.susceptible = [susceptible]
        self.infected = [infected]
        self.observed_infected = [0]
        self.recovered = [recovered]
        self.deceased = [deceased]
        self.funeral = [funeral]
        self.treated = [treated]
        self.beta_i = beta_i
        self.beta_d = beta_d
        self.ETC_cap = 0
        #TO-DO: ranges are now hardcoded
        self.uncertain_I = Uncertain_Variable(infected, 2.5)
        self.uncertain_bi = Uncertain_Constant(beta_i, [0.1,0.5])
        
        self.uncertainty_level = [3]
        self.capacity_over_time = [0]
        
        self.ETCs = []
        self.cummulative_patients = 0
        #to model the time delay in uncertainty reduction, we need to also keep track of the cummulative number of patients one timestep back
        self.cummulative_patients_prev = 0
        
        ##Need to know when the ST comes in
        
        self.hidden = True
        self.ST = None
        
    
    def update(self,compartments_list):
        
        self.susceptible.append(compartments_list[0])
        self.infected.append(compartments_list[1])
        self.recovered.append(compartments_list[2])
        self.deceased.append(compartments_list[3])
        self.funeral.append(compartments_list[4])
        self.treated.append(compartments_list[5])
        
        if self.hidden == True:
            self.uncertainty_level.append(3)
            self.observed_infected.append(0)
        else:
            self.uncertainty_level.append(self.uncertain_I.percentage + self.uncertain_bi.percentage)
        
        self.capacity_over_time.append(self.ETC_cap)
        
        self.uncertain_I.new_truth(self.infected[-1])
        if self.hidden == False:
            self.observed_infected.append(self.uncertain_I.current_range[0])
        
        
        
    def placement_decision(self, timestep, capacity):
        if self.hidden == True:
            self.hidden = False
        self.ETCs.append(ETC(capacity,timestep))
        
    def surveillance_team(self, timestep):
        self.hidden = False
        self.ST = Surveillance_Team(timestep)
        
    def calculate_capacity(self, timestep, regions):
        regions_list = [i for i in range(len(regions))]
        
        for ETC in self.ETCs:
            if ETC.timestep_opened == timestep:
                self.ETC_cap += ETC.capacity
            
            #once an ETC is opened, uncertainty is also reduced in neighbouring regions. One week of information delay.
            if ETC.timestep_opened + 1 == timestep:
                #get all the neighbours
                neighbours = get_neighbours(self.number,regions_list)
                for neighbour in neighbours:
                    updateable_region = regions[int(neighbour)]
                    
                    if updateable_region.hidden == True:
                        updateable_region.hidden = False
                    
                    if updateable_region.uncertain_I.percentage > 0.95:
                        updateable_region.uncertain_I.percentage = 0.95 
                
                    if updateable_region.uncertain_bi.percentage > 0.95:
                        updateable_region.uncertain_bi.percentage = 0.95
                    
                
            
            '''
            #Remove this if you maintain (local) capacity even if resources are removed
            if ETC.timestep_closed == timestep:
                self.ETC_cap -= ETC.capacity
            '''
    
    def update_cummulative_patients(self):
        
        self.cummulative_patients_prev = self.cummulative_patients
        
        self.cummulative_patients += self.treated[-1] - (self.treated[-2] - (self.treated[-2]*fat_with/t_fat_with 
                                                                             + self.treated[-2]*(1-fat_with)/t_rec_with))
           
    def spontaneous_news(self):
        no_infected = self.infected[-1]
        
        if no_infected >= 5:
        
            p = 1-1/(1+math.e**((no_infected-40)/5))

            i  = random.uniform(0,1)

            if i <= p:
                self.hidden = False
                #print("Spontaneous news from region ", self.number)
        
        

class ETC:
    def __init__(self, capacity, timestep_placed):
        self.capacity = capacity
        self.timestep_placed = timestep_placed
        
        if(capacity == 10):
            self.timestep_opened = timestep_placed + 1
        if(capacity == 50):
            self.timestep_opened = timestep_placed + 3
        if(capacity == 100):
            self.timestep_opened = timestep_placed + 4
        
        self.timestep_closed = -1
    
    def close_ETC(self, timestep):
        if self.capacity == 10:
            self.timestep_closed = timestep + 1
        elif self.capacity == 50 or self.capacity == 100:
            self.timestep_closed = timestep + 2
            
    def calc_cost(self, timesteps):
        total_cost = 0
        
        
        if self.capacity == 10:
            #one-off cost for setting up
            total_cost += 77200
            
            if self.timestep_closed == -1:
                weeks_open = timesteps - 1 - self.timestep_opened
            else:
                weeks_open = self.timestep_closed - self.timestep_opened
                
            total_cost += weeks_open * (2200 + 1125 + 564)
            
        elif self.capacity == 50:
            total_cost += 386000
            
            if self.timestep_closed == -1:
                weeks_open = timesteps - 1 - self.timestep_opened
            else:
                weeks_open = self.timestep_closed - self.timestep_opened
                
            total_cost += weeks_open * (4405 + 1125 + 564)
            
        elif self.capacity == 100:
            total_cost += 694800
            
            if self.timestep_closed == -1:
                weeks_open = timesteps - 1 - self.timestep_opened
            else:
                weeks_open = self.timestep_closed - self.timestep_opened
                
            total_cost += weeks_open * (8810 + 1125 + 564)
            
        return total_cost
        
            

class Surveillance_Team:
    def __init__(self,timestep_placed):
        self.timestep_placed = timestep_placed
        self.timestep_closed = -1
        
    def close_ST(self,timestep):
        self.timestep_closed = timestep