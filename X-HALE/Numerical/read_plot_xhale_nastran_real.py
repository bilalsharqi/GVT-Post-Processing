# -*- coding: utf-8 -*-
"""
Created on Mon Dec 23 10:13:33 2019

@author: Bilal
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Nov 15 17:14:09 2019

@author: Bilal
"""

import numpy as np
import os
import scipy.io as sio
import shutil
import sys
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d, Axes3D
#from MTK.MTK import EigenPair, ModeSet, PlotReal,TrackModes
#os.system('cls' if os.name == 'nt' else 'clear')
plt.close("all")

def importGridIDs(file_path):
    
    # this function imports the model grids from a Nastran BDF

    print("Importing grids...")

    # allocation 

    grids = []

    # checking that file exists

    if not os.path.isfile(file_path):

        print("\nError in importGridIDs: file not found!")
        sys.exit()

    # reading input file

    with open(file_path,'r') as open_file:

        lines = open_file.readlines()

    open_file.close()

    # looking for GRID entries  

    for line in lines:

        # formatted or comma-separated format

        if line.startswith('GRID'):

            # formatted short or long

            if line[4] == ' ' or line[4] == '*':
                
                grid = line.split()[1]

                if grid[0] == "*":

                    grid = grid[1:]

            # comma-separated

            elif line[4] == ',':

                grid = line.split(',')[1]

            else:

                print("\nError in importGridIDs: invalid GRID format!")
                sys.exit()

            # storing GRID ID
            
            grids.append(int(grid))

    return grids, len(grids)

# original function by BF, modified by BS to read multiple subcases
def importGridDispl(file_path, n_grids, grids, grids_order=[]):
    
    print('importing displacement fields...')
    
    # Initialize the output idsplacement fields
    u = [np.zeros([6,n_grids]) for i in range(n_subcases)]
    
    # Exit if file not found
    if not os.path.isfile(file_path):
        print('\nError in importGridDisp: file not found')
        sys.exit()
    
    # Initialize file object for reading
    fp = open(file_path,'r')
    
    cnt = 0
    for count, line in enumerate(fp):
        
        if 'D I S P L A C E M E N T   V E C T O R'  in line:
            
            # skip lines to get to start of data
            for i in range(2):
                
                fp.readline()
            
            # initialize unsorted displacement field
            u_unsorted = np.zeros([6,n_grids])
            
            # loop through all the grid points
            for j in range(n_grids):
                
                # Split line into multiple parts
                line_split = fp.readline().split()
                
                # get grid number
                grid = line_split[0]
                
                # find grid number in grids
                index = np.where(grids == int(grid))
                
                # loop over all 6 degrees of freedom
                for k in range(6):
#                    
                    # get the displacement value
                    u_unsorted[k,index] = line_split[k+2]
            # check grid ordering        
            if grids_order == []:
                
                # use unsorted displacement fields
                u_sorted = u_unsorted
                
            else:
                
                # sort the grids
                u_sorted = sortGridDispl(u_unsorted, grids, grids_order)
            
            # assign displacement field to output
            u[cnt] = u_sorted
            
            # incrememnt index on output vector
            cnt += 1
    
    return u

def sortGridDispl(u_unsorted, grids, grids_order):

    # this function sorts a displacement field according
    # to a user-specified grid order
    # this function can be also used to extract a set of
    # ids from the total imported displacement field 

    # allocation

    u_sorted = np.zeros([len(grids_order),3])

    # loop over the grid ids in the desired order

    for i, grid in enumerate(grids_order):

        # finding position of current grid

        index = grids.index(int(grid))

        # saving displacements

        u_sorted[:,i] = u_unsorted[:,index]

    return u_sorted

def importGridCoords(file_path, n_grids, grids):

    # this function imports grid coordinates in the 
    # Nastran global coordinate system from a SOL103
    # ALTER output (DMIG format)
    
    grids = list(grids)

    print("Importing grids coordinates...")

    # allocation

    x = np.zeros([3,n_grids])

    # checking that file exists

    if not os.path.isfile(file_path):

        print("\nError in importGridCoords: file not found!")
        sys.exit()

    # reading file

    with open(file_path,'r') as open_file:

        lines = open_file.readlines()

    open_file.close()

    # extracting grid coordinates

    for line in lines:

        if line.startswith('*'):

            line_split = line.split()

            grid = line_split[1]
            comp = line_split[2][0]

            if '-' in line_split[2]:

                value = line_split[2][1:].replace('D','e')

            else:

                value = line_split[3].replace('D','e')

            x[int(comp)-1,grids.index(int(grid))] = value

    return x

# original importFrequencies function by riceroni
# modification to read multiple subcases by BS
def importFrequencies(file_path, n_modes,n_subcases):

    # this function imports the modal frequencies from a 
    # MSC Nastran SOL103 f06 output

    print("Importing frequencies...")

    # allocation
    
    freq = list(range(n_subcases))

    for i in range(0,n_subcases):

        freq[i] = np.zeros([n_modes])

    # checking that file exists

    if not os.path.isfile(file_path):

        print("\nError in importFrequencies: file not found!")
        sys.exit()

    # importing frequencies

    open_file = open(file_path,'r') 
    while not 'R E A L   E I G E N V A L U E S' in open_file.readline():

        pass

    for n in range(0,n_subcases):
        while not 'RADIANS' in open_file.readline():
            pass
        f=np.zeros(n_modes)
        for i in range(0,1):
    
            line = open_file.readline()
    
        for i in range(0,n_modes):
    
            line_split = open_file.readline().split()
            f[i] = line_split[4]
    
#            for j in range(0,n_subcases):
#                freq[j,index] = line_split[j+2]
        freq[n] = f
    

    open_file.close()

    return freq


# original importEigenvectors function by riceroni
# modification to read multiple subcases by BF and BS
def importEigenvectors(file_path, n_fields, n_grids, grids,n_subcases,grids_order=[]):

    # this function imports a set of eigenvectors 
    # from a MSC Nastran f06 output (e.g. SOL103) and in
    # case the user supplies a desired output order does
    # a rearrangement of the values for different grids
    # if no output order is supplied then the values for
    # different grids are returned in the order as from
    # the MSC Nastran output file (ascending order based
    # on grid IDs)

    print("Importing eigenvectors...")

    # allocation

#    phi = list((range(n_fields),n_subcases))
    phi = [[np.zeros([6,n_grids]) for i in range(n_fields)] for j in range(n_subcases)]


    if not os.path.isfile(file_path):

        print("\nError in importEigenvectors: file not found!")
        sys.exit()

    # importing eigenvectors

    fp = open(file_path,'r') 
    cnt1 = 0 #  number of eigvectors
    cnt2 = 0 # number of subcases
    for count, line in enumerate(fp):
#        for cnt2 in range(0,n_subcases):
#            for cnt1 in range(0,n_fields):
                if 'R E A L   E I G E N V E C T O R   N O .'  in line:

                    # skip lines to get to start of data
                    for i in range(2):
                        
                        fp.readline()
                    
                    # initialize unsorted displacement field
                    u = np.zeros([6,n_grids])
                    
                    # loop through all the grid points
                    for j in range(n_grids):
                        
                        # Split line into multiple parts
                        line_split = fp.readline().split()
#                        print(line_split)
                        # get grid number
                        grid = line_split[0]
                        
                        # find grid number in grids
                        index = np.where(grids == int(grid))
                       
                        # loop over all 6 degrees of freedom
                        for k in range(6):
        #                    
                            # get the displacement value
                            u[k,index] = line_split[k+2]
                            
                    # assign displacement field to output
                    phi[cnt2][cnt1] = u
                    
                    # incrememnt index on output vector
                    cnt1+=1
                    if cnt1 == n_fields:
                        cnt1=0
                        cnt2+=1
#                    if cnt2 == n_subcases:
#                        cnt2=0
#                    print("cnt1 = "+ str(cnt1))
#                    print("cnt2 = "+ str(cnt2))
    return phi

file_path=".f06"
file_coords=".txt"
n_fields=25
n_subcases=1
grids1=importGridIDs('.bdf')
n_grids=grids1[1]
grids=np.array(grids1[0])
grid_coord_NASTRAN = importGridCoords(file_coords, n_grids, grids)
freq_NASTRAN = importFrequencies(file_path, n_fields,n_subcases)
mode_shapes_NASTRAN = importEigenvectors(file_path, n_fields, n_grids, grids, n_subcases,[])
static_deform= importGridDispl(file_path, n_grids, grids)
testlist = [[np.zeros([6,n_grids]) for i in range(n_subcases)] for j in range(n_fields)]

# sample loads, need to be defined in the Nastran subcases for static loading
#Loads=[[0,	0.000],
#       [0.001,	0.0098],
#       [0.01,	0.0981],
#       [0.02,	0.1962],
#       [0.03,	0.2943],
#       [0.04,	0.3924],
#       [0.05,	0.4905],
#       [0.06,	0.5886],
#       [0.07,	0.6867],
#       [0.08,	0.7848],
#       [0.09,	0.8829],
#       [0.1,	0.981],
#       [0.11,	1.079],
#       [0.12,	1.177],
#       [0.13,	1.275],
#       [0.14,	1.373],
#       [0.15,	1.472],
#       [0.16,	1.570],
#       [0.17,	1.668],
#       [0.18,	1.766],
#       [0.19,	1.864],
#       [0.2,	1.962],
#       [0.21,	2.060],
#       [0.22,	2.158],
#       [0.23,	2.256],
#       [0.24,	2.354],
#       [0.25,	2.453],
#       [0.26,	2.551],
#       [0.27,	2.649],
#       [0.28,	2.747],
#       [0.29,  2.845],
#       [0.3,	2.943],
#       [0.31,	3.041],
#       [0.32,	3.139],
#       [0.33,	3.237],
#       [0.34,	3.335],
#       [0.35,	3.434],
#       [0.36,	3.532],
#       [0.37,	3.630],
#       [0.38,	3.728],
#       [0.39,	3.826],
#       [0.4,	3.924],
#       [0.5,	4.905],
#       [0.6,	5.886],
#       [0.7,	6.867],
#       [0.8,	7.848],
#       [0.9,	8.829],
#       [1,	9.810]]



#================================================================================
# Reshape matrix of NASTRAN mode shapes 
#================================================================================
#mode_shapes_NASTRAN_reshape = np.empty([n_subcases,n_fields, n_grids, 6]) 
#
#for k in range(0, n_subcases):
#    for n in range(0, n_fields):
#        for i in range(0, n_grids):
#            for j in range(0, 6):
#                mode_shapes_NASTRAN_reshape[n][k][i][j] = mode_shapes_NASTRAN[k][n][i][j]


#================================================================================
# Save data in a .mat file, if want to use matlab for analysis/plotting
#================================================================================
#print("...Exporting results in a .mat file")
#dir=os.path.dirname(os.path.abspath("load_save_modes_mat.py"))
#path = os.path.join(dir, "NASTRAN_mode_shapes_out.mat")
#database = {}
##
### Write problem data
#database["n_fields"] = n_fields
#database["n_grids"] = n_grids
#database["grid_coords"] = grid_coord_NASTRAN
##
### Write mode shapes
##
## Write frequencies 
#database["freq_NASTRAN_out"] = freq_NASTRAN
## Write loads
#database["Loads"] = Loads
#
## Writing database
#if os.path.isfile(path):
#    os.remove(path)
#sio.savemat(path,database,appendmat=False)


#================================================================================
# Termination message
#================================================================================
#
print("\nNASTRAN data import completed")
##
#
#max_static_deform=np.zeros(48) # change this according to the model size
#for i in range(0,n_subcases):
#    max_static_deform[i]=max(abs((static_deform[i][2,:])))+max(static_deform[i][2,:])
#    
#msd_semi_span=max_static_deform/(6/2)*100
#    
print("MODE SHAPE PLOTTING")
print("OOP Bending mode shapes")
i=6 # Test mode number
plt.figure()
plt.plot(grid_coord_NASTRAN[1,:],mode_shapes_NASTRAN[0][i][2][:],'k*',label='Z translation')
plt.title('Mode number ' + str(i) + ' at frequency ' + str(freq_NASTRAN[0][i]) + '' )
plt.xlabel('Length [m]')
plt.ylabel('Normalized Displacement')
plt.legend()

print("IP and torsional components")    
plt.figure()
i=8 # Test mode number
#plt.plot(grid_coord_NASTRAN[0,:],mode_shapes_NASTRAN[0][i][1][:],'r*',label='In-Plane component')
plt.plot(grid_coord_NASTRAN[1,:],mode_shapes_NASTRAN[0][i][4][:],'b*',label='Rotation about y')
plt.title('Mode number ' + str(i) + ' at frequency ' + str(freq_NASTRAN[0][i]) + '' )
plt.legend()


print("MODE SHAPE PLOTTING")
print("Translational data only")
fig = plt.figure(figsize=(16,9))
ax = fig.add_subplot(111, projection='3d')
i=10
# Plot a basic scatter plot with translational eigenvectors 
# plotted on top of the grid coordinates
ax.scatter(grid_coord_NASTRAN[0,:] + mode_shapes_NASTRAN[0][i][0], \
           grid_coord_NASTRAN[1,:] + mode_shapes_NASTRAN[0][i][1], \
           grid_coord_NASTRAN[2,:] + mode_shapes_NASTRAN[0][i][2])
# the second scatter plot contains rotational data, which is not
# necessarily needed to visualize rotations
#ax.scatter(grid_coord_NASTRAN[0,:]+mode_shapes_NASTRAN[0][i][3], \
#           grid_coord_NASTRAN[1,:]+mode_shapes_NASTRAN[0][i][4], \
#           grid_coord_NASTRAN[2,:]+mode_shapes_NASTRAN[0][i][5])

ax.set_ylim3d(-3,3)
ax.set_zlim3d(-1.5,1.5)
ax.set_xlabel('Chord [m]')
ax.set_ylabel('Span [m]')
ax.set_zlabel('Vertical displacement [m]')
plt.title('Mode number ' + str(i) + ' at frequency ' + str(freq_NASTRAN[0][i]) + '' )
plt.show()


# Plot a basic scatter plot with static displacement 
# plotted on top of the grid coordinates
print("STATIC DISPLACEMENT")
print("Translational data only")
fig = plt.figure(figsize=(16,9))
ax = fig.add_subplot(111, projection='3d')
i=0
ax.scatter(grid_coord_NASTRAN[0,:] + static_deform[i][0][:], \
           grid_coord_NASTRAN[1,:] + static_deform[i][1][:], \
           grid_coord_NASTRAN[2,:] + static_deform[i][2][:])
plt.title('Static Displacement' )
#ax.set_xlim3d(-1,1.5)
ax.set_ylim3d(-3,3)
ax.set_zlim3d(-1.5,1.5)
ax.set_xlabel('Chord [m]')
ax.set_ylabel('Span [m]')
ax.set_zlabel('Vetical displacement [m]')
#ax.invert_xaxis()
plt.show()


# Plot a basic scatter plot with translational eigenvectors 
# plotted on top of the grid coordinates which have the initial deformation
# coming from the static displacement accounted for
print("MODE SHAPE PLOTTING")
print("Deformed jig + Translational data only")
fig = plt.figure(figsize=(16,9))
ax = fig.add_subplot(111, projection='3d')
i=10 # test mode shape number
# deformed mode shapes (initial grid coordinates + static displacement + modal displacements)
ax.scatter(grid_coord_NASTRAN[0,:] + mode_shapes_NASTRAN[0][i][0] +  static_deform[0][0], \
           grid_coord_NASTRAN[1,:] + mode_shapes_NASTRAN[0][i][1] +  static_deform[0][1], \
           grid_coord_NASTRAN[2,:] + mode_shapes_NASTRAN[0][i][2] +  static_deform[0][2])
# static displacement (initial grid coordinates + static displacement)
ax.scatter(grid_coord_NASTRAN[0,:] + static_deform[0][0][:], \
           grid_coord_NASTRAN[1,:] + static_deform[0][1][:], \
           grid_coord_NASTRAN[2,:] + static_deform[0][2][:])
# undeformed mode shapes (initial grid coordinates + modal displacements)
ax.scatter(grid_coord_NASTRAN[0,:] + mode_shapes_NASTRAN[0][i][0], \
           grid_coord_NASTRAN[1,:] + mode_shapes_NASTRAN[0][i][1], \
           grid_coord_NASTRAN[2,:] + mode_shapes_NASTRAN[0][i][2])
ax.set_ylim3d(-3,3)
ax.set_zlim3d(-1.5,1.5)
ax.set_xlabel('Chord [m]')
ax.set_ylabel('Span [m]')
ax.set_zlabel('Vertical displacement [m]')
#ax.invert_xaxis()
plt.title('Deformed Mode number ' + str(i) + ' at frequency ' + str(freq_NASTRAN[0][i]) + '' )
plt.show()


print("STATIC DISPLACEMENT")
print("OOP Z only")
i=6 # Test mode number
plt.figure()
plt.plot(grid_coord_NASTRAN[1,:]+static_deform[0][1][:], grid_coord_NASTRAN[2,:]+ static_deform[0][2][:],'k*',label='Z translation')
plt.title('Static Displacement in Z' )
plt.xlabel('Length [m]')
plt.ylabel('Normalized Displacement')
plt.axis('equal')
plt.legend()
   
# does not contain MTK capability of function calls


