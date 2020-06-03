import numpy as np
import os
import scipy.io as sio
import shutil
import sys
import matplotlib.pyplot as plt

plt.close("all")

num_file = 'beam_num_data_out.mat'
exp_file = 'beam_exp_data.mat'

exp_data = sio.loadmat(exp_file)
num_data = sio.loadmat(num_file)

# identify grid coordinates in the numerical analysis corresponding to
# accelerometer locations

exp_coordinates_x_adjusted = exp_data['exp_coordinates'][0] + 1.83
grids_uni_le_te = [0,31,61,92,122,153,183,214,244,275,305,336,366]

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

mode_shapes_reduced = num_data['num_mode_shapes']
#grids_uni_le_te.astype(int)
#num_data['grids'].astype(int)
for mode in range(len(num_data['num_mode_shapes'])):
    
    for dof in range(0,6):
        int_2_remove = []
        for node in range(len(num_data['grids'][0])):
        #    print(node)
        #    print(node_number[node])
            if num_data['grids'][0][node] not in grids_uni_le_te:
        #        print('delete is happening')
        #        np.delete(node_number, node)
                int_2_remove.append(node)
        mode_shapes_reduced[mode][dof] = np.delete(mode_shapes_reduced[mode][dof], int_2_remove)  
  
# have not modified anything after this
    mode_test = np.delete(mode_shapes_reduced[mode][dof], np.asarray(int_2_remove))  