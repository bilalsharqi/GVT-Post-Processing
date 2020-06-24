% MAC for wing accels
close all;
clear;

%FEMdata (evec_FEM, fn_FEM, GRIDs)
load('fullFEM_optimal.mat')

%GVT data (evec_gvt, fn_GVT, damp, node_xyz, nodeIDs_evec)
load('fullGVT_all.mat')

% 6DOF, (allFEMgrid*6*mode of interest)
% FEMevec_GRIDorder = GRIDs(:,1); % GRID IDs ordered as FEM evec

% NOTE: input
evec_FEM; % 6DOF, (allFEMgrid*6*mode of interest)
FEMevec_GRIDorder = GRIDs(:,1); % GRID IDs ordered as FEM evec
evec_GVT; % 3DOF (allGVTgrid*3*mode of interest)                            %Torrence note: Grids x 3 accels x Modes in question
nodeIDs_evec; % GVT evec-node ordering
type = 'notfull';

% pick up DOFs corresponding to GVT from FEM mode
% NOTE: no tail, no spine dof here

% name / channel / coord./ note
% U1 / 1 / [0.13, -3.0, 0.] / TE
% U2 / 2 / [0.13, -2.5, 0.] / TE
% U3 / 3 / [0.13, -1.5, 0.] / TE
% U4 / 4 / [0.13, -0.5, 0.] / TE
% U5 / 5 / [0.13,  0.0, 0.] / TE
% U6 / 6 / [0.13,  0.5, 0.] / TE
% U7 / 7 / [0.13,  1.5, 0.] / TE
% U8 / 8 / [0.13,  2.5, 0.] / TE
% U9 / 9 / [0.13,  3.0, 0.] / TE
% U11/ 11/ [0.0,  -2.0, 0.] / wingbox
% U12/ 12/ [0.13, -2.0, 0.] / TE
% U13/ 13/ [0.0,  -1.0, 0.] / wingbox
% U14/ 14/ [0.13, -1.0, 0.] / TE
% U15/ 15/ [0.0,   1.0, 0.] / wingbox
% U16/ 16/ [0.13,  1.0, 0.] / TE
% U17/ 17/ [0.0,   2.0, 0.] / wingbox
% U18/ 18/ [0.13,  2.0, 0.] / TE
% T1 / 19/ [0.0 , -3.0, 0.] / wingbox
% T2 / 20/ [0.0 , -2.5, 0.] / wingbox
% T3 / 21/ [0.0 , -1.5, 0.] / wingbox
% T4 / 22/ [0.0 , -0.5, 0.] / wingbox
% T5 / 23/ [0.0 ,  0.0, 0.] / wingbox
% T6 / 24/ [0.0 ,  0.5, 0.] / wingbox
% T7 / 25/ [0.0 ,  1.5, 0.] / wingbox
% T8 / 26/ [0.0 ,  2.5, 0.] / wingbox
% T9 / 27/ [0.0 ,  3.0, 0.] / wingbox

% accel <-> GRID correlation
if isequal(type,'full')
    GRIDs_TRI = [26020, 26015, 21015, 16015, 5001, 5015, 10015, 15015, 15020]; % 29-37
    GRIDs_UNI_TE = [26220, 26215, 21215, 16215, 5210, 5215, 10215, 15215, 15220]; % 1-9
    GRIDs_UNI_tail = [25004, 24004, 20004, 19004, 3000, 8004, 9004, 13004, 14004]; % 11-19
    accel2GRID = [1:9,11:19,29:37; [GRIDs_UNI_TE,GRIDs_UNI_tail,GRIDs_TRI]];
else
    GRIDs_TRI = [26020, 26015, 21015, 16015, 5001, 5015, 10015, 15015, 15020];
    GRIDs_UNI1_9 = [26220, 26215, 21215, 16215, 5210, 5215, 10215, 15215, 15220];
    GRIDs_UNI11_18 = [21002, 21220, 16002, 16220, 5002, 5220, 10002, 10220];
    accel2GRID = [1:9,11:27; [GRIDs_UNI1_9,GRIDs_UNI11_18,GRIDs_TRI]];
    
end
% reorder FEM evec: follows accel2GRID(1,:), i.e. accel 1->27
evec_FEM_1 = zeros(26,6,size(evec_FEM,3));
for i = 1:26 % loop over GVT node
    GRID_tmp = accel2GRID(2,i);  % GRID ID
    evec_FEM_1(i,:,:) = evec_FEM(FEMevec_GRIDorder==GRID_tmp,:,:);
end

% reorder evec: follows accel2GRID(1,:) i.e. accel 1->27
evec_GVT_1 = zeros(18,3,size(evec_GVT,3));
for i = 1:26 % loop over GVT node
    nodeID_tmp = accel2GRID(1,i); % GRID ID
    evec_GVT_1(i,:,:) = evec_GVT(nodeIDs_evec==nodeID_tmp,:,:);
end

% reorder to Phi: 
% [U1, U2,..., U18, T1x, T1y, T1z, T2x, T2y, T2z,...]
Phi_FEM = zeros(44,size(evec_FEM,3));
Phi_FEM(1:17,:) = evec_FEM_1(1:17,3,:);  % uni-axial
Phi_FEM(18:3:end,:) = evec_FEM_1(18:end,1,:); % tri-axial, x
Phi_FEM(19:3:end,:) = evec_FEM_1(18:end,2,:); % tri-axial, y
Phi_FEM(20:3:end,:) = evec_FEM_1(18:end,3,:); % tri-axial, z               %three have triaxial accelerometers. For uni only take z-component

% in a for loop select every four column 
Phi_GVT = zeros(44,size(evec_GVT,3));
Phi_GVT(1:17,:) = evec_GVT_1(1:17,3,:);  % uni-axial
Phi_GVT(18:3:end,:) = evec_GVT_1(18:end,1,:); % tri-axial, x
Phi_GVT(19:3:end,:) = evec_GVT_1(18:end,2,:); % tri-axial, y
Phi_GVT(20:3:end,:) = evec_GVT_1(18:end,3,:); % tri-axial, z

% match mode number
Nmode = min(size(Phi_FEM,2), size(Phi_GVT,2));
Phi_FEM = Phi_FEM(:,1:Nmode);
Phi_GVT = Phi_GVT(:,1:Nmode);

% --------------------
%    MAC
% -------------------
MAC = zeros(Nmode,Nmode);

for i = 1:Nmode
    for j = 1:Nmode
        tmp1 = Phi_GVT(:,i).' * Phi_FEM(:,j);
        tmp2 = Phi_GVT(:,i).' * Phi_GVT(:,i);
        tmp3 = Phi_FEM(:,j).' * Phi_FEM(:,j);
        MAC(i,j) = sqrt(tmp1^2 / (tmp2*tmp3));
    end
end

%MAC w/ vs w/o
figure;hold on;rotate3d on;view(3);                                         
bar3(MAC);                                                                  %Torrence Comment (is this the bar 3 command for a bar graph?)Originally 'bar3c(MAC)'
% axis limit
xlim([0 Nmode+1]);ylim([0 Nmode+1]);zlim([0 1]);
% title
title(['Modal Assurance Criterion'])
% axis label
xlabel('Mode set FEM')
ylabel('Mode set GVT')
zlabel('MAC')
% saveas(gcf,'MAC.png')

    
% plot
% xyz = [0.13, -3.0, 0.; 0.13, -2.5, 0.; 0.13, -1.5, 0.; ...
%        0.13, -0.5, 0.; 0.13,  0.0, 0.; 0.13,  0.5, 0.; ...
%        0.13,  1.5, 0.; 0.13,  2.5, 0.; 0.13,  3.0, 0.; ...
%        0.0,  -2.0, 0.; 0.13, -2.0, 0.; 0.0,  -1.0, 0.; ...
%        0.13, -1.0, 0.; 0.0,   1.0, 0.; 0.13,  1.0, 0.; ...
%        0.0,   2.0, 0.; 0.13,  2.0, 0.; 0.0 , -3.0, 0.; ...
%        0.0 , -2.5, 0.; 0.0 , -1.5, 0.; 0.0 , -0.5, 0.; ...
%        0.0 ,  0.0, 0.; 0.0 ,  0.5, 0.; 0.0 ,  1.5, 0.; ...
%        0.0 ,  2.5, 0.; 0.0 ,  3.0, 0.];
% 
% for i = 1:6
%     figure
%     loc_FEM = xyz + evec_FEM_1(:,1:3,i);
%     loc_GVT = xyz + evec_GVT_1(:,1:3,i);
%     scatter3(loc_FEM(:,1),loc_FEM(:,2),loc_FEM(:,3),10,'o');
%     hold on
%     scatter3(loc_GVT(:,1),loc_GVT(:,2),loc_GVT(:,3),10,'*');
% end
%     



%If I'm understanding this correctly the phi matrix is made with this order

%                           (Frequencies) 
%   (eig_comps) ------------------------
%   UniAxial      |
%   X-axis        |     
%   Y-axis        |  
%   Z-axis 
%
%
%
%

%
