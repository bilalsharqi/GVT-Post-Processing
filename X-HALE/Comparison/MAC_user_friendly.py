import numpy as np
import os
import pyuff
import scipy.io as sio
import shutil
import sys
from mpl_toolkits.mplot3d import axes3d
import matplotlib.pyplot as plt
from matplotlib import style
style.use('ggplot')

plt.close("all")

#need to reduce data from xhale and beam vis 
#Full Mac for xhale and plot values of manual and xhale automatic
#==========================================Load Data Section ==========================================================

# Step 0: Load your Numerical and Experimental Files

#XHALE MAC
num_file = 'NASTRAN_mode_shapes_out.mat' #Num XHALE Here
exp_file = 'xhale_exp_data.mat' #Exp XHALE Here

exp_data = sio.loadmat(exp_file)
num_data = sio.loadmat(num_file)


#------Data for Non Uniform Beam Case-------#
num_file_beam = 'beam_num_data_in_copy.mat' #Num beam here
exp_file_beam = 'beam_exp_data_copy.mat' #Exp beam here

num_data_beam = sio.loadmat(num_file_beam)
exp_data_beam = sio.loadmat(exp_file_beam)


#-------Data for Undeformed Exoerimental Test Case  --------#
file_name = 'gvt1all_copy.unv' #don't worry about this, this is the undeformed xhale 
uff_file = pyuff.UFF(file_name)

types_of_sets = uff_file.get_set_types()

data = uff_file.read_sets()


# locations of accelerometers (or nodes) for UNDEFORMED TEST CASE
coordinates_exp = []
for sub in data: 
    if sub['type'] == 15: 

        coordinates_exp = [sub['x'],sub['y'],sub['z']]
        break
#------End of Data for Undeformed Test Case -------#
# ==============================================================================================================





#====================================Grid and Frequency Section (Determine what type of comparison you want to do)==================================================

# STEP 1 DECIDE WHICH COMPARISON YOU WISH TO MAKE: XHALE MAC, INDIVIDUAL XHALE MAC, FULL BEAM MAC
manual_mac_display = False
individual_mac_display = False
beam_mac_display = False
full_mac_beam_display = False

# Step 1a: If you want to use only manually sorted data: (Otherwise ignore this section and script will use organizedGrids) 
#     - put grid points put the grid points in 'grids_uni_le_te'
#     - put idicies of interested numerical frequencies in freq_allowed
#     - list indicies of experimental data frequencies you are not interested in in the 'deleted_exp_freq'

# ------------Manually Sorted XHALE --------------------------#

# Accelerometer locations Manually sorted
grids_uni_le_te = [15420, 15020, 15220, 15416, 15016, 15216, 14004, 10420, 10002, 10220, 13004, 9003, 5419, 5402, 5220, 8004, 16411, 16011, 16211, 4005, 19003, 21411, 21011, 21211, 19002, 26412, 26012, 26212, 24001, 26418, 26018, 26218, 25004, 26420, 26020, 26220]

#Frequencies allowed manually sorted
freq_allowed = [6, 8, 12, 13, 19, 20 ]

#Indicies of ignored experiment frequencies
temp_exp_range_manual = range(0,len(exp_data['exp_freq'][0]))
deleted_exp_freq = [0,3,4,7,9]

manual_good_exp_freq = np.delete(temp_exp_range_manual, deleted_exp_freq) #testing first fundamental modes at 1.01 exp freq

    #----------------End of Manually Sorted --------------------#

# Step 1b: If you want to complete a Self MAC: (Otherwise ignore this section)
    # - Enter the numerical freq index you want to use in 'freq_allowed_self_v1'
    # - Enter the experimental freq index you want to use in 'individual_exp_freq'

#------------Individual MAC XHALE-----------------#
freq_allowed_self_v1 = [6] #input the frequency correllating to the NUMERICAL frequency index that you want to compare
individual_exp_freq = [1] #input the frequency correllating to the EXPERIMETNAL frequency index you want to compare

temp_exp_range = range(0,len(exp_data['exp_freq'][0]))
deleted_exp_freq_self_v1 = np.delete(temp_exp_range, individual_exp_freq) #testing first fundamental modes at 1.01 exp freq
    #-----------End of Individual MAC -------------------------#

# Step 1c: If you want to complete a MAC on a beam (or some other object): (Otherwise ignore this section)
    # - Enter the numerical freq indices you want to use in 'freq_allowed_total_beam'
    # - Enter the experimental freq indices you want to use in 'good_exp_beam_data'
    # - This MAC has a global translation to translate all numerical data to the position of the experimental data. This can be adjusted in lines 469 and 470

#------------Non-Uniform Beam MAC, uses organizedGrids function 
freq_allowed_beam_total = [7,8,9,10,12,13]  #enter in indicies of correct num freq and exp freq matched here !!!
good_exp_beam_data = [1,2,4,7,8,14]

temp_range_vec = range(0,len(exp_data_beam['exp_freq'][0]))
deleted_exp_beam_total = np.delete(temp_range_vec,good_exp_beam_data)




#Step 2a: Set the offset for the XHALE (Translates numerical data to experimental data ONLY Z )
XHALE_offset_x = 0.0
XHALE_offset_z = 0.509

#Step 2b: Set offset (x and z offset for Beam data)
beam_offset_x = -1.92577
beam_offset_z = 0.532887

# =====================================================================================================================





#====================================Preprocessing for data + Reshaping===========================================

#--------  Read In/ Transposing XHALE Num Data-------------
#import numerical and experimental data
mode_shapes_reduced_total = num_data['num_mode_shapes'][0][0]
all_grids = num_data['grids'][0]
exp_modes_norm = exp_data['exp_mode_shapes_normalized']


#note also had to transpose the non-deformed state as well deformed state and experimental data
mode_shapes_reduced_total = mode_shapes_reduced_total.transpose((2, 0, 1)) 
exp_modes_norm = exp_modes_norm.transpose((2, 0, 1)) 
exp_modes_norm_self = exp_modes_norm.copy()

#this changes the original axis formation from axis 0 , 1, 2 to axis 2, 0, 1 via transpose function /T
#new dimensions are 384 sheets of 25 x 6 arrays matching the original Matlab Script and Format /T
# ----- Adding Static + Deformd data (Numerical )------# (Deformed Numeric Shape)

#XHALE (Numeric)
#adds the two cells together static defomation to coordinates


#-------Read in/ Transposing Non-Uniform Beam Data------------------------------------------------- 
exp_mode_beam = exp_data_beam['exp_mode_shapes_normalized']
exp_beam_coord = exp_data_beam['exp_coordinates']
exp_mode_beam = exp_mode_beam.transpose((2,0,1))

#num_mode_beam = num_data_beam['num_mode_shapes']
num_beam_coord_def = num_data_beam['num_coordinates_in_with_def']
num_mode_beam = num_data_beam['sum_modal_def']
num_beam_coord = num_data_beam['num_coordinates']  #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! Cancel the mode transpose
 
num_mode_beam = num_mode_beam.transpose((2,0,1))
# =====================================================================================================================
                     
                     




# Pseudo code compGrid
    #do not read in z values
    #assign grid point I.D.s to each set of coordinates  
    #organize y values in ascending order and collect the indicies
    # use indicy values to organize the x values
    #Sort via tolerances
    #Implement contingency:
        #Bilal idea: if there are three or more values reduce to smallest tolerance (really small)

def plotGraphs (x1,y1,z1,x2,y2,z2):
    #Function plots two scatter graphs on top of each other. Enter [0] into x2,y2,z2, if you only want one scatter plot

    fig3 = plt.figure()
    ax3 = fig3.add_subplot(111, projection='3d')
    
    ax3.scatter(x1, y1, z1, c='b', linestyle='-', marker='o')
    ax3.plot(x1, y1, z1, c='b', linestyle='-', marker='o')

    ax3.scatter(x2, y2, z2, c='r',linestyle='-', marker='o')
    ax3.plot(x2, y2, z2, c='r',linestyle='-', marker='o')

    ax3.set_xlabel('X Label')
    ax3.set_ylabel('Y Label')
    ax3.set_zlabel('Z Label')
    ax3.set_ylim([-2,2])
    ax3.view_init(azim=-90, elev=0)
    return

class compGrid: 
    #creates class that is easy to sort based upon y coordinate with attached x coordinate and grid ID number
    def __init__ (self, y_comp, x_comp, gridID, z_comp, y_tol, x_tol):
        self.y = y_comp #y coordinate
        self.x = x_comp #x coordinate
        self.g = gridID #grid ID
        self.z = z_comp #z coordinate
        self.yt = y_tol #y tolerance 
        self.xt = x_tol #x tolerance


def organizeGrids (y_in, x_in, z_in, g_in, exp_in_y, exp_in_x, exp_in_z):
    #Function takes input of y coord_num, x_coord_num, z_coord_num, grid points of numerical data, y coord_exp, x_coord_exp, z_coord_exp
    #Function matches numerical grids to experimental grid points and returns matrix of grid number ID's and a scatter plot of both data sets, (numerical in red, experimental in blue )
    #del_list = []
    returned_grid_matrix = []
    x_s = []
    y_s = []
    z_s = []

       
    #Section one creating class objects of numerical and experimental code 
    grids_global_num = list()
    for sphynx in range(len(y_in)):
        grids_global_num.append(compGrid(y_in[sphynx], x_in[sphynx], g_in[sphynx],z_in[sphynx], None, None)) # creates list of objects with y,x,and grid ID 
    grids_global_num = sorted(grids_global_num, key = lambda compGrid: compGrid.y)  #arranges list in asceneding order 
    
    grids_global_exp = list()
    for pyramid in range(len(exp_in_y)): 
        grids_global_exp.append(compGrid(exp_in_y[pyramid], exp_in_x[pyramid], (pyramid + 1), z_in[pyramid], None, None)) # creates list of objects with y,x,and grid ID 
    grids_global_exp = sorted(grids_global_exp, key = lambda compGrid: compGrid.y)  #arranges list in asceneding order 

    grids_local_num = list()
    del_list = []
    temp_list = list()
    temp_list2 = list()
    for exp_range in range(0,(len(grids_global_exp))):   #outer for loop going through experimental element
        #print(exp_range)
       #Section two, two layers of sifting for y values closest matching experimental y values. Uses a 5% and 11% tolerance    
        grids_local_num.clear()
        grids_local_num = grids_global_num.copy()
        del_list.clear()
        temp_list.clear() #create temp list for y
        temp_list2.clear() #create tmep list for x
     
        #pre-processing (reduces total number of grid points searched. Searches if in positive or negative x plane and points with less than half of target value are removed)
        for num_range0 in range(0,(len(grids_local_num))):
            if grids_global_exp[exp_range].x > 0.1: # all values in quadrant y > 0 , x > 0 
                if grids_local_num[num_range0].x <= 0.5*grids_global_exp[exp_range].x:
                    del_list = np.append(del_list,[num_range0])
            if grids_global_exp[exp_range].x <= -0.1 :
                if grids_local_num[num_range0].x >= 0.5*grids_global_exp[exp_range].x:
                    del_list = np.append(del_list,[num_range0]) #append all values less than 0.5 negative version of   
            #still need to find a solution for points in -0.1 and 0.1 exclusion zone
            
            
        #make dictionary here 
        del_list = list(dict.fromkeys(del_list))
        del_list = sorted(del_list, reverse = True)
        for gamma in range(len(del_list)): #make reverse delete list here
            del grids_local_num[int(del_list[gamma])]
        
        # for trigger in range(len(grids_local_num)):  #------DEBUGGING SECTION FIX LATER----------
        #     print(str(grids_local_num[trigger].y)+' '+ str(grids_local_num[trigger].x))
        
        for num_range in range(0,(len(grids_local_num))): #create inner for loop going through numerical elements 
            if -0.1 <= grids_global_exp[exp_range].y <= 0.1 and -0.1 <= grids_local_num[num_range].y <= 0.1 : 
                grids_local_num[num_range].yt = abs(grids_local_num[num_range].y - grids_global_exp[exp_range].y)*(10**-2)
                temp_list.append(grids_local_num[num_range])
            else:
                if -0.1 <= grids_global_exp[exp_range].y <= 0.1:
                    p_diff = abs((grids_local_num[num_range].y - 10**-3)/(10**-3))#percent difference rel exp (in reality this calc greatly increases the %diff to prevent it from going through screen, just doesn't show divide by zero error)
                    grids_local_num[num_range].yt = p_diff
                    #x_range_temp = grids_global_exp[exp_range].x
                    if p_diff <= 0.05: # and (0.7*x_range_temp < grids_local_num[num_range].x < 1.3*x_range_temp): #must be within 20% x value to be added
                        temp_list.append(grids_local_num[num_range])
                        #if within 5% of experimental y value append to temp list
                    # if p_diff > 0.05 and len(temp_list) > 0: #if the temp indice is not empty AND percent difference rel. exp is greater than a 4% difference exit this loop
                    #     break #stops appending to the list after it gets in range and error is too great (this just is here to save time, may be problematic later)
                else:
                    p_diff = abs((grids_local_num[num_range].y - grids_global_exp[exp_range].y)/grids_global_exp[exp_range].y)#percent difference rel exp
                    grids_local_num[num_range].yt = p_diff
                    #x_range_temp = grids_global_exp[exp_range].x
                    if p_diff <= 0.05: # and (0.7*x_range_temp < grids_local_num[num_range].x < 1.3*x_range_temp): #must be within 20% x value to be added
                        temp_list.append(grids_local_num[num_range])
                        #if within 5% of experimental y value append to temp list
                    # if p_diff > 0.05 and len(temp_list) > 0: #if the temp indice is not empty AND percent difference rel. exp is greater than a 4% difference exit this loop
                    #     break #stops 
        

       #secondary processing. Ordered by x and finds the closest matching x value 
        #make contingency for grabbing the closest value if temp list is empty and doesn't match experiment
        if len(temp_list) == 0:
                #cycle through numbers and append the closest set of numbers, just repeat with bigger tolerance
            for num_range_e in range(len(grids_local_num)): 
                 if -0.1 <= grids_global_exp[exp_range].y <= 0.1 and -0.1 <= grids_local_num[num_range_e].y <= 0.1 : 
                     grids_local_num[num_range_e].yt = abs(grids_local_num[num_range_e].y - grids_global_exp[exp_range].y)*(10**-2)
                     temp_list.append(grids_local_num[num_range])
                 else: 
                    p_diff_e = abs((grids_local_num[num_range_e].y - grids_global_exp[exp_range].y)/grids_global_exp[exp_range].y)
                    grids_local_num[num_range_e].yt = p_diff_e
                    #x_range_temp1 = grids_global_exp[exp_range].x
                    if p_diff_e <= 0.11: # and (0.8*x_range_temp1 < grids_local_num[num_range_e].x < 1.2*x_range_temp1): #must be within 20% x value to be added
                        temp_list.append(grids_local_num[num_range_e])
                    # if p_diff_e > 0.11 and len(temp_list) > 0: #if the temp indice is not empty AND percent difference rel. exp is greater than a 4% difference exit this loop
                    #     break #stops appending to the list after it gets in range and error is too great (this just is here to save time, may be problematic later)
            
        #temp_list = sorted(temp_list, key = lambda compGrid: compGrid.x)
        
        
        # for trigger2 in range(len(temp_list)):  #DEBUGGING SECTION FIX LATER
        #     print(str(temp_list[trigger2].yt)+' '+str(temp_list[trigger2].y) + ' '+str(temp_list[trigger2].x)) 
           
           
       #Section 3 using temp matrix sort through temp x values compare to find the smallest absolute value difference (just use code from frequency work below)
        for t in range(len(temp_list)):
        
            if -0.01 <= grids_global_exp[exp_range].x <= 0.01 and -0.01 <= temp_list[t].x <= 0.01:
                  p_diff_x =  abs(temp_list[t].x - grids_global_exp[exp_range].x)*(10**-2)
                  temp_list[t].xt = p_diff_x
            else:
                if -0.01 <= grids_global_exp[exp_range].x <= 0.01:
                    p_diff_x = abs((temp_list[t].x - 10e-3)/10e-3) #percent difference rel zero point (but not exactly zero)
                    temp_list[t].xt = p_diff_x
                    
                else: 
                    p_diff_x = abs((temp_list[t].x - grids_global_exp[exp_range].x)/ grids_global_exp[exp_range].x) #else assign it to a percentage value 
                    temp_list[t].xt = p_diff_x
         
        
        temp_list = sorted(temp_list, key = lambda compGrid: compGrid.xt)
        for t2 in range(len(temp_list)):
            if temp_list[t2].xt <= (1.5*temp_list[0].xt) : #(0.9*temp_list[0].xt) <
                temp_list2.append(temp_list[t2])
     #sort the x values in this way. sort by xt first, then get that x value and if any values larger or smaller than this value do not get added. (really making sure )  
                                    #might run into issues with this. Maybe round up to the nearest 2 decimal points when doing this comparison
        #print(len(temp_list2))
        
        # del temp_list[int(del_list[:])] #deletes all points greater than 5% tolerance x 
        temp_list2 = sorted(temp_list2, key = lambda compGrid: compGrid.yt)
        returned_grid_matrix = np.append(returned_grid_matrix, float(temp_list2[0].g)) #uses the closest y-index (first index after sorting)
        x_s = np.append(x_s, temp_list2[0].x)  
        y_s = np.append(y_s, temp_list2[0].y)
        z_s = np.append(z_s, temp_list2[0].z)
       
        
                
    fig1 = plt.figure()
    ax1 = fig1.add_subplot(111, projection='3d')
    
    ax1.scatter(np.round(x_s[:],4), np.round(y_s[:],4), np.round(z_s[:],4), c='r', marker='o')
    ax1.scatter(exp_in_x, exp_in_y, exp_in_z, c='b', marker='o')
    ax1.set_xlabel('X Label')
    ax1.set_ylabel('Y Label')
    ax1.set_zlabel('Z Label')
    #fig1.show()
    return returned_grid_matrix
    
#Averaging function for beam 

def beamAverage (x_beam, y_beam, z_beam, zero_point):
    #This function assumes that the non-uniform beam straddles the y = 0 line
    # pos_points = list()
    # neg_points = list()
    temp_x = []
    temp_y = []
    temp_z = []
    
    #Based on readin data, the data technically comes in pairs. We can exploit this and avoid sorting by using the following
    for y in range(0,len(y_beam),2):
        temp_x = np.append(temp_x,  (x_beam[y] + x_beam[y+1])/2)
        temp_y = np.append(temp_y,  (y_beam[y] + y_beam[y+1])/2)
        temp_z = np.append(temp_z,  (z_beam[y] + z_beam[y+1])/2) 
    return(temp_x, temp_y, temp_z)
            
def normalizeNumData (data_mode):
    #Normalizes the numerical data by the largest value of the data set (either negative or positive). We are assuming the experimental data has been normalized by the largest absolute value magnitude and has been read in through the .mat file
    for centaur in range(len(data_mode[0])):
        max_index = np.where(np.abs(data_mode[:,centaur,2]) > 0, np.abs(data_mode[:,centaur,2]), np.inf).argmax()
        max_pos_neg = data_mode[max_index,centaur,2]
        for pos_run in range (len(data_mode)): 
            data_mode[pos_run,centaur,2] = data_mode[pos_run,centaur,2]/max_pos_neg
    
    return data_mode

#========================Section to call organizeGrids function ========================================#

#static deformation + coordinate data 
num_sim_static_coords = np.delete(num_data['num_mode_shapes'][0][1],[3, 4, 5], axis = 0)
num_sim_static_coords = np.add(num_sim_static_coords, num_data['num_coordinates'])


# Static Case Deformed ('U' Shape)
grids_matched_def = []
grids_matched_def = organizeGrids(num_sim_static_coords[1,:],num_sim_static_coords[0,:],num_sim_static_coords[2,:], all_grids, exp_data['exp_coordinates'][1], exp_data['exp_coordinates'][0], exp_data['exp_coordinates'][2])


#Static Case Undeformed ('Flat' Shape) 
grids_matched_static_test = []
grids_matched_static_test = organizeGrids(num_data['num_coordinates'][1], num_data['num_coordinates'][0],num_data['num_coordinates'][2], all_grids, coordinates_exp[1], coordinates_exp[0], coordinates_exp[2])


#------------Non-Uniform Beam Case -----------------#
averaged_x, averaged_y, averaged_z = beamAverage(exp_data_beam['exp_coordinates'][0,:],exp_data_beam['exp_coordinates'][1,:],exp_data_beam['exp_coordinates'][2,:],0)
temp_add_x = num_data_beam['num_coordinates_in_with_def'][0] - 1.83
temp_add_z = num_data_beam['num_coordinates_in_with_def'][2] + 0.53285
grids_matched_beam = []
grids_matched_beam  = np.asarray(organizeGrids(num_data_beam['num_coordinates_in_with_def'][1],temp_add_x, temp_add_z ,num_data_beam['grids'][0], averaged_y, averaged_x ,averaged_z ))

# ===================================================================================================================




#============================Section to add Mode amplitude with their coordinates+deformation for Mode Visualisation========================#


# --------------      ----------------  XHALE ---------------  -----------------


#--------Adding Mode amplitude to NUMERICAL u-shape coordinates for visualisation
mode_shapes_reduced_total_vis = mode_shapes_reduced_total.copy()
for igloo in range(len(mode_shapes_reduced_total)): 
    for jacob in range(len(mode_shapes_reduced_total[0])):
        mode_shapes_reduced_total_vis[igloo,jacob,0] = mode_shapes_reduced_total[igloo,jacob,0] + num_sim_static_coords[0,igloo] #x component
        mode_shapes_reduced_total_vis[igloo,jacob,1] = mode_shapes_reduced_total[igloo,jacob,1] + num_sim_static_coords[1,igloo] #y component
        mode_shapes_reduced_total_vis[igloo,jacob,2] = mode_shapes_reduced_total[igloo,jacob,2] + num_sim_static_coords[2,igloo] #z component



#---------Adding mode aplitude to EXPERIMENTAL u-shape coordinates Entire MAC for visualisation
exp_modes_norm_vis = exp_modes_norm.copy()
for igloo2 in range(len(exp_modes_norm)):
    for jacob2 in range(len(exp_modes_norm[0])):
        exp_modes_norm_vis[igloo2,jacob2,0] = exp_modes_norm[igloo2,jacob2,0] + exp_data['exp_coordinates'][0][igloo2] 
        exp_modes_norm_vis[igloo2,jacob2,1] = exp_modes_norm[igloo2,jacob2,1] + exp_data['exp_coordinates'][1][igloo2] 
        exp_modes_norm_vis[igloo2,jacob2,2] = exp_modes_norm[igloo2,jacob2,2] + exp_data['exp_coordinates'][2][igloo2] 


#--------- Individual MAC Adding mode aplitude to EXPERIMENTAL u-shape coordinates for visualisation
exp_modes_norm_self_vis = exp_modes_norm_self.copy()
for igloo3 in range(len(exp_modes_norm_self)):
    for jacob3 in range(len(exp_modes_norm_self[0])):
        exp_modes_norm_self_vis[igloo3,jacob3,:] = exp_modes_norm_self[igloo3,jacob3,:] + exp_data['exp_coordinates'][:,igloo3] 



#--------       ------------- Beam section Visualisation-------------   ----------------

#----Experimental data ---------------
exp_mode_beam_vis = exp_mode_beam.copy()
for juliet in range(len(exp_mode_beam)):
    for kilo in range(len(exp_mode_beam[0])):
        exp_mode_beam_vis[juliet,kilo,0] = exp_mode_beam[juliet,kilo,0] + exp_beam_coord[0,juliet]
        exp_mode_beam_vis[juliet,kilo,1] = exp_mode_beam[juliet,kilo,1] + exp_beam_coord[1,juliet] 
        exp_mode_beam_vis[juliet,kilo,2] = exp_mode_beam[juliet,kilo,2] + exp_beam_coord[2,juliet]


num_mode_beam_vis = num_mode_beam.copy()
for hector_v in range(len(num_mode_beam)):
    for hector2_v in range(len(num_mode_beam[0])):
        num_mode_beam_vis[hector_v,hector2_v,0] = num_mode_beam[hector_v,hector2_v,0] - num_beam_coord_def[0,hector_v] - num_beam_coord[0,hector_v]
        num_mode_beam_vis[hector_v,hector2_v,1] = num_mode_beam[hector_v,hector2_v,1] - num_beam_coord_def[1,hector_v] - num_beam_coord[1,hector_v]
        num_mode_beam_vis[hector_v,hector2_v,2] = num_mode_beam[hector_v,hector2_v,2] - num_beam_coord_def[2,hector_v] - num_beam_coord[2,hector_v]



#Averaging experimental data: 
    beam_exp_full_vis = np.zeros((int(len(exp_mode_beam_vis)/2),len(exp_mode_beam_vis[0]),len(exp_mode_beam_vis[0,0])))
for kami_v in range(len(exp_mode_beam_vis[0])): 
    temp_av_x_v, temp_av_y_v, temp_av_z_v = beamAverage(exp_mode_beam_vis[:,kami_v,0],exp_mode_beam_vis[:,kami_v,1],exp_mode_beam_vis[:,kami_v,2], 0)
    beam_exp_full_vis[:,kami_v,0] = temp_av_x_v
    beam_exp_full_vis[:,kami_v,1] = temp_av_y_v
    beam_exp_full_vis[:,kami_v,2] = temp_av_z_v
# =============================================================================================================











#========================================Additional Processing, translations + num data normalizations =============================
#------- ----------XHALE Section Additional Processing: Add mode to beam coord data ---------- -------------------

#/////////////Global XHALE Offsets: DO NOT TOUCH UNLESS EXPERIMENTAL SETUP CHANGES\\\\\\\\\\\\\\\\\\\\\\\\\
mode_shapes_reduced_total[:,:,0] = mode_shapes_reduced_total[:,:,0] + XHALE_offset_x
mode_shapes_reduced_total[:,:,2] = mode_shapes_reduced_total[:,:,2] + XHALE_offset_z
#/////////////Global XHALE Offsets: DO NOT TOUCH UNLESS EXPERIMENTAL SETUP CHANGES\\\\\\\\\\\\\\\\\\\\\\\\\


# add num normalization here 
mode_shapes_reduced_total = normalizeNumData(mode_shapes_reduced_total)


#--------       ------------- Beam section Additional Processing: Add Mode to beam coord data-------------   ----------------

#--------------Numerical data --------------

#We are trying to remove the static deformation from the total beam data since it was exported with static deformation
# Use static def to remove the static def from the total modes
for hector in range(len(num_mode_beam)):
    for hector2 in range(len(num_mode_beam[0])):
        num_mode_beam[hector,hector2,0] = num_mode_beam[hector,hector2,0] - num_beam_coord_def[0,hector]
        num_mode_beam[hector,hector2,1] = num_mode_beam[hector,hector2,1] - num_beam_coord_def[1,hector]
        num_mode_beam[hector,hector2,2] = num_mode_beam[hector,hector2,2] - num_beam_coord_def[2,hector]

# -----------Normalize beam numerical data-------------------

#/////////////Global Beam Offsets: DO NOT TOUCH UNLESS EXPERIMENTAL SETUP CHANGES\\\\\\\\\\\\\\\\\\\\\\\\\
num_mode_beam[:,:,0] = num_mode_beam[:,:,0] + beam_offset_x 
num_mode_beam[:,:,2] = num_mode_beam[:,:,2] + beam_offset_z
#/////////////Global Beam Offsets: DO NOT TOUCH UNLESS EXPERIMENTAL SETUP CHANGES\\\\\\\\\\\\\\\\\\\\\\\\\

num_mode_beam = normalizeNumData(num_mode_beam)

#===============================================end section=====================================================#





# =====================Visualization Secton for global translations and Rotations of Data==========================
 



#----------------USE THIS EXTENSIVELY WITH EACH NEW DATA SET method to match Beam frequencies of num (coord+mode) and exp (coord+mode) data by hand --------------------------
# temporary close
# tri = 14  
# trid = 13
# plotGraphs(-exp_mode_beam[:,tri,0],exp_mode_beam[:,tri,1],exp_mode_beam[:,tri,2],[0],[0],[0])
# # print('Current Exp Frequency is ' + str(exp_data_beam['exp_freq'][0,tri]) + ' Hz')
# for fifa in range(trid,trid + 5): 
#     matching_mods = plt.figure()
#     ax4 = matching_mods.add_subplot(111, projection='3d')
#     ax4.scatter(num_mode_beam[:,fifa,0],num_mode_beam[:,fifa,1],num_mode_beam[:,fifa,2], c='b', marker='o')
#     plt.title('Num Frequency of ' + str(num_data_beam['num_freq'][0,fifa]) + ' Hz')
#     ax4.set_xlabel('X Label')
#     ax4.set_ylabel('Y Label')
#     ax4.set_zlabel('Z Label')
#     ax4.set_ylim([-2,2])

#Uncomment this if you do not wish to see resulting data 
# plt.close('all')
#========================================End of Visualizations===============================================================







#Note: modes_shapes_reduced_total defined above is just put aside here so it does not manipulate code 
def remove_Grid_Freq (total_grids, mode_shapes_reduced_dummy, freq_we_want, grids_we_want):
    #Function removes grids (associated with grid number IDs as input)
        #Read in Values: 
            # 'total_grids': total grids ID's in numeric data set
            # 'mode_shapes_reduced_dummy': the mode data that you want reduced in order of [gridpoints x frequencies x accel directions (translations x,y,z)]
            # 'freq_we_want': numerical frequencies that are to be compared (we are getting rid of the rest of the frequencies)
            # 'grids_we_want': numerical grids that have been identified to match the experimental grids points (we want these for analysis later and want to get rid of the rest of the grid points)
    int_2_remove = [] #presumably cycling through the 348 gridpoint /T
    freq_2_remove = []
    for gridpoint in range(len(total_grids)):  
        if total_grids[gridpoint] not in grids_we_want:
            int_2_remove.append(gridpoint)
    mode_shapes_reduced_dummy = np.delete(mode_shapes_reduced_dummy, int_2_remove,0)  
    if len(freq_we_want) != 0:
        for f in range(len(mode_shapes_reduced_dummy[0])): #cycles through 25 frequencies in numerical data/T
            #    print(node)
            #    print(node_number[node])
            if f not in freq_we_want:  
            #       number assignment
                    freq_2_remove.append(f)  #-Problem int_2_remove is 348 long (removing all nodes??)
    mode_shapes_reduced_dummy = np.delete(mode_shapes_reduced_dummy, freq_2_remove,axis = 1)  
    return mode_shapes_reduced_dummy





# ========================================Beam ONLY Experimental data (coord+mode) Processing (Averaging and rotation of exp modes)===================


beam_exp_full = np.zeros((int(len(exp_mode_beam)/2),len(exp_mode_beam[0]),len(exp_mode_beam[0,0])))
for kami in range(len(exp_mode_beam[0])): 
    temp_av_x, temp_av_y, temp_av_z = beamAverage(exp_mode_beam[:,kami,0],exp_mode_beam[:,kami,1],exp_mode_beam[:,kami,2], 0)
    beam_exp_full[:,kami,0] = temp_av_x 
    beam_exp_full[:,kami,1] = temp_av_y 
    beam_exp_full[:,kami,2] = temp_av_z 



# =======================================end section ==========================================================



#======================Section to call remove_Grid_Freq functions =============================#
#note in this process we are reducing modes BEFORE they are matched to modes


# ------Manually sorted grids points------------
working_matrix = remove_Grid_Freq(all_grids, mode_shapes_reduced_total,freq_allowed, grids_uni_le_te )


#---------- Individual MAC for XHALE --------------------#
self_mac_rgf = remove_Grid_Freq( all_grids,mode_shapes_reduced_total,freq_allowed_self_v1 ,grids_matched_def )


#----------Remove grid_freq for beam ------------------#

#individual MAC remove_Grid_Freq
# beam_edited = remove_Grid_Freq(np.reshape(num_data_beam['grids'],(len(num_data_beam['grids'][0]),1)),num_mode_beam, [7], list(grids_matched_beam))


#full mac of non uniform beam
beam_num_edited_full = remove_Grid_Freq(np.reshape(num_data_beam['grids'],(len(num_data_beam['grids'][0]),1)),num_mode_beam, freq_allowed_beam_total , list(grids_matched_beam))



# =================================end section=========================================
 



#==============Additional Visualisation to check if grad3D worked=======================
# plt.close('all')
# for cypher in range(len(beam_exp_full[0])):
#     plotGraphs(beam_exp_full[:,cypher,0],beam_exp_full[:,cypher,1],beam_exp_full[:,cypher,2],beam_num_edited_full[:,cypher,0],beam_num_edited_full[:,cypher,1],beam_num_edited_full[:,cypher,2])
# =======================================================================================


#Function deletes the rotational modes and creates a 2D matrix of frequencies x all measurements in one mode (every three)
def orderPhi (num_reduced_matrix, length_vec):
    # Note: Function takes reduced data and returns matrix of dimension [# frequencies x grid z values in each mode]
    # Input values: 
        #num_reduced_matrix: the already reduced matrix without the unwanted grid points and frequencies NOTE: CAN BE NUMERIC MATRIX OR EXPERIMENTAL MATRIX, you need to do if for both anyway
        #length_vec: contains the frequencies indicies that are to be compared in the respected data set. the values themsleves don't matter it is just the length vec we want
    
    if (len(length_vec)) == 1: #Individual Mode MAC
        altered_working_matrix = num_reduced_matrix[0,0,2] 
        for foxtrot in range(1,len(num_reduced_matrix)):
            #altered_working_matrix = np.append(altered_working_matrix, np.reshape(num_reduced_matrix[foxtrot,:,2],(len(length_vec),1)), axis = 1)
            altered_working_matrix = np.append(altered_working_matrix, num_reduced_matrix[foxtrot,:,2])

    else: #GENERAL MAC
        altered_working_matrix = np.reshape(num_reduced_matrix[0,:,2],(len(length_vec),1)) #this can not be hardcoded in the future
        for foxtrot in range(1,len(num_reduced_matrix)):
            altered_working_matrix = np.append(altered_working_matrix, np.reshape(num_reduced_matrix[foxtrot,:,2],(len(length_vec),1)), axis = 1)

    return altered_working_matrix
       

def plotMAC(mac):
    # Given MAC array, function plots 3d bar graph
    mac_plot1 = plt.figure()
    ax5 = mac_plot1.add_subplot(111, projection = '3d')
    x_values1 = []
    y_values1 = []
    z_values1 = np.zeros((np.size(mac))) #corrected
    dx1 = np.ones(np.size(mac))
    dy1 = np.ones(np.size(mac)) 
    dz_values1 = []
    for r1 in range(len(mac)):
        for c1 in range(len(mac[0])):
            dz_values1.append(mac[r1][c1])
            x_values1.append(r1)
            y_values1.append(c1)
            # print(1)
    
    ax5.bar3d(x_values1, y_values1, z_values1, dx1, dy1, dz_values1 )
    plt.show()
    return

def calculateMAC (phi_exp, phi_num, t_f_display):
    # function calculates MAC value between two different z mode data sets based on MAC equation
    #Inputs: 
        # - phi_exp: uses orderPhi on experimental mode data
        # - phi_num: uses orderPhi on numerical mode data
        # - t_f_display
    MAC_matrix = np.zeros((len(phi_exp),len(phi_num)))
    for i in range(len(phi_num)):
        for j in range(len(phi_exp)):
            t1 = np.matmul(np.transpose(phi_num[i,:]),phi_exp[j,:])
            t2 = np.matmul(np.transpose(phi_num[i,:]),phi_num[i,:])
            t3 = np.matmul(np.transpose(phi_exp[j,:]),phi_exp[j,:])
            
            MAC_matrix[i,j] = (abs(t1)**2)/(t2 * t3) #check if this is even the right equation
    
    if t_f_display == True: 
        plotMAC(MAC_matrix)
    return MAC_matrix


def singleMAC(phi_e, phi_n):
    # calculates a single MAC value for a single frequecy pair of experimental and numerical z mode values 
    #Inputs: 
        # - phi_e: uses orderPhi on experimental mode data
        # - phi_n: uses orderPhi on numerical mode data    
    phi_e = np.reshape(phi_e, (len(phi_e),1)) #LONGEST DIMENSION HAS TO BE ON INSIDE TO RESULT IN SINGLE NUMBER
    phi_n = np.reshape(phi_n, (len(phi_n),1)) #[1 x 13] * [13 x 1] = 1x1 element

    n1 = abs(np.matmul(np.transpose(phi_n), phi_e))**2
    n2 = np.matmul(np.transpose(phi_n),phi_n)
    n3 = np.matmul(np.transpose(phi_e), phi_e)
    MAC_n = n1/(n2*n3)
    return MAC_n 
                


#==========================================Call orderPhi function============================#


#Note First set is blue, second is red 





# -------- Full MAC (not using automated grid sorting function)-------

# for ua in range(len(exp_modes_norm[0])):
#     plotGraphs(exp_modes_norm[:,ua,0],exp_modes_norm[:,ua,1],exp_modes_norm[:,ua,2], working_matrix[:,ua,0], working_matrix[:,ua,1], working_matrix[:,ua,2])



#----------------Manually Sorted MAC----------------------
#num
if manual_mac_display == True: 
    for ua0 in range(len(working_matrix)):
        plotGraphs(exp_modes_norm_vis[:,ua0,0],exp_modes_norm_vis[:,ua0,1],exp_modes_norm_vis[:,ua0,2], working_matrix[:,ua0, 0],working_matrix[:,ua0, 1],working_matrix[:,ua0, 2])
working_matrix = np.delete(working_matrix, [3,4,5], axis = 2)
working_matrix = orderPhi(working_matrix, manual_good_exp_freq)

#exp
exp_modes_norm = np.delete(exp_modes_norm, deleted_exp_freq, axis = 1)
exp_modes_norm = orderPhi(exp_modes_norm, freq_allowed)

xhale_mac = calculateMAC(working_matrix, exp_modes_norm, manual_mac_display)



#-------------Individual MAC for beam -------------------#
# num orderPhi
self_mac_rgf = np.delete(self_mac_rgf, [3,4,5], axis = 2) #deletes rotational data (x rot,y rot,z rot)
self_mac_phi = orderPhi(self_mac_rgf, freq_allowed_self_v1)

#exp orderPhi
exp_modes_norm_self = np.delete(exp_modes_norm_self, deleted_exp_freq_self_v1, axis = 1)
exp_modes_norm_mod = orderPhi(exp_modes_norm_self, individual_exp_freq)

individual_mac = singleMAC(self_mac_phi, exp_modes_norm_mod)

if individual_mac_display == True:
    plotGraphs(self_mac_rgf[:,0,0],self_mac_rgf[:,0,1],self_mac_rgf[:,0,2], exp_modes_norm_self[:,0,0],exp_modes_norm_self[:,0,1],exp_modes_norm_self[:,0,2])
    print('Indivdual MAC of Exp Indicy ' + str(freq_allowed_self_v1) + ' and Exp Indicy ' + str(individual_exp_freq) + ': ' + str(individual_mac))

#-------------Individual MAC for beam -------------------#
# ind_beam_num = orderPhi(beam_edited, [7]) # @3.28 hz 
# mac_number = singleMAC(za1, ind_beam_num)
# # print(mac_number)



#------------------Full Mac for beam-------------------------#

# exp phi beam
beam_exp_full = np.delete(beam_exp_full, deleted_exp_beam_total, axis = 1 ) #deletes the extra experimental modes
beam_exp_full = orderPhi(beam_exp_full, good_exp_beam_data)
#numerical phi beam
beam_num_edited_full  = orderPhi(beam_num_edited_full, freq_allowed_beam_total)
beam_MAC = calculateMAC(beam_exp_full, beam_num_edited_full, beam_mac_display)

if full_mac_beam_display == True: #displays mode data if user wants it to appear, also shows mac 3d bar chart
    for ua2 in range(len(beam_exp_full[0])):
        plotGraphs(beam_exp_full_vis[:,ua2,0],beam_exp_full_vis[:,ua2,1],beam_exp_full_vis[:,ua2,2], num_mode_beam_vis[:,ua2,0],num_mode_beam_vis[:,ua2,1], num_mode_beam_vis[:,ua2,2])
# calculate the mac of the beam 
beam_MAC = calculateMAC(beam_exp_full, beam_num_edited_full, beam_mac_display)



# check_MAC_large = calculateMAC(beam_exp_full, beam_num_edited_full)

# Normalization at line 504

    # ------Temporary use of singleMac function-----


#-------------------------------------------------------------#
# ============================== end orderPhi section ==========================================


#-------Call calculateMAC function --------#
#DUMMY MAC
# dummy_matrix = np.random.randint(10,size = (15,7))
# test_v1 = calculateMAC(dummy_matrix, dummy_matrix)


# #Total MAC Test
# test_v2 = calculateMAC(np.transpose(working_matrix),np.transpose(working_matrix))
# # test_v2 = calculateMAC(np.transpose(exp_modes_norm),np.transpose(working_matrix))
# #Note that exp_modes_norm needs to be adjusted to delete certain experimental freq

# #Individual MAC mode 1
# exp_modes_norm_mod = np.reshape(exp_modes_norm_mod, (1,len(exp_modes_norm_mod)))
# self_mac_phi = np.reshape(exp_modes_norm_mod, (1,len(self_mac_phi)))

# test_v3 = calculateMAC(np.transpose(exp_modes_norm_mod),np.transpose(self_mac_phi)) #test with different mode or with opposite modes+


#!!!!!!!!!!! reminder plot matched grid indicies as proof
#------End Call calculateMAC function ------#


#----------------Beam section MAC Functions ---------------



#####################Torrence Notes######################


# Newest notes: 
    # as long as you find the abs value you should be able to retain the shape 

# read plot 
# remove the abs value (put thought into this)
# for i in range(len(mode_shapes_normalized)):
#         mode_shapes_normalized[:][:][i] = np.divide(mode_shapes_normalized[:][:][i]\
#         ,np.max(np.max(np.abs(mode_shapes_normalized[:][:][i]))))


# first value of mac is falsely inflated somehow. za1 is higher than it should be







######################Bilal Notes############################
#run this with beam test data to ensure that it is as generalized a possible (non linear beam test files)
#look into TOR and XOR test methods from NASATRAN 
#you can manipulate data from nastran output (from bdf input file)
#use experimental analytical mass matrix 

#given a model and given a mass matrix how to do you peform TOR and XOR. Look into NASA and other papers 
    # bilal wants a suite and we can run it based on user desired tests 
    #tell bilal if he is missing anything !!!!!!!!!!
        #will probably need to have more info for tor and xor comparison matrix 


#compare only the z components (third component)

#function to compare experimental frequencies with numerical frequencies

################################################################



# ========================Unused CODE SECTION ======================================#
#------- PSEUDOCODE-----
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
#--------End of PSEUDOCODE---------


#def sortFrequencies (numericalData, experimentalData):
#experimentalData = exp_data['exp_freq']
                            # numericalData = num_data['freq_NASTRAN_out']
                            # numericalData = np.delete(numericalData,[0,1,2],1)
                            # freqIndicies = []
                            # for exp in range(len(experimentalData[0])):
                            #     for num in range(len(numericalData[0])):
                            #         version1 = (abs(numericalData[0][num] - experimentalData[0][exp]))/(experimentalData[0][exp])
                            #         if (num+1) < len(numericalData[0]):
                            #             version2 = (abs(numericalData[0][num+1] - experimentalData[0][exp])/(experimentalData[0][exp]))
                            #         else:
                            #             version2 = 3
                            #         if (version1 < version2) and (version1 < 0.25): #version less than 25%
                            #             freqIndicies.append(num)
                            #             break
#    return freqIndicies
#might try using three check version, the problem with this one is that if the 2nd entry after the search point is larger, then the code will not work  

# for kami_sec in range(len(beam_exp_full[0])): # You have to make sure that number of numerical frequencies and number of experimental frequencies match
#     beam_exp_full[:,kami_sec,2] = beam_exp_full[:,kami_sec,2]*exception_flip_z[kami_sec] + 0.67 #see how this alters code
#     #grad3D would have been called here  #The beam offset (above would have made it easier to compare the num and exp after being flipped, Bilal and I determined it should no longer be applied because it would throw off the MAC calculations)
# # print(beam_exp_full[:,1,2])



#grad3D was supposed to be called to correct mode shapes flipped over the x axis, but turned out to not be useful because it could not be applied uniformly to all modes
# def grad3D (num_x, num_y, num_z,exp_x,exp_y,exp_z):

#     abs_exp_z = []
#     abs_num_z = []
#     for trudy in range(len(exp_z)):
#         abs_exp_z = np.append(abs_exp_z,abs(exp_z[trudy]))
    
#     for trudy2 in range(len(num_z)):
#         abs_num_z = np.append(abs_num_z,abs(num_z[trudy2]))
    
#     cond_1 = np.where(abs_exp_z > 0, abs_exp_z, np.inf).argmax() #finds the maximum possible value (even if negative and returns index)
#     cond_2 = np.where(abs_num_z > 0, abs_num_z, np.inf).argmax()
#     # take both max negative and max positve, compare absolute value
#     if exp_z[cond_1] < 0 and num_z[cond_2] > 0:
#         for tamper1 in range(len(exp_z)):
#             exp_z[tamper1] = -1*exp_z[tamper1]    
    
#     if exp_z[cond_1] > 0 and num_z[cond_2] < 0:
#         for tamper2 in range(len(exp_z)):
#             exp_z[tamper2] = -1*exp_z[tamper2]
    

#     plotGraphs(exp_x,exp_y,exp_z,num_x,num_y,num_z)
#     return exp_x, exp_y, exp_z


#===================================================Bilal Prior Code======================================#
 # ------Bilal hard coded the grids in this section to reflect the grids points used in experiment (try to code this differently) /T
                #num_file = 'beam_num_data_out.mat'
                #exp_file = 'beam_exp_data.mat'
                
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
                
                #------End of Hardcoded Bilal Section --------#
                

                #----Bilal Section -----#
                #mode_appended = []
                # for freq2 in range(0,25):
                #    for freq2 in range(0,6):
                #        mode_appended = num_data['num_mode_shapes'][0][0]
                
                
                #         -----set aside point to make add the two arrays together to avoid reference issues later /T
                # len(num_data['num_mode_shapes']) = 1
                #grids_uni_le_te.astype(int)
                #num_data['grids'].astype(int)
                
                # have not modified anything after this
                  #  mode_test = np.delete(mode_shapes_reduced_total[mode][dof], np.asarray(int_2_remove))  
                  
                #-------------End of Bilal Section-------------------- #




