# -*- coding: utf-8 -*-
"""
Created on Fri Apr 10 12:38:40 2020

@author: Bilal
"""


import numpy as np
import matplotlib.pyplot as plt
import pyuff
import os
import scipy.io as sio
import re
from mpl_toolkits.mplot3d import Axes3D
plt.close("all")

# Load the file
file_name = "OOP_inb_new_attach_0_30Hz_complex_poymax.unv"
uff_file = pyuff.UFF(file_name)

# Extract data sets
types_of_sets = uff_file.get_set_types()
data = uff_file.read_sets()

# Initialize variables for coordinates and node numbers
coordinates = []
node_number = []

# Retrieve locations of accelerometers (or nodes)
for sub in data: 
    if sub['type'] == 2411:
        coordinates = [sub['x'], sub['y'], sub['z']]
        node_number = sub['node_nums']
        break

# Initialize local coordinate systems for accelerometers
CS_accel = []
CS_labels = []
for sub in data: 
    if sub['type'] == 2420:
        CS_accel = sub['CS_matrices']
        CS_accel = [matrix[:-1, :] for matrix in CS_accel]
        CS_labels = sub['CS_sys_labels']
        break

# Connection of nodes as defined in the test software
node_connection = []
for sub in data:
    if sub['type'] == 82:
        node_connection = sub['nodes']

# Count the number of frequencies stored in the universal file
def count_freq(x):
    return sum(1 for elem in x if elem == 55)

# Initialize vectors for frequencies, mode shapes, and damping
freq_gvt = []
damp_gvt = []
mode_number = []
mode_shapes = []
node_number_eigenvector = []

# Retrieve frequencies, mode number, and damping for each mode
for sub in data: 
    if sub['type'] == 55:
        split_str = sub['id4'].split(',')
        mode_number.append(int(re.findall("\\d+", split_str[0])[0]))
        freq_gvt.append(float(re.findall("\\d+\\.\\d+", split_str[1])[0]))
        damp_gvt.append(float(re.findall("\\d+\\.\\d+", split_str[2])[0]))
        mode_shapes.append([sub['r1'], sub['r2'], sub['r3']])
        node_number_eigenvector = sub['node_nums']

# Convert mode shapes to NumPy array for complex data
mode_shapes = np.asarray(mode_shapes, dtype=np.complex64)

# Remove nodes that are not in the eigenvector node list
int_2_remove = [i for i, node in enumerate(node_number) if node not in node_number_eigenvector]
node_number = np.delete(node_number, int_2_remove)
coordinates = [np.delete(coord, int_2_remove) for coord in coordinates]

# Function to sort mode shapes according to sensor data order in unv file
def sort_mode_shapes(u_unsorted, grids, grids_order):
    u_sorted = np.csingle([np.zeros((3, len(grids_order)), dtype=np.complex64) for _ in range(len(u_unsorted))])
    for j in range(len(u_unsorted)):
        for i, grid in enumerate(grids_order):
            index = int(np.where(grids == int(grid))[0])
            u_sorted[j][:, i] = u_unsorted[j][:, index]
    return u_sorted

# Sort mode shapes according to sensor data order in unv file
mode_shapes_sorted = sort_mode_shapes(mode_shapes, node_number_eigenvector, node_number)

# Rotate mode shapes if local coordinate systems are defined
mode_shapes_rotated = np.zeros_like(mode_shapes_sorted)
if CS_accel:
    for i in range(len(freq_gvt)):
        for j in range(len(node_number_eigenvector)):
            mode_shapes_rotated[i, :, j] = np.dot(mode_shapes_sorted[i, :, j], CS_accel[j])
else:
    mode_shapes_rotated = mode_shapes_sorted

# Normalize eigenvector to have the highest value as 1
mode_shapes_normalized = np.csingle(mode_shapes_rotated)
for i in range(len(mode_shapes_normalized)):
    mode_shapes_normalized[i] /= np.max(np.abs(mode_shapes_normalized[i]))

# Prepare data for plotting eigenvectors
evec_gvt = mode_shapes_normalized.imag + [coordinates[0], coordinates[1], coordinates[2]]

# Plotting
for i in reversed(range(len(freq_gvt))):
    fig = plt.figure(figsize=(16, 9))
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(coordinates[0], coordinates[1], coordinates[2], c='k', marker='o')
    ax.scatter(evec_gvt[i][0], evec_gvt[i][1], evec_gvt[i][2])
    ax.set_ylim3d(-0.5, 0.5)
    ax.set_xlim3d(-3, 3)
    ax.set_zlim3d(-2, 2)
    ax.set_xlabel('Span [m]')
    ax.set_ylabel('Chord [m]')
    ax.set_zlabel('Vertical displacement [m]')
    plt.title(f'Mode number {i + 1} at frequency {freq_gvt[i]} Hz')
    plt.show()

# Save results in a .mat file
print("...Exporting results in a .mat file")
output_dir = os.path.dirname(os.path.abspath(__file__))
output_path = os.path.join(output_dir, "beam_exp_data.mat")
database = {
    "exp_mode_shapes_normalized": mode_shapes_normalized.imag,
    "exp_freq": freq_gvt,
    "exp_damp": damp_gvt,
    "exp_coordinates": coordinates
}
if os.path.isfile(output_path):
    os.remove(output_path)
sio.savemat(output_path, database, appendmat=False)

