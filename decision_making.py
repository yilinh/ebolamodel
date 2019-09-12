# -*- coding: utf-8 -*-
"""
Created on Thu May 23 22:43:33 2019

@author: Emma
"""

### Decision-making functions ###
import random
from uncertainty_reduction import total_uncertainty

def policy_exploration_ratio(c1, c2, r1, r2, w, regions):
        
        uncertainty = total_uncertainty(regions)
        
        policy = min(max(w * abs((uncertainty-c1)/r1)**3 + (1-w) * abs((uncertainty-c2)/r2)**3,0),1)
        
        return policy

def explorative_decision(regions,x, surveillance_capacity, bed_capacity, chosen_regions):
    

        #assumption that you can send out max 3 surveillance teams at a time
        available_st = min(3, surveillance_capacity - surveillance_teams_in_use(regions,x))
        
        #Surveillance teams only have an effect on hidden regions. Check if there are still hidden regions
        still_hidden = False
        for region in regions:
            if region.hidden == True:
                still_hidden = True
        
        #if there is capacity and there are still hidden regions, we can employ surveillance teams
        if available_st and still_hidden:
            
            hidden_regions = []
            
            for region in regions:
                if region.hidden == True:
                    hidden_regions.append(region)
            
            #we use this list to keep track of where surveillance teams are sent
            selected_regions = []
            
            for i in range(min(len(hidden_regions),available_st)):
                different_region = False
                
                while different_region == False:
                    chosen_region = random.choice(hidden_regions)
                    if chosen_region.number not in selected_regions:
                        different_region = True
                        
                        chosen_region.surveillance_team(x)
                        selected_regions.append(chosen_region.number)
                        #print("A surveillance team has been deloyed to region", chosen_region.number)

            chosen_regions.append(stringifyer(selected_regions))
        
        
        #Else we can (further) reduce uncertainty using a small ETC
        else:
            options = []
            highest_uncertainty = 0

            #iterate over the regions, store the one with the highest uncertainty            
            for region in regions:

                uncertainty = region.uncertain_I.percentage + region.uncertain_bi.percentage
                if region.hidden == True:
                    #If a region is hidden, the uncertainty is 1.5 + 1.5 = 3
                    uncertainty = 3

                if uncertainty > highest_uncertainty:
                    highest_uncertainty = uncertainty
                    options = [region]
                elif uncertainty == highest_uncertainty:
                    options.append(region)

            #if there are multiple region with the same level of uncertainty, choose one at random            
            if len(options) != 1:
                    chosen_region = random.choice(options)
            else:
                    chosen_region = options[0]

            #print(resources_in_use(regions,x))

            #For now, we always place a small ETC because this gives the fastest reduction.
            #Uncertainty cannot be reduced below 0.2 so it makes no sense to do anything if you're already at that point
            if bed_capacity - resources_in_use(regions,x) >= 10 and highest_uncertainty > 0.2:
                chosen_region.placement_decision(x,10)
                chosen_regions.append(stringifyer([chosen_region.number]))
                #print("I'm making an explorative decision to place a small ETC in region ", chosen_region.number)
            else:
                chosen_regions.append(None)
                #print("I wanted to make an explorative decision but there was no capacity")
        
def exploitative_decision(regions,x, bed_capacity, chosen_regions):
        #beta_i*infected * (susceptible /(susceptible + infected) (for now we don't take into account the deceased/funerals)
         
  
            
        highest_infected = 0
        options = []
            
        for region in regions:
            
            if region.hidden == False:

                #we don't want to choose a region in which an ETC opens the this timestep
                if region.ETCs:
                    if region.ETCs[-1].timestep_opened == x:
                        continue
                        
                        
                #conservative choice: choose the region with the highest no of infections according to the lower bound
                #for the next timestep
                
                infected = region.uncertain_I.current_range[0] + region.uncertain_I.current_range[0] * region.uncertain_bi.variable_range[0] * (region.susceptible[0]  / (region.susceptible[0]  + region.uncertain_I.current_range[0]))

 
                if infected > highest_infected:
                    highest_infected = infected
                    options = [region]
                elif infected == highest_infected:
                    options.append(region)
        
        

        if not options:
            #all the regions are hidden. We do nothing
            chosen_regions.append(None)
            #print("I wanted to take an exploitative action but all the regions are hidden")
            
        else:
            if options:
                #if there are multiple regions with the same number of infected people, choose one at random
                if len(options) != 1:
                    chosen_region = random.choice(options)

                else:
                    chosen_region = options[0]


                #print(resources_in_use(regions,x))    
                if highest_infected >= 100:
                    if bed_capacity - resources_in_use(regions,x) >= 100:
                        chosen_region.placement_decision(x,100)
                        chosen_regions.append(str(chosen_region.number))
                    elif bed_capacity - resources_in_use(regions,x) >= 50:
                        chosen_region.placement_decision(x,50)
                        chosen_regions.append(str(chosen_region.number))
                        #print("I'm making an exploitaive decision to place a big ETC in region", chosen_region.number)
                    elif bed_capacity - resources_in_use(regions,x) >= 10:
                        chosen_region.placement_decision(x,10)
                        chosen_regions.append(str(chosen_region.number))
                    else:
                        chosen_regions.append(None)
                        #print("I wanted to place a big ETC but there was no capacity to do anything in region", chosen_region.number)

                elif highest_infected >= 50:
                    if bed_capacity - resources_in_use(regions,x) >= 50:
                        chosen_region.placement_decision(x,50)
                        chosen_regions.append(str(chosen_region.number))
                        #print("I'm making an exploitaive decision to place a big ETC in region", chosen_region.number)
                    elif bed_capacity - resources_in_use(regions,x) >= 10:
                        chosen_region.placement_decision(x,10)
                        chosen_regions.append(str(chosen_region.number))
                        #print("I wanted to place a big ETC but there was not enough capacity so I placed a small one in region", chosen_region.number)
                    else:
                        chosen_regions.append(None)
                        #print("I wanted to place a big ETC but there was no capacity to do anything in region", chosen_region.number)

                else:
                    #at a certain point you only might have 0.004 infected individuals, makes no sense to keep adding capacity at that point
                    if bed_capacity - resources_in_use(regions,x) >= 10 and highest_infected >= 1:
                        chosen_region.placement_decision(x,10)
                        chosen_regions.append(str(chosen_region.number))
                        #print("I'm making an exploitative decision to place a small ETC in region", chosen_region.number)
                    else:
                        chosen_regions.append(None)
                        #print("I wanted to place a small ETC but there was no capacity to do anything in region", chosen_region.number)

#in order to deal with the surveillance team picking multiple regions, where the first one COULD be region 0
#we add 10 to all region numbers and then stick them all in  string
def stringifyer(l):
    outputstring = ''
    for entry in l:
        outputstring = outputstring + str(entry+10)
    return outputstring                 
                
def check_for_removal(regions,timestep):
    for region in regions:
        #if there are fewer than 5 infected people in the region we assume "The worst is over"
        #and start handing over to locals
        
        #TO-DO: Now we're suddenly accessing a ground truth, DM can't do that!!!
        if region.infected[-1] < 5:
            for ETC in region.ETCs:
                #check if it's not already closed
                if ETC.timestep_closed == -1:
                    #check if it has been open for 2 weeks
                    #assumption: takes at least 2 weeks before local staff has been sufficiently trained
                    if timestep >= ETC.timestep_opened + 2:
                        #print("I am removing (a) ETC(s) in region", region.number)
                        ETC.close_ETC(timestep)

                        
def check_surveillance_removal(regions,timestep):
    for region in regions:
        if region.ST:
            if region.ST.timestep_placed + 1 == timestep:
                region.ST.close_ST(timestep)
                
                
### Function to calculate the total amount of resources currently deployed ###

def resources_in_use(regions, timestep):
    beds_in_use = 0
    for region in regions:
        for ETC in region.ETCs:
            if ETC.timestep_closed == -1 or not timestep >= ETC.timestep_closed:
                #even if the ETC is not open yet, it is assumed those resources are occupied.
                #the only time the resources are no longer occupied is when the ETC is shut down.
                beds_in_use += ETC.capacity
                
    return beds_in_use

def surveillance_teams_in_use(regions,timestep):
    st_in_use = 0
    for region in regions:
        if region.ST:
            if region.ST.timestep_closed == -1:
                st_in_use += 1
                
    return st_in_use