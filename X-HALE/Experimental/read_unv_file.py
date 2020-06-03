# -*- coding: utf-8 -*-
"""
Created on Fri Apr 10 12:38:40 2020

@author: Bilal
"""


import numpy as np
import matplotlib.pyplot as plt
import pyuff
import os
import sys
import re
import cmath
from mpl_toolkits.mplot3d import axes3d, Axes3D
plt.close("all")

file_name = 'Out_time_mdof_complex_conf1.unv'
uff_file = pyuff.UFF(file_name)

types_of_sets = uff_file.get_set_types()

data = uff_file.read_sets()

# locations of accelerometers (or nodes)
coordinates = []
for sub in data: 
    if sub['type'] == 15: 

        coordinates = [sub['x'],sub['y'],sub['z']]
        break

# pick up node number ordering (accelerometer order)
node_number = []
for sub in data:
    if sub['type'] == 15:
        node_number = sub['node_nums']
        
# test accel locations by plotting
"""
fig = plt.figure(figsize=(16,9))
ax = fig.add_subplot(111, projection='3d')
ax.scatter(coordinates[0][0:26],coordinates[1][0:26],coordinates[2][0:26])
ax.set_ylim3d(-0.5,0.5)
ax.set_xlim3d(-2,2)
ax.set_zlim3d(-1,1)
ax.set_xlabel('Span [m]')
ax.set_ylabel('Chord [m]')
ax.set_zlabel('Vertical displacement [m]')
"""

# pick up local coordinate systems defined for accelerometers
CS_accel = []
for sub in data: 
    if sub['type'] == 2420: 
        CS_accel = sub['CS_matrices']
        break


# connection of nodes as defined in the test software
node_connection = []
for sub in data:
    if sub['type'] == 82:
        node_connection = sub['nodes']


# function to count number of frequencies stored in the universal file
def count_freq(x):
    count = 0
    for elem in x:
        if (elem == 55):
            count+=1
    return count

# initialize vectors of frequencies, mode shapes and damping
# mode shapes vector needs to be initialized
freq_gvt = []
damp_gvt =[]
mode_number = []
mode_shapes = []
node_number_eigenvector = []
# pick up frequencies, mode number and damping associated with each mode
for sub in data: 
    if sub['type'] == 55: 
        
        split_str = sub['id4'].split(',')
        mode_number.append(int(re.findall("\d+", split_str[0])[0]))
        freq_gvt.append(float(re.findall("\d+\.\d+", split_str[1])[0]))
        damp_gvt.append(float(re.findall("\d+\.\d+", split_str[2])[0]))
        mode_shapes.append([sub['r1'], sub['r2'], sub['r3']])
        node_number_eigenvector = sub['node_nums']
        
# check if the number of sensors providing data is fewer than the number 
# of sensors defined in geometry; a la some of the sensors were turned off
# during the test
if len(node_number) != len(node_number_eigenvector):
    cut_off = range(len(node_number_eigenvector))
else:
    cut_off = range(len(node_number))
# normalize eigenvector
mode_shapes_normalized = np.csingle(mode_shapes)
for i in range(len(mode_shapes_normalized)):
        mode_shapes_normalized[:][:][i] = np.divide(mode_shapes_normalized[:][:][i]\
        ,np.max(np.max(np.abs(mode_shapes_normalized[:][:][i]))))
#
    
# function to sort node displacements in eigenvector to the same order as 
# coordinates (or accelerometers) definition
def sort_mode_shapes(u_unsorted, grids, grids_order):

    # this function sorts a displacement field according
    # to a user-specified grid order
    # this function can be also used to extract a set of
    # ids from the total imported displacement field 

    # allocation

    u_sorted = np.csingle([np.zeros([3,len(grids_order)],dtype=np.complex) \
                           for i in range(len(u_unsorted))]) 

    # loop over the number of fields (e.g. mode shapes)
    for j in range(len(u_unsorted)):
        # loop over the grid ids in the desired order
        for i, grid in enumerate(grids_order):
            
            # finding position of current grid
            index = int(np.where(grids == int(grid))[0])
            print(index)
            # saving displacements
            u_sorted[j][:,i] = u_unsorted[j][:,index]
            
    return u_sorted

mode_shapes_sorted = sort_mode_shapes(mode_shapes_normalized, \
                                     node_number_eigenvector, node_number[cut_off])

# plotting
i=2
fig = plt.figure(figsize=(16,9))
ax = fig.add_subplot(111, projection='3d')
#ax.scatter(mode_shapes[0][0][:].real + coordinates[0][cut_off],\
#           mode_shapes[0][1][:].real + coordinates[1][cut_off],\
#           mode_shapes[0][2][:].real + coordinates[2][cut_off])
ax.scatter((np.abs(mode_shapes_sorted[0][0][:]) + coordinates[0][cut_off]),\
           (np.abs(mode_shapes_sorted[0][1][:]) + coordinates[1][cut_off]),\
           (np.abs(mode_shapes_sorted[0][2][:]) + coordinates[2][cut_off]))
ax.set_ylim3d(-0.5,0.5)
ax.set_xlim3d(-2,2)
ax.set_zlim3d(-1,1)
ax.set_xlabel('Span [m]')
ax.set_ylabel('Chord [m]')
ax.set_zlabel('Vertical displacement [m]')
plt.title('Mode number ' + str(i+1) + ' at frequency ' + str(freq_gvt[i]) + '' )
plt.show()