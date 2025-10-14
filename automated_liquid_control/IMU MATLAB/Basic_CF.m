% Get gyro and accel values from MATLAB realistic IMU
accelVals = readmatrix('C:\Users\anthe\OneDrive - University of Pretoria\UP\Final Year\EPR 400\IMU Testing for Proposal\MATLAB\MATLAB_IMU_accelerometer_vDrift.xlsx')*(-9.807); % <- m/s^2
gyroVals = readmatrix('C:\Users\anthe\OneDrive - University of Pretoria\UP\Final Year\EPR 400\IMU Testing for Proposal\MATLAB\MATLAB_IMU_gyroscope_vDrift.xlsx'); % <- deg/s;

% accelVals = readmatrix('C:\Users\anthe\OneDrive - University of Pretoria\UP\Final Year\EPR 400\IMU Testing for Proposal\MATLAB\acceleration.xlsx')*(-9.807);
% gyroVals = readmatrix('C:\Users\anthe\OneDrive - University of Pretoria\UP\Final Year\EPR 400\IMU Testing for Proposal\MATLAB\gyroscope.xlsx');
% Step time
fs = 600; % Hz <- IMU has 100 Hz <- 400 for plot 
ts = 1/fs;
delta_t = ts;
t_len = 5; 
n = 10;
totalNumSamples = n*(t_len/ts);   
t = (0:(totalNumSamples-1)).'/fs;

% Convert from deg/s to rad/s for gyroscope as needed for Magdwick
% Accel -> Gs
% Gyro -> rad/s
gyroVals = gyroVals*(pi/180);

%% Main

alpha = 0.96; % <- value between 0 and 1
theta = zeros(totalNumSamples, 3);
theta_prev = [0 0 0]; % Initial orientation
for i = 1:totalNumSamples
    theta(i, :) = (alpha*angVelocityCals(gyroVals(i, :), theta_prev, delta_t) + (1-alpha)*accelCals(accelVals(i, :)));
    theta_prev = theta(i, :);
end

for i = 1:totalNumSamples
    theta(i, :) = [theta(i, 2)*(180/pi)-0.7 theta(i, 1)*(180/pi)-0.7 theta(i, 3)*(180/pi)]*-2; % <- degrees
end

% theta = theta*(180/pi);

% Plot results CF
% figure(10)
% plot(t, theta)
% xlabel('Time (s)')
% ylabel('Degrees')
% title('Attitude Estimation from Basic CF Roll, Pitch, Yaw')
% legend('Roll - x','Pitch - y','Yaw - z')
% grid on

figure(10)
plot(t, -theta(:, 1), 'm', 'LineWidth', 1.5)
hold on;
plot(t, -theta(:, 2), 'Color', [0.9290, 0.6940, 0.1250], 'LineWidth', 1.5)
hold on;
plot(t, -theta(:, 3), 'g', 'LineWidth', 1.5)
xlabel('Time (s)','FontName','Times New Roman','FontSize', 16)
ylabel('Orientation Estimation (Degrees)','FontName','Times New Roman','FontSize', 16)
legend('r','p','y')
set(gca, 'FontName', 'Times New Roman','LineWidth', 1)
set(gca, 'XColor', 'k', 'YColor', 'k', 'LineWidth', 1)
set(gca, 'FontSize', 16);  % Make tick label numbers larger
% Enable minor ticks for both x and y axes
set(gca, 'XMinorTick', 'on', 'YMinorTick', 'on');   
box on
grid on
hold off;
% cleanfigure;
% filepath = 'C:/Users/anthe/OneDrive - University of Pretoria/UP/Final Year/EPR 400/Report/EPR 400 Template v2/Figures/Design/CF_orient_noise.tex';
% matlab2tikz(filepath, 'width', '\fwidth', 'simplify', true, 'minimumPointsDistance', 0.01);

% Write basic CF values to excel for comparison RMSE
writematrix(theta,'C:\Users\anthe\OneDrive - University of Pretoria\UP\Final Year\EPR 400\IMU Testing for Proposal\MATLAB\Basic_CF_attitude.xlsx', WriteMode='overwritesheet')

%% Functions of CF
% Accel fuction
function theta_acc = accelCals(Acc)
    theta_acc = [atan(Acc(2)/Acc(3)) atan(-Acc(1)/sqrt(Acc(2)^2 + Acc(3)^2)) 0];
end 

% Gyro fuction
function theta_ang_velocity = angVelocityCals(Gyro, theta_prev, delta_t)
    theta_ang_velocity = [(theta_prev(1) + Gyro(1)*delta_t) (theta_prev(2) + Gyro(2)*delta_t) (theta_prev(3) + Gyro(3)*delta_t)];
end 

