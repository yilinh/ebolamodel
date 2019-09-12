# -*- coding: utf-8 -*-
"""
Created on Tue Jul 23 15:06:45 2019

@author: Emma

Creates the animation videos to study the behaviour of individual runs.
Run the ebola model with store_data = True

The resulting csv files are loaded by this script and used to generate the videos

See bottom of this script on how to concate these videos together in one.


"""

import numpy as np
import math
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from matplotlib import cm
import matplotlib as mpl
from matplotlib.colors import ListedColormap

import pandas as pd

def region_extraction(chosen_region, decision_type):
    l = []
    #the EMA results are a string, but if you save them in a pandas csv tey become floats
    #so cast them back into a string again!
    

    if math.isnan(chosen_region):
        return l
    else:
        chosen_region = str(int(chosen_region))
        if decision_type == 0:
            l.append(int(chosen_region))
            return l
        else:
            length = len(chosen_region)
            n = int(length / 2) #the length of the string divided by 2 is the no of regions chosen
            for i in range (0,n):
                r = chosen_region[2*i:2*i+2]
                l.append(int(r)-10)
            return l



def array_coord(region_no, grid_size):
    row = math.sqrt(grid_size)
    i = int(region_no/row)
    j = int(region_no % row)
    
    return i, j

from mpl_toolkits.axes_grid1 import make_axes_locatable

def colorbar(mappable):
    ax = mappable.axes
    fig = ax.figure
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    return fig.colorbar(mappable, cax=cax, ticks=[0,1])

#from model import ebola_model

outcomes = pd.read_csv('result_test.csv')

results = pd.read_csv('save_test.csv')

regions = [[0,1,2,3],
           [4,5,6,7],
           [8,9,10,11],
           [12,13,14,15]]

# Now we can do the plotting!
fig, ax = plt.subplots(1, figsize=(1, 1))


# Remove a bunch of stuff to make sure we only 'see' the actual imshow
# Stretch to fit the whole plane
#fig.subplots_adjust(0, 0, 1, 1)
# Remove bounding line

#ax.set_xticks(np.arange(data.shape[1]+1)-.5, minor=True)
#ax.set_yticks(np.arange(data.shape[0]+1)-.5, minor=True)


plt.xticks([-0.5, 0.5, 1.5, 2.5, 3.5])
plt.yticks([-0.5, 0.5, 1.5, 2.5, 3.5])

ax.grid(color="w", linestyle='-', linewidth=2)
#ax.axis("off")

## Remove ticks and labels
for axi in (ax.xaxis, ax.yaxis):
    for tic in axi.get_major_ticks():
        tic.tick1On = tic.tick2On = False
        tic.label1On = tic.label2On = False

text = regions
for i in range(4):
    for j in range(4):
        text[i][j] = ax.text(j, i, regions[i][j],
                       ha="center", va="center", color="w", fontsize="small") 

## DECISIONS OVER TIME ##
        
        
## DEFINE OUR OWN COLORMAP##
cmap = cm.Spectral
        
cmap2 = ListedColormap([cmap(0), cmap(0.1), cmap(0.2), cmap(0.3), cmap(0.4), 'w',
         cmap(0.6), cmap(0.7), cmap(0.8), cmap(0.9), cmap(0.99)])

a=np.full((4,4),0.5)
im = plt.imshow(a, cmap=cmap2, vmin=0, vmax=1)

ax.set_title("Decision Types Over Time", loc='center', fontsize=4, pad=2)


# ims is a list of lists, each row is a list of artists to draw in the
# current frame; here we are just animating one artist, the image, in
# each frame


ims = []


for i in range(27):
    if i > 0:
        #make a list of all the regions affected by decisions in timestep i
        l = region_extraction(outcomes['Chosen Regions'][i-1], outcomes['Decision Types'][i-1])
        for r in l:
            k,j = array_coord(r, 16)
            if outcomes['Decision Types'][i-1] == 0:
                if a[k][j] > 0.5:
                    a[k][j] = 0.5
                a[k][j] -= 0.1
            else:
                if a[k][j] < 0.5:
                    a[k][j] = 0.5
                a[k][j] += 0.1
     
    for edge, spine in ax.spines.items():
        spine.set_visible(False)
   
            
    im = ax.imshow(a, cmap=cmap2, vmin=0, vmax=1)
    


    
    #add_arts = [im, ]
    
    ims.append([im])






ani_decisions = animation.ArtistAnimation(fig, ims, interval=1000, blit=True)

ani_decisions.save('decisions.mp4', dpi=512)




## UNCERTAINTY ##

b =np.ones((4,4))

im2 = plt.imshow(b, cmap='binary', vmin=0, vmax=1)

ax.set_title("Uncertainty Over Time", loc='center', fontsize=4, pad=2)

ims2 = []


#for each timestep
for i in range(27):
    #for each region update the array
    for j in range(16):
        m,n = array_coord(j, 16)
        b[m][n] = (results['Uncertainty'][i+(j*27)])/3
            
    im2 = plt.imshow(b, cmap='binary', vmin=0, vmax=1)
    ims2.append([im2])

ani_uncertainty = animation.ArtistAnimation(fig, ims2, interval=1000, blit=False)

ani_uncertainty.save('uncertainty.mp4', dpi=512)

## ACTUAL CASES ##

c = np.zeros((4,4,))

max_cases = results['I'].max()

im3 = plt.imshow(c, cmap='gist_heat_r', vmin=0, vmax=max_cases)

ax.set_title("Actual Cases",  loc='center', fontsize=4, pad=2)

ims3 = []


for i in range(27):
    for j in range(16):
        m,n = array_coord(j,16)
        c[m][n] = (results['I'][i+(j*27)])
        
    im3 = plt.imshow(c, cmap='gist_heat_r', vmin=0, vmax=max_cases)
    ims3.append([im3])
    
ani_cases = animation.ArtistAnimation(fig, ims3, interval=1000, blit=False)

ani_cases.save('cases.mp4', dpi=512)


## OBSERVED CASES (MIN) ##

d = np.zeros((4,4,))

im4 = plt.imshow(d, cmap='gist_heat_r', vmin=0, vmax=max_cases)

ax.set_title("Observed Cases", loc='center', fontsize=4, pad=2)



ims4 = []

max_cases = results['I'].max()
for i in range(27):
    for j in range(16):
        m,n = array_coord(j,16)
        d[m][n] = (results['Observed I'][i+(j*27)])
        
    im4 = plt.imshow(d, cmap='gist_heat_r', vmin=0, vmax=max_cases)
    
    #ttl = plt.text(0.95, 0.95, i, horizontalalignment='right', verticalalignment='bottom', transform=ax.transAxes)
    
    ims4.append([im4])
    
    

    
ani_obs_cases = animation.ArtistAnimation(fig, ims4, interval=1000, blit=False)

ani_obs_cases.save('observed_cases.mp4', dpi=512)




'''' 
IDEA: Generate the "third" video here with the timer and the legends for
the other videos here. 
'''




fig = plt.figure(figsize=(1, 2))

ax1 = fig.add_axes([0.55, 0.60, 0.1, 0.30])
ax2 = fig.add_axes([0.05, 0.10, 0.1, 0.30])
ax3 = fig.add_axes([0.55, 0.10, 0.1, 0.30])



#FOR THE NUMBER OF CASES#
cmap = cm.gist_heat_r
norm = mpl.colors.Normalize(vmin=0, vmax=max_cases)

cb1 = mpl.colorbar.ColorbarBase(ax1, cmap=cmap,
                                norm=norm,
                                orientation='vertical',
                                ticks=[0,max_cases])
cb1.set_label('Number of Cases', fontsize=4, labelpad=-2)

cb1.ax.tick_params(pad=1) 

cb1.ax.set_yticklabels(['0', str(int(max_cases))], fontsize=4)


#FOR THE LEVEL OF UNCERTAINTY#

cmap = cm.binary
norm = mpl.colors.Normalize(vmin=0, vmax=100)

cb2 = mpl.colorbar.ColorbarBase(ax2, cmap=cmap,
                                norm=norm,
                                orientation='vertical',
                                ticks=[0,100])
cb2.set_label('% of Uncertainty', fontsize=4, labelpad=-8)

cb2.ax.tick_params(pad=1) 

cb2.ax.set_yticklabels(['0%', '100%'], fontsize=4)


# FOR THE DECISIONS #

cmap = cm.Spectral



from matplotlib.colors import ListedColormap


cmap2 = ListedColormap([cmap(0), cmap(0.1), cmap(0.2), cmap(0.3), cmap(0.4), 'w',
         cmap(0.6), cmap(0.7), cmap(0.8), cmap(0.9), cmap(0.99)])

norm = mpl.colors.Normalize(vmin=0, vmax=1)

cb3 = mpl.colorbar.ColorbarBase(ax3, cmap=cmap2,
                                norm=norm,
                                orientation='vertical',
                                ticks=[0.35,0.9])
cb3.set_label('Decision Type', fontsize=4)

cb3.ax.tick_params(pad=3, length=0) 

cb3.ax.set_yticklabels(['Exploitative', 'Explorative'], fontsize=3, rotation=90)

cb3.ax.plot([0,1], [0.45,0.45], 'black', linewidth=1)
cb3.ax.plot([0,1], [0.55,0.55], 'black', linewidth=1)


steps = []

plt.text(  # position text relative to Figure
    0.05, 0.75, 'Timestep:',
    ha='left', va='top',
    transform=fig.transFigure,
    fontsize=5
)

for i in range(27):
    ttl = plt.text(  # position text relative to Figure
            0.15, 0.70, i,
            ha='left', va='top',
            transform=fig.transFigure,
            fontsize=8
        )
     #ttl = plt.text(1.5, 0.75, i, horizontalalignment='right', verticalalignment='bottom', transform=ax.transAxes)
    steps.append([ttl])
     
ani_legend = animation.ArtistAnimation(fig, steps, interval=1000, blit=False)

ani_legend.save('legend.mp4', dpi=512)




''' 
HOW TO ADD ALL THESE IN ONE VIDEO: 

First the 4 plots:
    
In the directory, using command line:
    
    ffmpeg -i cases.mp4 -i observed_cases.mp4 -i uncertainty.mp4 -i decisions.mp4 -filter_complex "[0:v][1:v]hstack[top];[2:v][3:v]hstack[bottom];[top][bottom]vstack[out]" -map "[out]" out.mp4

which yields the out.mp4 video which is a square.
Now we want to append the legends to the right of this video.

    ffmpeg -i out.mp4 -i legend.mp4 -filter_complex hstack out2.mp4

Then out2.mp4 is your final video!
'''