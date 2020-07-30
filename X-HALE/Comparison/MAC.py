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





#==========================================Load Data Section ==========================================================
num_file = 'NASTRAN_mode_shapes_out.mat'
exp_file = 'xhale_exp_data.mat'

exp_data = sio.loadmat(exp_file)
num_data = sio.loadmat(num_file)





#-------Data for Undeformed Test Case  --------#
file_name = 'gvt1all_copy.unv'
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



#------Data for Non Uniform Case-------#
num_file_beam = 'beam_num_data_in_copy.mat'
exp_file_beam = 'beam_exp_data_copy.mat'

num_data_beam = sio.loadmat(num_file_beam)
exp_data_beam = sio.loadmat(exp_file_beam)

# ==============================================================================================================






#====================================Grid and Frequency Section==================================================

#-------------Dummy case-----------------#
#exp_coordinates_x_adjusted = exp_data['exp_coordinates'][0] + 1.83  #Leftover from previous GVT beam test
#grids_uni_le_te = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,22,23,24,25,31,61,92,122,153,183,214,244,275,305,336] #Dummy indexes for grids and 
#freq_allowed = [0, 1, 2, 3, 4, 5, 6, 7, 9, 14, 24]
    # -----------end dummy case-----------------#


# ------------Manually Sorted XHALE --------------------------#

# identify grid coordinates in the numerical analysis corresponding to
# --------accelerometer locations Manually sorted --------#
grids_uni_le_te = [15420, 15020, 15220, 15416, 15016, 15216, 14004, 10420, 10002, 10220, 13004, 9003, 5419, 5402, 5220, 8004, 16411, 16011, 16211, 4005, 19003, 21411, 21011, 21211, 19002, 26412, 26012, 26212, 24001, 26418, 26018, 26218, 25004, 26420, 26020, 26220]

#-----Frequencies allowed manually sorted-------#
#freq_allowed = [5,6,7,10,11,12,17,18,19,20,21] #PLEASE NOTE THESE ARE INDICIES. STILL FIXING THE REDUCTION FREQUENCY FUNCTION
freq_allowed = [6, 8, 12, 13, 19, 20 ]#revised freq_allowed from bilal data (entry 1 does not have correlary. Entry 3 is improper correlary, closest match is index 8)
deleted_exp_freq = [0,3,4,7,9] #indicies of ignored experiment frequencies
    #---------- end freq allowed manually sorted------#

    #----------------End of Manually Sorted --------------------#


#------------Individual MAC first Mode Freq not allowed-----------------#
freq_allowed_self_v1 = [6] #input the frequencies correllating to the NUMERICAL allowed frequency index 
deleted_exp_freq_self_v1 = [0,2,3,4,5,6,7,8,9,10] #testing first fundamental modes at 1.01 exp freq

print(grids_uni_le_te)
print(freq_allowed)

    #-----------End of Individual Mac first Mode -------------------------#


#------------Frequencies allowed for beam data 
freq_allowed_beam_total = [7,8,9,10,12,13]
deleted_exp_beam_total = [0,3,5,6,9,10,11,12,13,15]
exception_list = [0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
exception_flip_z = [1,-1,-1,1,-1,-1]



# =====================================================================================================================





#====================================Preprocessing for data + Reshaping===========================================

#--------  Read In/ Transposing XHALE Num Data-------------
#import numerical and experimental data
#mode_shapes_reduced = np.reshape(num_data['num_mode_shapes'][0][0], 25, 6, 348)  #need to reshape this matrix so isn't a single row vector
mode_shapes_reduced = num_data['num_mode_shapes'][0][0]
all_grids = num_data['grids'][0]
exp_modes_norm = exp_data['exp_mode_shapes_normalized']

print('The size of the working mode matrix is currently ' + str(np.shape(mode_shapes_reduced)))

#note also had to transpose the non-deformed state as well deformed state and experimental data
mode_shapes_reduced_part = np.transpose(num_data['num_mode_shapes'][0][1],(1,0))
mode_shapes_reduced_total = mode_shapes_reduced.transpose((2, 0, 1)) 
exp_modes_norm = exp_modes_norm.transpose((2, 0, 1)) 
exp_modes_norm_self =exp_modes_norm.copy()

#this changes the original axis formation from axis 0 , 1, 2 to axis 2, 0, 1 via transpose function /T
#new dimensions are 384 sheets of 25 x 6 arrays matching the original Matlab Script and Format /T
# ----- Adding Static + Deformd data (Numerical )------# (Deformed Numeric Shape)

#XHALE (Numeric)
#adds the two cells together static defomation to coordinates
for beta in range(len(mode_shapes_reduced_total)):  #so typically I would just modify mode_shapes_reduced_total but it is getting wonky for some reason  so i duplicated it for manipulation
   for charlie in range(len(mode_shapes_reduced_total[0])):
       mode_shapes_reduced_total[beta][charlie] = np.add(mode_shapes_reduced_total[beta][charlie] , mode_shapes_reduced_part[beta])
print('The size of the working matrix is now ' + str(np.shape(mode_shapes_reduced_total)))

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
    return

class compGrid: 
    #creates class that is easy to sort based upon y coordinate with attached x coordinate and grid ID number
    def __init__ (self, y_comp, x_comp, gridID, z_comp, y_tol, x_tol):
        self.y = y_comp
        self.x = x_comp
        self.g = gridID
        self.z = z_comp
        self.yt = y_tol
        self.xt = x_tol


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
       #!!!!!! Work on tomorrow Just get rid of x values because that is where the weak point is. You already have a decent y sift
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
            


#========================Section to call organizeGrids function ========================================#


num_sim_static_coords = np.delete(num_data['num_mode_shapes'][0][1],[3, 4, 5], axis = 0)
num_sim_static_coords = np.add(num_sim_static_coords, num_data['num_coordinates'])


# Static Case Deformed ('U' Shape)
grids_matched_def = []
grids_matched_def = organizeGrids(num_sim_static_coords[1,:],num_sim_static_coords[0,:],num_sim_static_coords[2,:], all_grids, exp_data['exp_coordinates'][1], exp_data['exp_coordinates'][0], exp_data['exp_coordinates'][2])


#Static Case Undeformed ('Flat' Shape) 
grids_matched_static_test = []
grids_matched_static_test = organizeGrids(num_data['num_coordinates'][1], num_data['num_coordinates'][0],num_data['num_coordinates'][2], all_grids, coordinates_exp[1], coordinates_exp[0], coordinates_exp[2])
                                #Find out if I used the proper coordinates as before. Trying to find the grid points from gvt1all section, but it is difficult


#------------Non-Uniform Beam Case -----------------#
averaged_x, averaged_y, averaged_z = beamAverage(exp_data_beam['exp_coordinates'][0,:],exp_data_beam['exp_coordinates'][1,:],exp_data_beam['exp_coordinates'][2,:],0)
temp_add_x = num_data_beam['num_coordinates_in_with_def'][0] - 1.83
temp_add_z = num_data_beam['num_coordinates_in_with_def'][2] + 0.53285
grids_matched_beam = []
grids_matched_beam  = np.asarray(organizeGrids(num_data_beam['num_coordinates_in_with_def'][1],temp_add_x, temp_add_z ,num_data_beam['grids'][0], averaged_y, averaged_x ,averaged_z ))

#----Visualization of raw exp beam coordinate data with beam coordinate data of static def + coord------
# fig2 = plt.figure()
# ax2 = fig2.add_subplot(111, projection='3d')

# ax2.scatter(num_data_beam['num_coordinates_in_with_def'][0] - 1.83,num_data_beam['num_coordinates_in_with_def'][1],num_data_beam['num_coordinates_in_with_def'][2] + 0.53285 , c='r', marker='o')
# #ax2.scatter(exp_data_beam['exp_coordinates'][0,:],exp_data_beam['exp_coordinates'][1,:],exp_data_beam['exp_coordinates'][2,:], c='b', marker='o')
# ax2.scatter(averaged_x, averaged_y, averaged_z, c='g', marker='o')

# ax2.set_xlabel('X Label')
# ax2.set_ylabel('Y Label')
# ax2.set_zlabel('Z Label')
#---------------End of Visualization------------------





            #--------------debugging section to adjust height and span position of numerical data---------------
            # check_length = list()
            
            # for tango in range(len(num_data_beam['num_coordinates_in_with_def'][1,:])):
            #     check_length.append(compGrid(num_data_beam['num_coordinates_in_with_def'][1,tango],num_data_beam['num_coordinates_in_with_def'][0,tango],None, num_data_beam['num_coordinates_in_with_def'][2, tango], None, None))
            
            # check_length = sorted(check_length, key = lambda compGrid: compGrid.z)
            # total_length = abs(check_length[0].z - check_length[-1].z)
            
            # print('Total height of numeric is ' + str(total_length))
            
            # check_length2 = list()
            # for tango2 in range(len(exp_data_beam['exp_coordinates'][1,:])):
            #     check_length2.append( compGrid(exp_data_beam['exp_coordinates'][1,tango2], exp_data_beam['exp_coordinates'][0,tango2],None, exp_data_beam['exp_coordinates'][2,tango2],None,None))
            
            # check_length2 = sorted(check_length2, key = lambda compGrid: compGrid.x)
            # total_length_2 = abs(check_length2[0].x - check_length2[-1].x)
            # print('Total length of exp is ' + str(total_length_2))
            
            # Height of experimental +0.557 minus the version above zero 0.02415504. Total height of z added to num is 0.53285. Add 1.83 to x
            #---------------Be sure this is centered correctly ------------------------#
# ===================================================================================================================

#============================Section to add Mode amplitude with their coordinates+deformation========================#


# --------------      ----------------  XHALE ---------------  -----------------
#debug section
# pelican1 = num_sim_static_coords.copy()
# pelican2 = exp_data['exp_coordinates'].copy()

#--------Adding Mode amplitude to NUMERICAL u-shape coordinates 
for igloo in range(len(mode_shapes_reduced_total)): 
    for jacob in range(len(mode_shapes_reduced_total[0])):
        mode_shapes_reduced_total[igloo,jacob,0] = mode_shapes_reduced_total[igloo,jacob,0] + num_sim_static_coords[0,igloo] #x component
        mode_shapes_reduced_total[igloo,jacob,1] = mode_shapes_reduced_total[igloo,jacob,1] + num_sim_static_coords[1,igloo] #y component
        mode_shapes_reduced_total[igloo,jacob,2] = mode_shapes_reduced_total[igloo,jacob,2] + num_sim_static_coords[2,igloo] #z component

#debug section
#plotGraphs(mode_shapes_reduced_total[:,6,0],mode_shapes_reduced_total[:,6,1],mode_shapes_reduced_total[:,6,2],pelican1[0,:],pelican1[1,:],pelican1[2,:])


#---------Adding mode aplitude to EXPERIMENTAL u-shape coordinates Entire MAC
for igloo2 in range(len(exp_modes_norm)):
    for jacob2 in range(len(exp_modes_norm[0])):
        exp_modes_norm[igloo2,jacob2,0] = exp_modes_norm[igloo2,jacob2,0] + exp_data['exp_coordinates'][0][igloo2] 
        exp_modes_norm[igloo2,jacob2,1] = exp_modes_norm[igloo2,jacob2,1] + exp_data['exp_coordinates'][1][igloo2] 
        exp_modes_norm[igloo2,jacob2,2] = exp_modes_norm[igloo2,jacob2,2] + exp_data['exp_coordinates'][2][igloo2] 
        #exp_modes_norm[igloo2,jacob2,:] =  exp_modes_norm[igloo2,jacob2,:] + exp_data['exp_coordinates'][:,igloo2]

#debug section
#plotGraphs(exp_modes_norm[:,1,0],exp_modes_norm[:,1,1],exp_modes_norm[:,1,2],pelican2[0,:],pelican2[1,:],pelican2[2,:])

#---------Adding mode aplitude to EXPERIMENTAL u-shape coordinates Individual MAC (This is just a precaution in case code is manipulated above)
for igloo3 in range(len(exp_modes_norm_self)):
    for jacob3 in range(len(exp_modes_norm_self[0])):
        # exp_modes_norm_self[igloo3,jacob3,0] = exp_modes_norm_self[igloo3,jacob3,0] + exp_data['exp_coordinates'][0][igloo3] 
        # exp_modes_norm_self[igloo3,jacob3,1] = exp_modes_norm_self[igloo3,jacob3,1] + exp_data['exp_coordinates'][1][igloo3] 
        exp_modes_norm_self[igloo3,jacob3,:] = exp_modes_norm_self[igloo3,jacob3,:] + exp_data['exp_coordinates'][:,igloo3] 



#--------       ------------- Beam section: Add Mode to beam coord data-------------   ----------------

#----Experimental data ---------------
for juliet in range(len(exp_mode_beam)):
    for kilo in range(len(exp_mode_beam[0])):
        exp_mode_beam[juliet,kilo,0] = exp_mode_beam[juliet,kilo,0] + exp_beam_coord[0,juliet]
        exp_mode_beam[juliet,kilo,1] = exp_mode_beam[juliet,kilo,1] + exp_beam_coord[1,juliet] 
        exp_mode_beam[juliet,kilo,2] = exp_mode_beam[juliet,kilo,2] + exp_beam_coord[2,juliet]

# pelican4 = num_beam_coord.copy()
# pelican4 = num_mode_beam.copy()

#--------------Numerical data --------------

#!!!!!!!!!!!!We are trying to remove the static deformation from the total beam data 

# Step 1: Separate static deformation from coord + def 
subtract_mat = np.zeros(((len(num_beam_coord)),(len(num_beam_coord[0]))))

for jackson in range(len(num_beam_coord_def[0])):
    subtract_mat[0,jackson] = num_beam_coord_def[0,jackson] - num_beam_coord[0,jackson]
    subtract_mat[1,jackson] = num_beam_coord_def[1,jackson] - num_beam_coord[1,jackson]
    subtract_mat[2,jackson] = num_beam_coord_def[2,jackson] - num_beam_coord[2,jackson]

    
# Step 2: Use this static def to remove the static def from the total modes
for hector in range(len(num_mode_beam)):
    for hector2 in range(len(num_mode_beam[0])):
        num_mode_beam[hector,hector2,0] = num_mode_beam[hector,hector2,0] - subtract_mat[0,hector]
        num_mode_beam[hector,hector2,1] = num_mode_beam[hector,hector2,1] - subtract_mat[1,hector]
        num_mode_beam[hector,hector2,2] = num_mode_beam[hector,hector2,2] - subtract_mat[2,hector]
#!!!!!!!!!this would be a good place to normalize data, wait no experimental 

plotGraphs(subtract_mat[0,:],subtract_mat[1,:],subtract_mat[2,:],num_beam_coord_def[0,:], num_beam_coord_def[1,:],num_beam_coord_def[2,:])

#===============================================end section=====================================================#





# =====================Visualization Secton for global translations and Rotations of Data==========================


#-------------- Beam Visualization of Numerical vs. Experimental data of each mode. Adjust range as neccessary. Experimental mode has options to use xa, ya, za to see the averaged data using averageBeam (averages width wise endpoints )
# plt.close('all')
# for g in range(5,9):
#     plotGraphs(num_mode_beam[:,g,0],num_mode_beam[:,g,1],num_mode_beam[:,g,2],num_data_beam['num_coordinates_in_with_def'][0,:],num_data_beam['num_coordinates_in_with_def'][1,:],num_data_beam['num_coordinates_in_with_def'][2,:])


# for g1 in range(1,2):
    # xa, ya, za = beamAverage(exp_mode_beam[:,g1,0],exp_mode_beam[:,g1,1],exp_mode_beam[:,g1,2], 0)
    # plotGraphs(xa,ya,za,num_data_beam['num_coordinates_in_with_def'][0,:],num_data_beam['num_coordinates_in_with_def'][1,:],num_data_beam['num_coordinates_in_with_def'][2,:])
    # plotGraphs(exp_mode_beam[:,g1,0],exp_mode_beam[:,g1,1],exp_mode_beam[:,g1,2],num_data_beam['num_coordinates_in_with_def'][0,:],num_data_beam['num_coordinates_in_with_def'][1,:],num_data_beam['num_coordinates_in_with_def'][2,:])
    # plotGraphs(exp_mode_beam[:,g1,0],exp_mode_beam[:,g1,1],exp_mode_beam[:,g1,2],xa,ya,za)

    
#///////////////////////Observations Beam data  //////////////////////////////
#First sin is at 1.25 hz for num beam data, Side Note: Exp data equivalent is not ideal for a MAC, move on to next highest mode
#Next portion Num index:7 (3.28 Hz)
            # Matches experimental index:1 (3.02906 hz) needs to be inverted on the x axis, multiply by negative 1?

# plotGraphs(-1*exp_mode_beam[:,1,0] + 3,exp_mode_beam[:,1,1],exp_mode_beam[:,1,2] - 0.2,num_mode_beam[:,7,0],num_mode_beam[:,7,1],num_mode_beam[:,7,2])

# Adjustments for mode num 7, exp 1: 
    # - Multiply exp by negative 1 
    # - subtract from x (-3)
    # - average the function 
    # - subtract 0.2 from z 
#CANNOT be used for global adjustments 

# First Beam Mode Results shown below 
#   #Edited, we no longer translate experimental data points (when we did we added 1.83 to x and -0.53285 to z)
xa1, ya1, za1 = beamAverage(-1*exp_mode_beam[:,1,0],exp_mode_beam[:,1,1],exp_mode_beam[:,1,2], 0)
plotGraphs(xa1, ya1, za1 ,num_mode_beam[:,7,0],num_mode_beam[:,7,1],num_mode_beam[:,7,2])
  
# //////////////////////////////////Results\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
#///////////////////////add this to num x : -1.92577\\\\\\\\\\\\\\\\\\\\\\\\\
#///////////////////////add this to num z : 0.532887\\\\\\\\\\\\\\\\\\\\\\\\\
plotGraphs(num_beam_coord_def[0,:]-1.92577,num_beam_coord_def[1,:],num_beam_coord_def[2,:]+0.532887, exp_beam_coord[0,:],exp_beam_coord[1,:],exp_beam_coord[2,:])



# ------------------Second individual MAC at 6.36 Hz (num)---------------------  

#Note!!!!!!! Only the z value matters, don't need to technically match x and y but will do anyway
#Matching num8 (6.36) with exp2 5.91 (better than going higher to num9 = 10.5652 hz )
w = 2
v = 8

#Mode 2: Edited, we no longer translate experimental data points (when we did we added 1.83 to x and multiplied by -1 for z (kept the z change)
xa2, ya2, za2 = beamAverage(exp_mode_beam[:,w,0],exp_mode_beam[:,w,1], -exp_mode_beam[:,w,2] + 0.532887 , 0)
plotGraphs(xa2, ya2, za2 ,num_mode_beam[:,v,0],num_mode_beam[:,v,1],num_mode_beam[:,v,2])



# plotGraphs(exp_mode_beam[:,w,0] + 1.7,exp_mode_beam[:,w,1],-1*exp_mode_beam[:,w,2] - 0.2,num_mode_beam[:,v,0],num_mode_beam[:,v,1],num_mode_beam[:,v,2])
plotGraphs(exp_mode_beam[:,w,0] + 1.83,exp_mode_beam[:,w,1],-1*exp_mode_beam[:,w,2] ,num_mode_beam[:,v,0],num_mode_beam[:,v,1],num_mode_beam[:,v,2])

# !!!!!!!!Can't use exp2 , num8 combo without improving beamAverage. The function does not account for overlapping x values even though divided by positive and negatie y values . Fix this later 

#----------------method to match Beam frequencies of num (coord+mode) and exp (coord+mode) data by hand --------------------------
# temporary close
tri = 14  
trid = 13
plotGraphs(-exp_mode_beam[:,tri,0],exp_mode_beam[:,tri,1],exp_mode_beam[:,tri,2],[0],[0],[0])
# print('Current Exp Frequency is ' + str(exp_data_beam['exp_freq'][0,tri]) + ' Hz')
for fifa in range(trid,trid + 5): 
    matching_mods = plt.figure()
    ax4 = matching_mods.add_subplot(111, projection='3d')
    ax4.scatter(num_mode_beam[:,fifa,0],num_mode_beam[:,fifa,1],num_mode_beam[:,fifa,2], c='b', marker='o')
    plt.title('Num Frequency of ' + str(num_data_beam['num_freq'][0,fifa]) + ' Hz')
    ax4.set_xlabel('X Label')
    ax4.set_ylabel('Y Label')
    ax4.set_zlabel('Z Label')
    ax4.set_ylim([-2,2])

#Uncomment this if you do not wish to see resulting data 
plt.close('all')
#========================================End of Visualizations===============================================================


#NUM COORD + MODE BEAM DATA IS FIRST TRANSLATED TO MEET EXPERIMENTAL COORD + MODE LOCATION (THIS IS BECAUSE EXPERIMENTAL DATA HAS GOOD PLACEMENT)
# EXPERIMENTAL DATA IS THEN MATCHED TO THE CORRECT NUM MODE SHAPE VIA ROTATION

#PSEUDOCODE FOR AUTOMATIC ZERO FUNCTION 
# will not be adjusting x and z, keep to master level 
# use min and max functions
# be sure to reduce all of the numerical nodes before feeding in data to match 
    #put after remove grid function, maybe use old frequency sift function?
# 1. use compgrid class to create and order experimental(averaged) and numerical(grid matched) data 
# 2. sort compgrid class by x, use reverse order to start at positive x 
# 3. calculate slope (x v. z) of numerical and experimental data
        #3.a if num slope is positive and exp slope is negative 
            #3.a.1 for loop adding negative sign to all z values in num values
            #store local change in matrix (add negative one to matrix)
        #3.b if num slope is negative and exp slope is positive
            # 3.b.1 for loop adding negative sign to all z values in num values 
            #store local change in matrix (add positive 1)
            
        #-----Should there be a contingency for zero slope case?-----


# !!!!!!!!!!!!!! THIS IS IN THE WRONG ORDER!!!!!! (NEED TO USE MAX IDEA, too many excetions to the slope rule)
def grad3D (num_x, num_y, num_z,exp_x,exp_y,exp_z):
    # SINGLE MODE intake the numerical data (coord+mode) and exp data (coord+mode)  and list of exception indices. Exc indicies rotate along z axis 
    #make sure to put in the averaged values and gridMatched values for the beam here    
    
    #Run through exceptions list (note I'm adjusting x data here instead of num data)
    # if exc == True :
    #     for pre_i in range(len(exp_x)):
    #         exp_x[pre_i] = -1*exp_x[pre_i]

    # #Step 1
    # exp_vals = list()
    # num_vals = list()
    # for i in range(len(exp_x)): 
    #     exp_vals.append(compGrid(exp_y[i], exp_x[i], None,exp_z[i], None, None))
    # for i2 in range(len(num_x)):
    #     num_vals.append(compGrid(num_y[i2], num_x[i2], None, num_z[i2], None, None))
    
    # # Step 2 
    # exp_vals = sorted(exp_vals, key = lambda compGrid: compGrid.x, reverse = True)
    # num_vals = sorted(num_vals, key = lambda compGrid: compGrid.x, reverse = True)
    # # Step 3 
    # slope_exp = (exp_vals[2].z - exp_vals[1].z)/(exp_vals[2].x - exp_vals[1].x) #after further review we want to avoid absolute end points because they sometimes curve inward towards the shape
    # slope_num = (num_vals[2].z - num_vals[1].z)/(num_vals[2].x - num_vals[1].x)
    
    
    # # This graph is off center relative to z, so if z has a higher negative value it is most likely off
    # if slope_num > 0 and slope_exp < 0:
    #     for tamper in range(len(exp_vals)):
    #         exp_vals[tamper].z = -1*exp_vals[tamper].z
    # if slope_num < 0 and slope_exp > 0 :
    #     for tamper2 in range(len(exp_vals)):
    #         exp_vals[tamper2].z = -1*exp_vals[tamper2].z
    # #returning exp data, not numeric data to avoid 3d matrix problem
    
    # corr_x = []
    # corr_y = []
    # corr_z = []
    
    # for m in range(len(exp_vals)):
    #     corr_x = np.append(corr_x,exp_vals[m].x)                #corected x, etcetera 
    #     corr_y = np.append(corr_y,exp_vals[m].y)
    #     corr_z = np.append(corr_z,exp_vals[m].z)
    abs_exp_z = []
    abs_num_z = []
    for trudy in range(len(exp_z)):
        abs_exp_z = np.append(abs_exp_z,abs(exp_z[trudy]))
    
    for trudy2 in range(len(num_z)):
        abs_num_z = np.append(abs_num_z,abs(num_z[trudy2]))
    
    cond_1 = np.where(abs_exp_z > 0, abs_exp_z, np.inf).argmax() #finds the maximum possible value (even if negative and returns index)
    cond_2 = np.where(abs_num_z > 0, abs_num_z, np.inf).argmax()
    # take both max negative and max positve, compare absolute value
    if exp_z[cond_1] < 0 and num_z[cond_2] > 0:
        for tamper1 in range(len(exp_z)):
            exp_z[tamper1] = -1*exp_z[tamper1]    
    
    if exp_z[cond_1] > 0 and num_z[cond_2] < 0:
        for tamper2 in range(len(exp_z)):
            exp_z[tamper2] = -1*exp_z[tamper2]
    

    plotGraphs(exp_x,exp_y,exp_z,num_x,num_y,num_z)
    return exp_x, exp_y, exp_z





# focus --> remove grid location points first (reduce from 348 sheets) then reduce frequencies from 25 to 12ish i think /T
#modes_shapes_reduced_total defined above is just put aside here so it does not manipulate code 
def remove_Grid_Freq (total_grids, mode_shapes_reduced_dummy, freq_we_want, grids_we_want):
    #total_grids = total_grids.astype('int32')

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
#///////////////////////add this to num x : -1.92577\\\\\\\\\\\\\\\\\\\\\\\\\
#///////////////////////add this to num z : 0.532887\\\\\\\\\\\\\\\\\\\\\\\\\

    

# !!!!!!!!!!!!!!!!!!!!!!!!!Global Readjustment to experimental data locatio DO NOT TOUCH!!!!!!!!!!!!!!!!!!!!!!!!!!!!
num_mode_beam[:,:,0] = num_mode_beam[:,:,0] - 1.92577 
num_mode_beam[:,:,2] = num_mode_beam[:,:,2] + 0.532887
# !!!!!!!!!!!!!!!!!!!!!!!!!Global Readjustment to experimental data locatio DO NOT TOUCH!!!!!!!!!!!!!!!!!!!!!!!!!!!!


beam_exp_full = np.zeros((int(len(exp_mode_beam)/2),len(exp_mode_beam[0]),len(exp_mode_beam[0,0])))
for kami in range(len(exp_mode_beam[0])):
    if exception_list[kami] == True:
        temp_av_x, temp_av_y, temp_av_z = beamAverage(-1*exp_mode_beam[:,kami,0],exp_mode_beam[:,kami,1],exp_mode_beam[:,kami,2], 0)
    else: 
        temp_av_x, temp_av_y, temp_av_z = beamAverage(exp_mode_beam[:,kami,0],exp_mode_beam[:,kami,1],exp_mode_beam[:,kami,2], 0)
    beam_exp_full[:,kami,0] = temp_av_x 
    beam_exp_full[:,kami,1] = temp_av_y 
    beam_exp_full[:,kami,2] = temp_av_z 

print(beam_exp_full[:,1,2])




# =======================================end section ==========================================================











#======================Section to call remove_Grid_Freq functions =============================#

#-------dummy case XHALE-----------#
working_matrix = remove_Grid_Freq(all_grids, mode_shapes_reduced_total,freq_allowed, grids_uni_le_te )
#print('The working dummy matrix has now been reduced to a size of ' + str(np.shape(working_matrix)))
    #-----end dummy case------#

#---------- Self MAC first mode case (for individual MAC case) Note we need to add -0.509 to the z coordinates of the xhale and 
self_mac_rgf = remove_Grid_Freq( all_grids,mode_shapes_reduced_total,freq_allowed_self_v1 ,grids_matched_def )


#----------Remove grid beam ------------------#

#individual MAC 3.28 hz num
beam_edited = remove_Grid_Freq(np.reshape(num_data_beam['grids'],(len(num_data_beam['grids'][0]),1)),num_mode_beam, [7], list(grids_matched_beam))
#note in this process re are reducing modes BEFORE they are matched to modes

#individual MAC 6.36 hz num
beam_edited2 = remove_Grid_Freq(np.reshape(num_data_beam['grids'],(len(num_data_beam['grids'][0]),1)),num_mode_beam, [8], list(grids_matched_beam))

#full mac of non uniform beam
beam_num_edited_full = remove_Grid_Freq(np.reshape(num_data_beam['grids'],(len(num_data_beam['grids'][0]),1)),num_mode_beam, freq_allowed_beam_total , list(grids_matched_beam))

# if statement about numerical and experimental frequencies matching (use quit() command)


# -------------Former (Special grad3D section) EDITED Additional processing  -------------------
beam_exp_full = np.delete(beam_exp_full, deleted_exp_beam_total, axis = 1 ) #deletes the extra experimental modes

for kami_sec in range(1,(len(beam_exp_full[0]))): # You have to make sure that number of numerical frequencies and number of experimental frequencies match
    # reworked_x,reworked_y, reworked_z = grad3D(beam_num_edited_full[:,kami_sec,0],beam_num_edited_full[:,kami_sec,1],beam_num_edited_full[:,kami_sec,2],beam_exp_full[:,kami_sec,0],beam_exp_full[:,kami_sec,1],beam_exp_full[:,kami_sec,2])
    # beam_exp_full[:,kami_sec,0] = reworked_x
    # beam_exp_full[:,kami_sec,1] = reworked_y
    if exception_flip_z[kami_sec] == -1:
        beam_exp_full[:,kami_sec,2] = beam_exp_full[:,kami_sec,2]*exception_flip_z[kami_sec] + 0.8

print(beam_exp_full[:,1,2])


# =================================end section=========================================
 

#==============Additional Visualisation to check if grad3D worked=======================
plt.close('all')
for cypher in range(len(beam_exp_full[0])):
    plotGraphs(beam_exp_full[:,cypher,0],beam_exp_full[:,cypher,1],beam_exp_full[:,cypher,2],beam_num_edited_full[:,cypher,0],beam_num_edited_full[:,cypher,1],beam_num_edited_full[:,cypher,2])
print(1)
# =======================================================================================










#Function deletes the rotational modes and creates a 2D matrix of frequencies x all measurements in one mode (every three)
def orderPhi (num_reduced_matrix, length_vec):
    #length_vec is just the length of how many frequencies we are interested in
    # a = len(length_vec)
    
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
       



#calculates the mac matrix of an experimental and numerical data set of ngrid_rows x mode freq. columns 
def calculateMAC (phi_exp, phi_num):
    MAC_matrix = np.zeros((len(phi_exp[0]),len(phi_num[0])))
    for i in range(len(phi_exp[0])):
        for j in range(len(phi_num[0])):
            t1 = np.matmul(np.transpose(phi_exp[:][i]),phi_num[:][j])
            t2 = np.matmul(np.transpose(phi_exp[:][i]),phi_exp[:][i])
            t3 = np.matmul(np.transpose(phi_num[:][j]),phi_num[:][j])
            MAC_matrix[i][j] = ((abs(t1)**2)/(t2 * t3))**0.5 #check if this is even the right equation
    mac_plot = plt.figure()
    ax1 = mac_plot.add_subplot(111, projection = '3d')
    #x_values = np.arange(0,len(MAC_matrix), 1)
    #y_values = np.arange(0,len(MAC_matrix[0]), 1)
    x_values = []
    y_values = []
    z_values = np.zeros((np.size(MAC_matrix))) #corrected
    dx = np.ones(np.size(MAC_matrix))
    dy = np.ones(np.size(MAC_matrix)) 
    dz_values = []
    for r in range(len(MAC_matrix)):
        for c in range(len(MAC_matrix[0])):
            dz_values.append(MAC_matrix[r][c])
            x_values.append(r)
            y_values.append(c)
            # print(1)
    
    ax1.bar3d(x_values, y_values, z_values, dx, dy, dz_values )
    plt.show()
    return MAC_matrix



def plotMAC(mac):
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
    

def singleMAC(phi_e, phi_n):
    phi_e = np.reshape(phi_e, (len(phi_e),1)) #LONGEST DIMENSION HAS TO BE ON INSIDE TO RESULT IN SINGLE NUMBER
    phi_n = np.reshape(phi_n, (len(phi_n),1)) #[1 x 13] * [13 x 1] = 1x1 element

    n1 = abs(np.matmul(np.transpose(phi_n), phi_e))**2
    n2 = np.matmul(np.transpose(phi_n),phi_n)
    n3 = np.matmul(np.transpose(phi_e), phi_e)
    MAC_n = n1/(n2*n3)
    return MAC_n 
                



#==========================================Call orderPhi function============================#
# Notes:
#   orderPhi reshapes the matrix into 
            #               _______every 3 translational modes ________
            #frequencies|
            #           |
            #           |



#--- call orderPhi function for Individual self MAC of XHALE-------

# num   (HAVE TO ADD 0.509 to z coordinates for XHALE)
for hotel in range(len(self_mac_rgf)):
    self_mac_rgf[hotel,0,2] = self_mac_rgf[hotel,0,2] + 0.509
    
self_mac_rgf = np.delete(self_mac_rgf, [3,4,5], axis = 2)
self_mac_phi = orderPhi(self_mac_rgf, [0])

#exp
exp_modes_norm_self = np.delete(exp_modes_norm_self, deleted_exp_freq_self_v1, axis = 1)
exp_modes_norm_mod = orderPhi(exp_modes_norm_self, freq_allowed_self_v1)

    #plotGraphs(self_mac_rgf[:,0,0],self_mac_rgf[:,0,1],self_mac_rgf[:,0,2], exp_modes_norm_self[:,0,0],exp_modes_norm_self[:,0,1],exp_modes_norm_self[:,0,2])

#Note First set is blue, second is red 





# -------- Full MAC (not using automated grid sorting function)-------
# #num
# for hotel2 in range(len(working_matrix)):
#   for hotel3 in range(len(working_matrix[0]))):
#       self_mac_rgf[hotel2,hotel3,2] = self_mac_rgf[hotel2,hotel3,2] + 0.509

working_matrix = np.delete(working_matrix, [3,4,5], axis = 2)
working_matrix = orderPhi(working_matrix, freq_allowed)

#exp
exp_modes_norm = np.delete(exp_modes_norm, deleted_exp_freq, axis = 1)
exp_modes_norm = orderPhi(exp_modes_norm, freq_allowed)


#-------------Individual MAC for beam -------------------#
ind_beam_num = orderPhi(beam_edited, [7]) # @3.28 hz 
mac_number = singleMAC(za1, ind_beam_num)
mac_number_test = singleMAC(za1,za1)
print(mac_number)
#just take the z values from the averaged beam data!!!!!!
plotGraphs (beam_edited[:,0,0],beam_edited[:,0,1],beam_edited[:,0,2], xa1,ya1,za1)

# @6.36 hz num
ind_beam_num2 = orderPhi(beam_edited2,[8])
mac_number2 = singleMAC(za2,ind_beam_num2)
print(mac_number2)

plotGraphs (beam_edited2[:,0,0],beam_edited2[:,0,1],beam_edited2[:,0,2], xa2,ya2,za2)


#------------------Full Mac for beam-------------------------#
#experimental phi
# beam_exp_full = orderPhi(beam_exp_full, np.delete((range(0,(len(exp_data_beam['exp_freq'][0])))), deleted_exp_beam_total))
beam_exp_full = orderPhi(beam_exp_full, [1,2,4,7,8,14])
#numerical phi
beam_num_edited_full  = orderPhi(beam_num_edited_full, freq_allowed_beam_total)

mac_array_beam = np.zeros((len(beam_exp_full),len(beam_num_edited_full)))
if len(beam_exp_full) == len(beam_num_edited_full):
    for final1 in range (len(beam_num_edited_full)):
        for final2 in range(len(beam_exp_full)):
            mac_array_beam[final1, final2] = singleMAC(beam_exp_full[final2,:], beam_num_edited_full[final1,:])
    plotMAC(mac_array_beam)
        

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




