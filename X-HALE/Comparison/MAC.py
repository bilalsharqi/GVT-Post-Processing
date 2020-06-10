import numpy as np
import os
import scipy.io as sio
import shutil
import sys
import matplotlib.pyplot as plt

plt.close("all")

#num_file = 'beam_num_data_out.mat'
#exp_file = 'beam_exp_data.mat'
num_file = 'NASTRAN_mode_shapes_out.mat'
exp_file = 'xhale_exp_data.mat'

exp_data = sio.loadmat(exp_file)
num_data = sio.loadmat(num_file)

# identify grid coordinates in the numerical analysis corresponding to
# accelerometer locations

exp_coordinates_x_adjusted = exp_data['exp_coordinates'][0] + 1.83
grids_uni_le_te = [0,31,61,92,122,153,183,214,244,275,305,336] #Problem grid index 366 DNE
freq_allowed = [0, 4, 9, 14, 24]

# ------Bilal hard coded the grids in this section to reflect the grids points used in experiment (try to code this differently) /T


# function to take selected node displacements in numerical eigenvectors
# These nodes are selected by the user to match accel locations 
#def reduced_mode_shapes(u_unsorted, grids, grids_order):
#
#    # this function sorts a displacement field according
#    # to a user-specified grid order
#    # this function can be also used to extract a set of
#    # ids from the total imported displacement field 
#
#    # allocation
#    u_reduced = ([np.zeros([6,len(grids_order)],dtype=np.float64) \
#                           for i in range(len(grids_order))]) 
#
#    # loop over the number of fields (e.g. mode shapes)
#    for j in range(len(u_unsorted)):
#        # loop over the grid ids in the desired order
#        for i, grid in enumerate(grids_order):
#            
#            # finding position of current grid
#            index = int(np.where(grids == int(grid))[0])
#            
#            # saving displacements
#            u_reduced[j][:,i] = u_unsorted[j][:,index]
#            
#    return u_reduced
#
## sort mode shapes according to sensor data order in unv file
#mode_shapes_reduced = reduced_mode_shapes(num_data['num_mode_shapes'], \
#                     num_data['grids'], grids_uni_le_te)

#u_reduced = ([np.zeros([6,len(grids_uni_le_te)],dtype=np.single) \
#                           for i in range(len(num_data['num_mode_shapes']))]) 
#index = int(np.where(num_data['grids'] == int(grid))[0])


# delete any node locations that do not correspond to sensor data

#mode_shapes_reduced = np.reshape(num_data['num_mode_shapes'][0][0], 25, 6, 348)  #need to reshape this matrix so isn't a single row vector
mode_shapes_reduced = num_data['num_mode_shapes'][0][0]

mode_shapes_reduced_part = np.transpose(num_data['num_mode_shapes'][0][1],(1,0))

mode_shapes_reduced_total = mode_shapes_reduced.transpose((2, 0, 1)) 
#this changes the original axis formation from axis 0 , 1, 2 to axis 2, 0, 1 via transpose function /T
#new dimensions are 384 sheets of 25 x 6 arrays matching the original Matlab Script and Format /T

#this adds the two cells together
for beta in range(len(mode_shapes_reduced_total)):  #so typically I would just modify mode_shapes_reduced_total but it is getting wonky for some reason  so i duplicated it for manipulation
   for charlie in range(len(mode_shapes_reduced_total[0])):
       mode_shapes_reduced_total[beta][charlie] = np.add(mode_shapes_reduced_total[beta][charlie] , mode_shapes_reduced_part[beta])




#mode_shapes_reduced =  mode_shapes_reduced.reshape((25, 6, 348)) #need to reshape this matrix so isn't a single row vector
#mode_shapes_reduced_test = mode_shapes_reduced[0,:,:]
mode_appended = []
# for freq2 in range(0,25):
#    for freq2 in range(0,6):
#        mode_appended = num_data['num_mode_shapes'][0][0]


#         -----set aside point to make add the two arrays together to avoid reference issues later /T
# len(num_data['num_mode_shapes']) = 1
#grids_uni_le_te.astype(int)
#num_data['grids'].astype(int)


#for charlie in range(0,1):
# focus --> remove grid location points first (reduce from 348 sheets) then reduce frequencies from 25 to 12ish i think /T
int_2_remove = [] #presumably cycling through the 348 gridpoint /T
freq_2_remove = []
for gridpoint in range(len(mode_shapes_reduced_total)):  
    if gridpoint not in grids_uni_le_te:
        int_2_remove.append(gridpoint)
mode_shapes_reduced_total = np.delete(mode_shapes_reduced_total, int_2_remove,0)  #finish this later/T
for f in range(len(mode_shapes_reduced_total[0])): #cycles through 25 frequencies in numerical data/T
    #    print(node)
    #    print(node_number[node])
    if f not in freq_allowed:  
    #       number assignment
            freq_2_remove.append(f)  #-Problem int_2_remove is 348 long (removing all nodes??)
mode_shapes_reduced_total = np.delete(mode_shapes_reduced_total, freq_2_remove,axis = 1)  

# have not modified anything after this
  #  mode_test = np.delete(mode_shapes_reduced_total[mode][dof], np.asarray(int_2_remove))  

#function to compare experimental frequencies with numerical frequencies

#create frequency matrix
#for going through length of vector experimental 
    #for loop going through vector numerical 
        #version 1  = abs(numerical value - experimental value)/experimental
        #if index + 1 exist,
            #version 2 = abs((numerical value + 1 in index)  - experimental value)/experimental
            #else version 2 = 1;
        #if version1 is smaller than version 2 and within a 50% tolerance (I'm trying to prevent super small data)
            #append the index value to frequency array
            #else if version 2 < version 1
                #exit loop this inner loop
#def sortFrequencies (numericalData, experimentalData):
experimentalData = exp_data['exp_freq']
numericalData = num_data['freq_NASTRAN_out']
numericalData = np.delete(numericalData,[0,1,2],1)
freqIndicies = []
for exp in range(len(experimentalData[0])):
    for num in range(len(numericalData[0])):
        version1 = (abs(numericalData[0][num] - experimentalData[0][exp]))/(experimentalData[0][exp])
        if (num+1) < len(numericalData[0]):
            version2 = (abs(numericalData[0][num+1] - experimentalData[0][exp])/(experimentalData[0][exp]))
        else:
            version2 = 3
        if (version1 < version2) and (version1 < 0.25): #version less than 25%
            freqIndicies.append(num)
            break
#    return freqIndicies
#might try using three check version, the problem with this one is that if the 2nd entry after the search point is larger, then the code will not work  
