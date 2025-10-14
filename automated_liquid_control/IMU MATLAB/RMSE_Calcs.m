%% Calculate the RMSE for Estimations vs ground truth
addpath('C:/Users/anthe/Documents/MATLAB/matlab2tikz-master/src/');
% % Get attitude estimation Magdwick
Magdwick_vals = readmatrix('C:\Users\anthe\OneDrive - University of Pretoria\UP\Final Year\EPR 400\IMU Testing for Proposal\MATLAB\Magdwick_attitude.xlsx'); 

% Get attitude estimation Basic CF
CF_vals = readmatrix('C:\Users\anthe\OneDrive - University of Pretoria\UP\Final Year\EPR 400\IMU Testing for Proposal\MATLAB\Basic_CF_attitude.xlsx'); 

% Sampling frequency
fs = 600; % Hz (100) <- 400 for CF and 6664 for GD
ts = 1/fs;
t_len = 5; 
numSamples = t_len/ts;
n = 10;
t = (0:(n*numSamples-1)).'/fs; % <- needs to be increased based on no rotations
N = n*numSamples;

% Ground truth
M = [0 0 0;
    45 0 0;
    -45 0 0;
    0 0 0;
    0 50 0;
    0 -50 0; 
    0 0 0;
    30 0 0;
    -30 0 0;
    0 0 0];

% Find ground truth values
% arrayTemp = zeros(n*numSamples, 3);
ground_truth = zeros(numSamples, 3);
vRes = [0 0 0];
for i = 2:n
    [vRes, temp_arr] = CalcGroundTruth(M(i, :), numSamples, vRes);
    ground_truth = cat(1, ground_truth, temp_arr);
end

% RMSE_Mad = zeros(N, 3);
% % Calculate RMSE
% RMSE = zeros(n*numSamples, 3);
% for i = 1:N
%     RMSE_Mad(i, :) = [(sqrt((ground_truth(i, 1) - Magdwick_vals(i, 1))^2)) (sqrt((ground_truth(i, 2) - Magdwick_vals(i, 2))^2)) (sqrt((ground_truth(i, 3) - Magdwick_vals(i, 3))^2))];
% end

% Calculate RMSE
RMSE_CF = zeros(N, 3);
for i = 1:N
    RMSE_CF(i, :) = [sqrt((ground_truth(i, 1)-CF_vals(i, 1))^2) sqrt((ground_truth(i, 2)-CF_vals(i, 2))^2) sqrt((ground_truth(i, 3)-CF_vals(i, 3))^2)];
end

% % Plot results RMSE
% figure(8)
% plot(t, RMSE)
% xlabel('Time (s)')
% ylabel('RMSE (Degrees)')
% % title('RMSE of Ground Truth and Magdwick Attitude')
% title('RMSE of Ground Truth and Basic CF Attitude')
% legend('Roll - x','Pitch - y','Yaw - z')
% grid on

% figure(8)
% plot(t, RMSE_Mad(:, 1), 'Color', [0.8500 0.3250 0.0980], 'LineWidth', 1.5)
% hold on;
% plot(t, RMSE_Mad(:, 2), 'Color', [0.4940 0.1840 0.5560], 'LineWidth', 1.5)
% hold on;
% plot(t, RMSE_Mad(:, 3), 'Color', [0.3010 0.7450 0.9330], 'LineWidth', 1.5)
% xlabel('Time (s)','FontName','Times New Roman','FontSize', 16)
% ylim([0 5]);
% ylabel('RMSE (Degrees)','FontName','Times New Roman','FontSize', 16)
% legend('r','p', 'y')
% set(gca, 'FontName', 'Times New Roman','LineWidth', 1)
% set(gca, 'XColor', 'k', 'YColor', 'k', 'LineWidth', 1)
% set(gca, 'FontSize', 16);  % Make tick label numbers larger
% % Enable minor ticks for both x and y axes
% set(gca, 'XMinorTick', 'on', 'YMinorTick', 'on');   
% box on
% grid on
% hold off;
% cleanfigure;
% filepath = 'C:/Users/anthe/OneDrive - University of Pretoria/UP/Final Year/EPR 400/Report/EPR 400 Template v2/Figures/Design/RMSE_Mad.tex';
% matlab2tikz(filepath, 'width', '\fwidth', 'simplify', true, 'minimumPointsDistance', 0.01);

figure(9)
plot(t, RMSE_CF(:, 1), 'Color', [0.8500 0.3250 0.0980] , 'LineWidth', 1.8)
hold on;
plot(t, RMSE_CF(:, 2), 'Color', [0.4940 0.1840 0.5560], 'LineWidth', 1.8)
hold on;
plot(t, RMSE_CF(:, 3), 'Color', [0.3010 0.7450 0.9330], 'LineWidth', 1.8)
xlabel('Time (s)','FontName','Times New Roman','FontSize', 18)
ylim([0 5]);
ylabel('RMSE (Degrees)','FontName','Times New Roman','FontSize', 18)
legend('r','p', 'y')
set(gca, 'FontName', 'Times New Roman','LineWidth', 1)
set(gca, 'XColor', 'k', 'YColor', 'k', 'LineWidth', 1)
set(gca, 'FontSize', 18);  % Make tick label numbers larger
% Enable minor ticks for both x and y axes
% set(gca, 'XMinorTick', 'on', 'YMinorTick', 'on');   
box on
grid on
hold off;
cleanfigure;
% filepath = 'C:/Users/anthe/OneDrive - University of Pretoria/UP/Final Year/EPR 400/Report/EPR 400 Template v2/Figures/Design/RMSE_CF.tex';
% matlab2tikz(filepath, 'width', '\fwidth', 'simplify', true, 'minimumPointsDistance', 0.1);


% overall_RMSE_mad = [(sum(RMSE_Mad(N, 1)))/N (sum(RMSE_Mad(N, 2)))/N (sum(RMSE_Mad(N, 3)))/N];
overall_RMSE_CF = [(sum(RMSE_CF(N, 1)))/N (sum(RMSE_CF(N, 2)))/N (sum(RMSE_CF(N, 3)))/N];


% disp("Average RMSE of CF is")
disp(overall_RMSE_CF)

% RMSE = rmse(Magdwick_vals, ground_truth);
%% Functions
function [vRes, array] = CalcGroundTruth(motion, numSamples, vRes)
    array = zeros(numSamples, 3);
    for i = 1:numSamples
        array(i,1) = vRes(1) + (motion(1)/numSamples)*i;
        array(i,2) = vRes(2) + (motion(2)/numSamples)*i;
        array(i,3) = vRes(3) + (motion(3)/numSamples)*i;
    end
    vRes = array(i, :);
end
