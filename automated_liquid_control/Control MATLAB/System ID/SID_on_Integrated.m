
addpath('C:/Users/anthe/Documents/MATLAB/matlab2tikz-master/src/');
SID_data = readmatrix('C:\Users\anthe\OneDrive - University of Pretoria\UP\Final Year\EPR 400\STM Things\SID\IMU1 and IMU 2 with Kp of 3 in PID.xlsx');
Ts = 0.01;

cup_roll = smoothdata(SID_data(:, 1));
cup_pitch = smoothdata(SID_data(:, 2));

car_roll = smoothdata(SID_data(:, 3));
car_pitch = smoothdata(SID_data(:, 4));

data_roll = iddata(cup_roll, car_roll, Ts);
% data_roll = iddata(cup_roll(1:700,:), car_roll(1:700,:), Ts);
% data_roll_check = iddata(cup_roll(701:1002,:), car_roll(701:1002,:), Ts);
% data_pitch = iddata(cup_pitch, car_pitch, Ts);

% For roll
% np = 4;
% nz = 3;
np = 5;
nz = 3;
sys1 = tfest(data_roll, np, nz);

figure(2)
compare(sys1, data_roll, 'g');
xlabel('');
ylabel('');
xlabel('Sample (s)','FontName','Times New Roman','FontSize', 18)
ylabel('Amplitude (Degrees)','FontName','Times New Roman','FontSize', 18)
set(gca, 'FontName', 'Times New Roman','LineWidth', 1.8)
set(gca, 'XColor', 'k', 'YColor', 'k', 'LineWidth', 1.8)
set(gca, 'FontSize', 18);  % Make tick label numbers larger
legend('Validation','SID')
title('');
box on
grid on
hold off;
cleanfigure;
% filepath = 'C:/Users/anthe/OneDrive - University of Pretoria/UP/Final Year/EPR 400/Report/EPR 400 Template v2/Figures/Design/SID.tex';
% matlab2tikz(filepath, 'width', '\fwidth', 'simplify', true, 'minimumPointsDistance', 0.01);



% % For pitch
% np = 4;
% nz = 3;
% sys2 = tfest(data_pitch, np, nz);
% 
% figure(2)
% compare(sys2, data_pitch);
% 
% % Take SID models and tune the PIDs
s = tf('s');
G_roll = (24.22*s^3 + 9.929*s^2 + 30.96*s - 12.96)/(s^5 + 5.185*s^4 + 55.17*s^3 + 62.21*s^2 + 146*s + 5.607);
% G_pitch = (-13.51*s^3 + 128.9*s^2 - 12.29*s + 2.041)/(s^4 + 19.23*s^3 + 173.3*s^2 + 454.9*s + 32.62);
% 
figure(3)
step(G_roll);
% 
figure(4)
pzplot(G_roll);
% 
% figure(5)
% step(G_pitch);
% 
% figure(6)
% pzplot(G_pitch);
% 
[pid_roll, info_roll] = pidtune(G_roll, 'PID');
% [pid_pitch, info_pitch] = pidtune(G_pitch, 'PID');
% 
% % Roll controller
Kp_roll = pid_roll.Kp; % 0
Ki_roll = pid_roll.Ki; % -0.492266245983061
Kd_roll = pid_roll.Kd; % 0
% 
% Kp_roll = 1;
% Ki_roll = -0.5;
% Kd_roll = 0.0001;
% 
% % Pitch controller
% % Kp_pitch = pid_pitch.Kp; % 0
% % Ki_pitch = pid_pitch.Ki; % 0.323859564846206
% % Kd_pitch = pid_pitch.Kd; % 0
% 
% Kp_pitch = 0;
% Ki_pitch = 0.324;
% Kd_pitch = 0;
% 
info_roll;
% info_pitch;
% 
% K = 1;
controller_roll = pid(Kp_roll, Ki_roll, Kd_roll, Ts);
% % controller_roll = C;
open_loop_roll = G_roll*controller_roll;
closed_loop_roll = feedback(open_loop_roll, K);
% 
% controller_pitch = pid(Kp_pitch, Ki_pitch, Kd_pitch, Ts);
% open_loop_pitch = G_pitch*controller_pitch;
% closed_loop_pitch = feedback(open_loop_pitch, K);
% 
figure(7)
step(closed_loop_roll)
% 
figure(8)
pzplot(closed_loop_roll);
% 
% figure(9)
% step(closed_loop_pitch)
% 
% figure(10)
% pzplot(closed_loop_pitch);



