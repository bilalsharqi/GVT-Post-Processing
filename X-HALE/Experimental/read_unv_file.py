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
#file_name = 'OOP_inb_new_attach_0_30Hz_no euler.unv'
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
CS_labels = []
for sub in data: 
    if sub['type'] == 2420: 
        CS_accel = sub['CS_matrices']
        CS_labels = sub['CS_sys_labels']
        break
if CS_accel == []:
    print('No local coordinate systems found in the universal file')
else:
    print('Found local coordinate systems defined (thru rotation matrices)')
    print('Importing local coordinate systems and rotating the accel readings')


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
        
# convert list to np.array
mode_shapes = np.asarray(mode_shapes, dtype=np.complex64)

            

#if len(node_number) != len(node_number_eigenvector):
#    cut_off = range(len(node_number_eigenvector))
#else:
#    cut_off = range(len(node_number))
  
# check if the number of sensors providing data is fewer than the number 
# of sensors defined in geometry; a la some of the sensors were turned off
# during the test  
# delete any node locations that do not correspond to sensor data
int_2_remove = []
node_number.astype(int)
node_number_eigenvector.astype(int)
for node in range(len(node_number)):
#    print(node)
#    print(node_number[node])
    if node_number[node] not in node_number_eigenvector:
#        print('delete is happening')
#        np.delete(node_number, node)
        int_2_remove.append(node)
node_number = np.delete(node_number, int_2_remove)  
for i in range(len(coordinates)):
    coordinates[i] = np.delete(coordinates[i], int_2_remove)     
# have not modified anything after this
    
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
            
            # saving displacements
            u_sorted[j][:,i] = u_unsorted[j][:,index]
            
    return u_sorted

# sort mode shapes according to sensor data order in unv file
mode_shapes_sorted = sort_mode_shapes(mode_shapes, \
                     node_number_eigenvector, node_number)

# bring the deformations in the local coordinate systems 
mode_shapes_rotated = np.zeros_like(mode_shapes_sorted)
# check if rotation matrices are defined, if yes, rotate the readings
if CS_accel != []:
#    mode_shapes_rotated = mode_shapes_sorted
    for i in range(len(freq_gvt)):
        for j in range(len(node_number_eigenvector)):
            mode_shapes_rotated[i,:,j] = (mode_shapes_sorted[i,:,j]).dot(CS_accel[j])
# if not, the data is already in the global coordinate system
else:
    mode_shapes_rotated = mode_shapes_sorted
            
# normalize eigenvector to have highest value as 1
mode_shapes_normalized = np.csingle(mode_shapes_rotated)
for i in range(len(mode_shapes_normalized)):
        mode_shapes_normalized[:][:][i] = np.divide(mode_shapes_normalized[:][:][i]\
        ,np.max(np.max(np.abs(mode_shapes_normalized[:][:][i]))))

evec_gvt = mode_shapes_normalized.imag + \
          [coordinates[0][:], coordinates[1][:], coordinates[2][:]]
          
## plotting
for i in reversed(range(0, len(freq_gvt))):
    fig = plt.figure(figsize=(16,9))
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(coordinates[0][:],\
                coordinates[1][:],\
                coordinates[2][:], c='g', marker='*')
    ax.scatter(evec_gvt[i][0][:], evec_gvt[i][1][:], evec_gvt[i][2][:])
    ax.set_ylim3d(-3.5,3.5)
    ax.set_xlim3d(-.5,1.0)
    ax.set_zlim3d(-1,2)
    ax.set_xlabel('x [m]')
    ax.set_ylabel('y [m]')
    ax.set_zlabel('Vertical displacement [m]')
    plt.title('Mode number ' + str(i+1) + ' at frequency ' + str(freq_gvt[i]) + '' )
    plt.show()
    
    line_matrix = [] # this matrix contains cartesian vectors for lines connecting the points
    line_matrix_2 = []
    for line in range(0,len(node_connection)-1):
        node_1 = node_connection[line]
#        print('node_1')
#        print(node_1)
        node_2 = node_connection[line+1]
#        print('node_2')
#        print(node_2)
        if int(node_1)>=len(node_number_eigenvector):
            line_matrix_2 = []
        elif node_1==0:
            line_matrix_2 = []
        else:
            line_matrix_2.append(evec_gvt[i][:,int(node_1)])
        # This puts the lines from a portion of deformations together then
        # when a zero is encountered at node_1, plots them
        if node_1 == 0:
            
            # Plots each segment of the aircraft defined in LMS
            x_tmp = [x[0] for x in line_matrix]
#            print('x_tmp')
#            print(x_tmp)
            y_tmp = [x[1] for x in line_matrix]
#            print('y_tmp')
#            print(y_tmp)
            z_tmp = [x[2] for x in line_matrix]
#            print('z_tmp')
#            print(z_tmp)
            ax.plot3D(np.asarray(x_tmp).flatten(), np.asarray(y_tmp).flatten(), np.asarray(z_tmp).flatten(), 'black')
            
            # This happens at the end of node_connection
            if (node_1 == 0) & (node_2 == 0):
                # Plots the last segment of aircraft, useless for now
                x_tmp = [x[0] for x in line_matrix]
                y_tmp = [x[1] for x in line_matrix]
                z_tmp = [x[2] for x in line_matrix]
                ax.plot3D(np.asarray(x_tmp).flatten(), np.asarray(y_tmp).flatten(), np.asarray(z_tmp).flatten(), 'black')
#                break
            line_matrix = []
                                      
        # when node_1 is not 0
        # because accel 23 was removed from the node_number and any 
        # other data source (only for this test), shift the index
        # for reading and assigning displacement values
#        elif int(node_1)>len(node_number_eigenvector):
#            line_matrix.append([0,0,0])
        elif int(node_1)>22:
            line_matrix.append(evec_gvt[i][:,int(node_1)-2])
        else: 
            line_matrix.append(evec_gvt[i][:,int(node_1)-1])
          
# for a in range(len(evec_gvt)):
#     # a = 6 # Test mode number
#     plt.figure()
#     # plt.plot(evec_gvt[a][1][:], evec_gvt[a][2][:],'k*',label='Z translation')
#     plt.plot(coordinates[1],mode_shapes_normalized[a][2][:],'k*',label='Z translation') 
#     # plt.plot(mode_shapes_sorted[a][1][:], mode_shapes_normalized[a][2][:],'k*',label='Z translation')
#     current_frequency = str(freq_gvt[a]) #which frequency is this really
#     plt.title('Mode number '+ str(a+1) +' at a frequency of '+ current_frequency)
#     plt.xlabel('Length [m]')
#     plt.ylabel('Normalized Displacement')
#     plt.legend()


#currently need to compare mode 7 and 8 in experimental