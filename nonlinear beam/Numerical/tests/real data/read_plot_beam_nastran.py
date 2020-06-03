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
from MTK.MTK import EigenPair, ModeSet, TrackModes
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
                        
                        # get grid number
                        grid = line_split[0]
                        
                        # find grid number in grids
                        index = np.where(grids == int(grid))
                        
                        # loop over all 6 degrees of freedom
                        for k in range(6):
        #                    
                            # get the displacement value
                            u[k,index] = line_split[k+2]
#                            print(u[k,index])
#                            print(line_split[k+2])
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


file_path="beam_model_sol400_out.f06"
file_coords="sol400_coor.txt"
n_fields=25
n_grids=367
n_subcases=48
grids1=importGridIDs('beam_model.bdf')
grids=np.linspace(1,367,367)
#g = list(range(1,367))
grid_coord_NASTRAN = importGridCoords(file_coords, n_grids, grids)
freq_NASTRAN = importFrequencies(file_path, n_fields,n_subcases)
mode_shapes_NASTRAN = importEigenvectors(file_path, n_fields, n_grids, grids,n_subcases,[])
static_deform= importGridDispl(file_path, n_grids, grids)
testlist = [[np.zeros([6,n_grids]) for i in range(n_subcases)] for j in range(n_fields)]
Loads=[[0,	0.000],
       [0.001,	0.0098],
       [0.01,	0.0981],
       [0.02,	0.1962],
       [0.03,	0.2943],
       [0.04,	0.3924],
       [0.05,	0.4905],
       [0.06,	0.5886],
       [0.07,	0.6867],
       [0.08,	0.7848],
       [0.09,	0.8829],
       [0.1,	0.981],
       [0.11,	1.079],
       [0.12,	1.177],
       [0.13,	1.275],
       [0.14,	1.373],
       [0.15,	1.472],
       [0.16,	1.570],
       [0.17,	1.668],
       [0.18,	1.766],
       [0.19,	1.864],
       [0.2,	1.962],
       [0.21,	2.060],
       [0.22,	2.158],
       [0.23,	2.256],
       [0.24,	2.354],
       [0.25,	2.453],
       [0.26,	2.551],
       [0.27,	2.649],
       [0.28,	2.747],
       [0.29,  2.845],
       [0.3,	2.943],
       [0.31,	3.041],
       [0.32,	3.139],
       [0.33,	3.237],
       [0.34,	3.335],
       [0.35,	3.434],
       [0.36,	3.532],
       [0.37,	3.630],
       [0.38,	3.728],
       [0.39,	3.826],
       [0.4,	3.924],
       [0.5,	4.905],
       [0.6,	5.886],
       [0.7,	6.867],
       [0.8,	7.848],
       [0.9,	8.829],
       [1,	9.810]]



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
# Save data
#================================================================================
#print("...Exporting results in a .mat file")
#dir=os.path.dirname(os.path.abspath("read_plot_beam_nastran.py"))
#path = os.path.join(dir, "beam_num_data_out.mat")
#database = {}
##
### Write problem data
##database["number_of_modes"] = n_fields
#database["grids"] = grids
#database["num_coordinates"] = grid_coord_NASTRAN
#database["num_mode_shapes"] = mode_shapes_NASTRAN[47] + static_deform[47]
##
### Write mode shapes
##
## Write frequencies 
#database["num_freq"] = freq_NASTRAN[47]
## Write loads
##database["Loads"] = Loads
#
## Writing database
#if os.path.isfile(path):
#    os.remove(path)
#sio.savemat(path,database,appendmat=False)


#================================================================================
# Termination message
#================================================================================
#
#print("\nNASTRAN data import completed")
##
#
max_static_deform=np.zeros(48)
for i in range(0,n_subcases):
    max_static_deform[i]=max(abs((static_deform[i][2,:])))+max(static_deform[i][2,:])

# snippet to plot all static displacements vs. loads
print("Static Displacement with loads")   
fig=plt.figure(figsize=(15,5)) 
for i in range(0,n_subcases):
    plt.plot(grid_coord_NASTRAN[0,:]+static_deform[i][0][:],(static_deform[i][2][:])/1.835*100,label=' ' +str(Loads[i][0])+ 'g' '',linewidth=3)
#    plt.title('Static deformation with loads in g outboard' ,fontsize=32)
    plt.xlabel('Beam Length [m]',fontsize=26)
    plt.ylabel('Vertical deflection [% of max]',fontsize=26)
    plt.xticks(fontsize=25)
    plt.yticks(fontsize=25)
    plt.annotate('Increasing loads [g]', xy=(1.7, -25), xytext=(1.7, 2),size = 25,
             arrowprops=dict(facecolor='black', shrink=0.05),
             )
    plt.legend(loc='lower right',fontsize=12)
#
#    fig.savefig('loads_static_out.svg',bbox_inches='tight')

# code snippet to plot undeformed and fully deformed cases    
print("Static Displacement with loads")   
fig=plt.figure(figsize=(15,5)) 

plt.plot(grid_coord_NASTRAN[0,:]+static_deform[0][0][:],(static_deform[0][2][:])/1.835*100,label=' ' +str(Loads[0][0])+ 'g' '',linewidth=3)
plt.plot(grid_coord_NASTRAN[0,:]+static_deform[len(static_deform)-1][0][:],(static_deform[len(static_deform)-1][2][:])/1.835*100,label=' ' +str(Loads[len(static_deform)-1][0])+ 'g' '',linewidth=3)
#    plt.title('Static deformation with loads in g outboard' ,fontsize=32)
plt.xlabel('Beam Length [m]',fontsize=26)
plt.ylabel('Vertical deflection [% of max]',fontsize=26)
plt.xticks(fontsize=25)
plt.yticks(fontsize=25)
plt.annotate('Increasing load [g]', xy=(1.7, -25), xytext=(1.7, 2),size = 25,
         arrowprops=dict(facecolor='black', shrink=0.05),
         )
plt.legend(loc='lower right',fontsize=24)

#fig.savefig('loads_static_out.svg',bbox_inches='tight')

#================================================================================
# Mode tracking create data
#================================================================================

print("\nStart of mode tracking data formatting")
data_mode_sets =[[[0.,np.zeros([6*n_grids])] for i in range(n_fields)] for j in range(n_subcases)]
for i in range(n_subcases):
    for j in range(n_fields):
        data_mode_sets[i][j][0] = freq_NASTRAN[i][j]
        data_mode_sets[i][j][1] = mode_shapes_NASTRAN[i][j].flatten('F') # double check that it flattened correctly
        


#================================================================================
# Save data
#================================================================================
#print("...Exporting mode set results in a .mat file")
#dir=os.path.dirname(os.path.abspath("load_save_modes_mat.py"))
#path = os.path.join(dir, "mode_sets_out_tuned.mat")
#database = {}
##
## Write primary data
#database["mode_sets"] = data_mode_sets
#
## Write loads
#database["Loads"] = Loads
#
## Writing database
#if os.path.isfile(path):
#    os.remove(path)
#sio.savemat(path,database,appendmat=False)
#================================================================================
# End of Save data
#================================================================================      
       
def PlotReal(var, data, line=True, sym=True):
    """Plots the real mode progression over a variable.
    """
    N_sets = len(data)
    N_modes = data[0].Size()
    real = np.zeros([N_sets, N_modes])

    for i in range(N_sets):
        for j in range(N_modes):
            real[i,j] = data[i][j]["value"].real

    # plot the data
    opt = ""
    if sym:
        opt += "o"
    if line:
        opt += "-"

    plt.plot(var, real, opt)
    
print("\nRead and plot untracked data")
mode_sets = []

for modeset_list in data_mode_sets:
    
    modeset = ModeSet()
    for mode in modeset_list:
        pair = EigenPair()
        pair["value"], pair["vector"]  = mode

        modeset.AddPair(pair)

    mode_sets.append(modeset)
    
seed = ModeSet()

print(mode_sets[0])

for i in range(mode_sets[0].Size()):
#    print(i)
    if (i >=0) and (i < 23):
#        print("adding mode " +str(i))
        pair  = mode_sets[0][i]
        seed.AddPair(pair)
        
var1=np.array(Loads)[0:,0] # store loads
# plot the untracked mode sets
fig1=plt.figure(figsize=(15,8))
PlotReal(var1, mode_sets[0:], sym=True, line=True)
plt.rcParams["lines.linewidth"] = 3
plt.title('Modes evolution with loading in g outboard(untracked)',fontsize=32 )
plt.xlabel("Loads [g]",fontsize=26)
plt.ylabel("Frequency [Hz]",fontsize=26)
plt.ax = plt.gca()
plt.xticks(fontsize=25)
plt.yticks(fontsize=25)
plt.ax.spines["right"].set_visible(False)
plt.ax.spines["top"].set_visible(False)

#fig1.savefig("untracked_test_out_tuned.svg",bbox_inches='tight')

print("\ntrack modes")
tracked_mode_sets=TrackModes(seed,mode_sets[0:])
var2=np.array(Loads)[0:,0]
print("\nPlot tracked data")
fig2=plt.figure(figsize=(15,8))
plt.rcParams["lines.linewidth"] = 4
PlotReal(var2, tracked_mode_sets, sym=True, line=True)
plt.title('Modes evolution with loading: outboard(tracked)',fontsize=32 )
plt.xlabel("Loads [g]",fontsize=26)
plt.xticks(fontsize=25)
plt.yticks(fontsize=25)
plt.ylabel("Frequency [Hz]",fontsize=26)
plt.ax = plt.gca()
plt.annotate('1 T', xy=(-0.05,46), xytext=(-0.05, 46),size=25)
plt.annotate('2 IP', xy=(-0.05,53), xytext=(-0.05, 53),size=25)
plt.annotate('2 T', xy=(-0.05,97), xytext=(-0.05, 97),size=25)
plt.annotate('1 IP', xy=(-0.05, 18), xytext=(-0.05, 18),size=25)
plt.annotate('Pitch:X', xy=(-0.05, 1), xytext=(-0.05, 1),size=25)

plt.ax.spines["right"].set_visible(False)
plt.ax.spines["top"].set_visible(False)

#fig2.savefig("tracked_test_out_tuned.svg",bbox_inches='tight')

fig3=plt.figure(figsize=(15,8))
plt.rcParams["lines.linewidth"] = 4
PlotReal(max_static_deform*100/1.835, tracked_mode_sets, sym=True, line=True)
plt.title('Modes evolution with max static deformation: outboard(tracked)',fontsize=32 )
plt.xlabel("Tip Deflection [% semi-span]",fontsize=26)
plt.xticks(fontsize=25)
plt.yticks(fontsize=25)
plt.ylabel("Frequency [Hz]",fontsize=26)
plt.ax = plt.gca()
plt.annotate('1 IP', xy=(-0.02, 18), xytext=(-0.02, 18),size=25)
plt.annotate('1 T', xy=(-0.02,48), xytext=(-0.02, 48),size=25)
plt.annotate('2 IP', xy=(-0.02,52), xytext=(-0.02, 52),size=25)
plt.annotate('2 T', xy=(-0.02,97), xytext=(-0.02, 97),size=25)
plt.annotate('Pitch:X', xy=(-0.04, 1), xytext=(-0.04, 1),size=25)

plt.ax.spines["right"].set_visible(False)
plt.ax.spines["top"].set_visible(False)

#fig3.savefig("tracked_test_out_tuned_static.svg",bbox_inches='tight')
        
def PlotReal2(var, data, line=True, sym=True):
    """Plots the real mode progression over a variable. 
    Modified to plot only certain modes input by the user in the 
    test_modes array
    """
    N_sets = len(data)
    N_modes = data[0].Size()
    real = np.zeros([N_sets, N_modes])

    for i in range(N_sets):
        for j in range(N_modes):
            real[i,j] = data[i][j]["value"].real

    # plot the data
    opt = ""
    if sym:
        opt += "o"
    if line:
        opt += "-"
    test_modes=np.array([0,11,16,17,22])
    real2=real[:,test_modes]
    plt.plot(var, real2, opt)

#    print("...Exporting results in a .mat file")
    dir=os.path.dirname(os.path.abspath("read_plot_beam_nastran.py"))
    path = os.path.join(dir, "outb_tracked_modes.mat")
    database = {}
    
    # Write problem data
    database["Loads"] = var2
    database["tracked_modes_out"] = real2
    
    # Writing database, uncomment if want to store selected modes in a .mat file
#    if os.path.isfile(path):
#        os.remove(path)
#    sio.savemat(path,database,appendmat=False)
#    
#print("\ntrack modes")
tracked_mode_sets=TrackModes(seed,mode_sets[0:])
var2=np.array(Loads)[0:,0]
    
print("\nPlot tracked data with modes of interest")
fig4=plt.figure(figsize=(15,8))
plt.rcParams["lines.linewidth"] = 4
PlotReal2(var2, tracked_mode_sets, sym=True, line=True)
plt.title('Selected modes evolution with loading: outboard(tracked)',fontsize=32 )
plt.xlabel("Loads [g]",fontsize=26)
plt.xticks(fontsize=25)
plt.yticks(fontsize=25)
plt.ylabel("Frequency [Hz]",fontsize=26)
plt.ax = plt.gca()
plt.annotate('Pitch:X', xy=(-0.05, 1), xytext=(-0.05, 1),size=25)
plt.annotate('1 IP', xy=(-0.05, 18),   xytext=(-0.05, 18),size=25)
plt.annotate('1 T', xy=(-0.05,45),     xytext=(-0.05, 45),size=25)
plt.annotate('2 IP', xy=(-0.05,53),    xytext=(-0.05, 53),size=25)
plt.annotate('2 T', xy=(-0.05,97),     xytext=(-0.05, 97),size=25)

plt.ax.spines["right"].set_visible(False)
plt.ax.spines["top"].set_visible(False)

#fig4.savefig("tracked_test_out_tuned_selected.svg",bbox_inches='tight')

fig5=plt.figure(figsize=(15,8))
plt.rcParams["lines.linewidth"] = 4
PlotReal2(max_static_deform, tracked_mode_sets, sym=True, line=True)
plt.title('Selected modes evolution with max static deformation: outboard(tracked)',fontsize=32 )
plt.xlabel("Tip Deflection [% semi-span]",fontsize=26)
plt.xticks(fontsize=25)
plt.yticks(fontsize=25)
plt.ylabel("Frequency [Hz]",fontsize=26)
plt.ax = plt.gca()
plt.annotate('1 IP', xy=(-0.02, 18), xytext=(-0.02, 18),size=25)
plt.annotate('1 T', xy=(-0.02,48), xytext=(-0.02, 48),size=25)
plt.annotate('2 IP', xy=(-0.02,52), xytext=(-0.02, 52),size=25)
plt.annotate('2 T', xy=(-0.02,97), xytext=(-0.02, 97),size=25)
plt.annotate('Pitch:X', xy=(-0.02, 1), xytext=(-0.02, 1),size=18)
plt.ax.spines["right"].set_visible(False)
plt.ax.spines["top"].set_visible(False)

#fig5.savefig("tracked_test_out_tuned_static_select.svg",bbox_inches='tight')