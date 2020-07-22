clear;
load('NASTRAN_mode_shapes_out.mat'); 
load('xhale_exp_data.mat'); 
figure(1);
scatter3(exp_coordinates(1,:), exp_coordinates(2,:),exp_coordinates(3,:))
hold on
comp = num_coordinates + num_mode_shapes{1,2}(1:3,:);
epipen = num_mode_shapes{1,2}(1:3,:);
scatter3(comp(1,:),comp(2,:),comp(3,:))

hold off
%legend('experimental data', 'numerical data'); 
xlabel('width(X)');
ylabel('length(y)');
zlabel('height(Z)')

x_num = comp(1,:);
y_num = comp(2,:);
z_num = comp(3,:);

grids = double(grids);
[sortedY, sortIndexY] = sort(y_num); 
sortedX = x_num(sortIndexY); 
sortedZ = z_num(sortIndexY); 
sortedgrids = grids(sortIndexY); 

sorted_coords_grids_num = [sortedX;sortedY;sortedZ; sortedgrids]; 

exp_x = exp_coordinates(1,:); 
exp_y = exp_coordinates(2,:); 
exp_z = exp_coordinates(3,:); 

[sort_expY, sort_expIndexY] = sort(exp_y); 
sort_expX = exp_x(sort_expIndexY); 
sort_expZ = exp_z(sort_expIndexY); 

sorted_coords_grids_exp = [sort_expX; sort_expY;sort_expZ;(36.0:-1.0:1.0)];


figure(2)
scatter3(exp_mode_shapes_normalized(1,1,:),exp_mode_shapes_normalized(1,2,:),exp_mode_shapes_normalized(1,3,:))
xlabel('X-axis'); 
ylabel('Y-axis'); 
zlabel('Z-axis'); 
%% Matching coordinates to their experimental counterparts
% Numerical coordinates matched with there Experiment Counter Parts
% Exp. Node      Numerical Node    Exp Coordinates        Numerical Coordinaes
%   3               [15420]      (-0.05756,2.985,1.13)   (-0.05754,2,847,0.5326)
%   1               [15020]       (0.01762, 2.985,1.13)    (2.223e-5,2.847, 0.5326)
%   2               [15220]     (0.1424,2.985,1.13)     (0.1424,2.847,0.5326) 
%                                                                                           
%   6               [15416]     (0.05756, 2.492,0.855)  (-0.05755, 2.508,0.3201)
%   4               [15016]     (0.01762, 2.492,0.855)  (1.129e-5, 2.508,0.3201)                                                                                    
%   5               [15216]     (0.1424, 2.492,0.855)   (0.1425, 2.508, 0.3201) 
%   7               [14004]     (0.6572,2.24,0.6944)    (0.6586, 2.222, 0.08077)                                                                       
%  
%   10              [10420]     (-0.05756, 2, 0.58)      (-0.05756, 2, 0)                                                                     
%   8               [10002]     (0.01762, 2, 0.58)       (0, 2, 0)                                                                
%   9               [10220]     (0.1424, 2, 0.58)        (0.1424, 2, 0)                                                           
%   11              [13004]     (0.6572, 1.76, 0.4656)   (0.6555, 1.76, -0.1025)                                                                                                
%                                                                                                                   
%   12              [9003]      (0.6572, 1.24,0.25)      (0.6579,1.238,-0.3167)                                                                               
%                                                                                       
%   15              [5419]      (-0.05756, 1, 0.18)      (-0.05762, 0.9692, -0.3816)                                                                            
%   13              [5402]      (0.01762, 1, 0.18)       (-4.12e-5, 1.046, -0.3601)                                                                                
%   14              [5220]      (1.424, 1, 0.18)         (0.1424, 1.066, -0.3549)                                                              
%   16              [8004]      (0.6572,0.76,0.11)       (0.6557,0.836,-0.4372)
%                                                                            
%   20              [16411]     (-0.05756, 0, 0)         (-0.05771, -0.01882, -0.5087)                                                                              
%   17              [16011]     (0.01762, 0,0)           (-0.000152,-0.01883,-0.509) *worried this is missplaced in plane width (x dim)                                                                                                
%   19              [16211]     (0.1424, 0, 0)           (0.1423, -0.01887, -0.5098)
%   18              [4005]      (0.966, 0, 0.24)         (0.9741, 0.08117, -0.3066)                                                                                                  
%                                                                                                           
%   11              [19003]     (0.6572, -0.76, 0.11)    (0.6559, -0.7312, -0.4202)                                                                                                    
%                                                                                                                                           
%   24              [21411]     (-0.05756, -1, 0.18)     (-0.05759, -0.9984,-0.3241)
%   22              [21011]     (0.01762, -1, 0.18)      (-2.739e-5, -0.9985,-0.3243)
%   23              [21211]     (0.1424, -1, 0.18)       (0.1424, -0.9986,-0.3247)
%   21              [19002]     (0.6572, -0.76, 0.11)    (0.6562, -0.7887, -0.403)                                                                                    
%                                                                                                           
%   29              [26412]     (-0.05756, -2, 0.58)     (-0.05756, -2.007, 0.107)
%   27              [26012]     (0.01762, -2, 0.58)      (2.213e-6, -2, 0.58)                                                                                                          
%   28              [26212]     (0.1424, -2, 0.58)       (0.1424, -2.007, 0.107)                                                                                                                    
%   26              [24001]     (0.6572, -1.76, 0.4656)  (0.6566, -1.782, -0.03442)                                                                                                    
%   
%   33              [26418]     (-0.05756, -2.492, 0.855) (-0.05754,-2.5148,0.4263)                                                                                                                   
%   31              [26018]     (0.01762, -2.492,0.855)  (1.592e-5, -2.515,0.4263)                                                                                                                       
%   32              [26218]     (0.1424, -2.492, 0.855)   (0.1425, -2.515, 0.4263                                                                                        
%                                                                                                                               
%   30              [25004]     (0.6572, -2.24,0.6944)    (0.6587,-2.06,0.08008)
%   ------These three are closest approximations. Significant difference in y-position -------------------------------
%
%   36              [26420]     (-0.05756, -2.985, 1.13)    (-0.05754, -2.684, 0.5327)
%   34              [26020]     (0.01762, -2.985, 1.13)     (2.122e-5, -2.684, 0.5327)
%   35              [26220]     (0.1424, -2.985, 1.13)      (0.1425, -2.684, 0.5327)
%
%                                                                                           
