%% MATLAB IMU simulator using my accel and gyro values from My_IMU
% addpath('C:/Users/anthe/Documents/MATLAB/matlab2tikz-master/src/');
accelVals = readmatrix('C:\Users\anthe\OneDrive - University of Pretoria\UP\Final Year\EPR 400\IMU Testing for Proposal\MATLAB\acceleration.xlsx')*(-9.807); % <- m/s^2
gyroVals = readmatrix('C:\Users\anthe\OneDrive - University of Pretoria\UP\Final Year\EPR 400\IMU Testing for Proposal\MATLAB\gyroscope.xlsx')*(pi/180); %  <- rad/s;

fs = 600; % 40 Hz test <- 6664 for Madgwick and 400 for CF
ts = 1/fs;
t_len = 5; 
numSamples = t_len/ts;
t = (0:(10*numSamples-1)).'/fs;
IMU = imuSensor('accel-gyro','SampleRate', fs,'ReferenceFrame', 'NED');

% For lsm6dsox accelerometer on IMU:
specsheet1 = accelparams( ...
    'MeasurementRange', 156.9064, ...
    'Resolution', 0.00059875, ...
    'ConstantBias', [0.196133 0.196133 0.196133], ...
    'AxesMisalignment', 0, ... % Assume ideal sense
    'NoiseDensity', [0.0010787 0.0010787 0.0010787], ...
    'BiasInstability', [0.0003717 0.0003967 0.0002893], ...
    'TemperatureBias', [0.000981 0.000981 0.000981], ...
    'RandomWalk', [0.000866 0.000841 0.00080332], ...
    'TemperatureScaleFactor', 0.01);

IMU.Accelerometer = specsheet1;

% For lsm6dsox gyroscope on IMU:
specsheet2 = gyroparams( ...
    'MeasurementRange', 34.907, ...
    'Resolution', 0.00122173, ...
    'ConstantBias', [0.01745 0.01745 0.01745], ...
    'AxesMisalignment', 0, ... % Assume ideal sense
    'NoiseDensity', [0.0000663 0.0000663 0.0000663], ...
    'BiasInstability', [0.0000109 0.000016241 0.000008047], ...
    'TemperatureBias', [0.0001745 0.0001745 0.0001745], ...
    'TemperatureScaleFactor', 0.007, ...
    'RandomWalk', [0.00293 0.00318 0.00288]); % <- according to online
    % 'RandomWalk', [0.0005 0.0005 0.0005]); 

IMU.Gyroscope = specsheet2;
[accelReadings,gyroReadings] = IMU(accelVals,gyroVals);

accelReadings = accelReadings/(2*9.807); % <- in G = /(9.807) NED orientation!!!
gyroReadings = gyroReadings*(180/pi); % <-  in degrees/s

% Write Matlab IMU values to excel
% writematrix(accelReadings,'C:\Users\anthe\OneDrive - University of Pretoria\UP\Final Year\EPR 400\IMU Testing for Proposal\MATLAB\MATLAB_IMU_accelerometer.xlsx', WriteMode='overwritesheet')
% writematrix(gyroReadings,'C:\Users\anthe\OneDrive - University of Pretoria\UP\Final Year\EPR 400\IMU Testing for Proposal\MATLAB\MATLAB_IMU_gyroscope.xlsx', WriteMode='overwritesheet')
writematrix(accelReadings,'C:\Users\anthe\OneDrive - University of Pretoria\UP\Final Year\EPR 400\IMU Testing for Proposal\MATLAB\MATLAB_IMU_accelerometer_vDrift.xlsx', WriteMode='overwritesheet')
writematrix(gyroReadings,'C:\Users\anthe\OneDrive - University of Pretoria\UP\Final Year\EPR 400\IMU Testing for Proposal\MATLAB\MATLAB_IMU_gyroscope_vDrift.xlsx', WriteMode='overwritesheet')

figure(6)
plot(t, accelReadings(:, 1), 'r','LineWidth', 1.5)
hold on;
plot(t, accelReadings(:, 2), 'b','LineWidth', 1.5)
hold on;
plot(t, accelReadings(:, 3),  'Color', [1 0.5 0],'LineWidth', 1.5)
xlabel('Time (s)','FontName','Times New Roman','FontSize', 16)
ylabel('Acceleration (G)','FontName','Times New Roman','FontSize', 16)
legend('x','y','z')
box on
set(gca, 'FontName', 'Times New Roman','LineWidth', 1)
set(gca, 'XColor', 'k', 'YColor', 'k', 'LineWidth', 1)
set(gca, 'FontSize', 16);  % Make tick label numbers larger
% Enable minor ticks for both x and y axes
set(gca, 'XMinorTick', 'on', 'YMinorTick', 'on');
grid on
hold off;
% cleanfigure;
% filepath = 'C:/Users/anthe/OneDrive - University of Pretoria/UP/Final Year/EPR 400/Report/EPR 400 Template v2/Figures/Design/Acc_realistic.tex';
% matlab2tikz(filepath, 'width', '\fwidth', 'simplify', true, 'minimumPointsDistance', 0.01);

% Plot results Gyroscope
figure(7)
plot(t, gyroReadings(:, 2), 'r','LineWidth', 1.5)
hold on;
plot(t, gyroReadings(:, 1), 'b','LineWidth', 1.5)
hold on;
plot(t, gyroReadings(:, 3), 'Color', [1 0.5 0],'LineWidth', 1.5)
xlabel('Time (s)','FontName','Times New Roman','FontSize', 16)
ylabel('Angular Rate (Degrees/s)','FontName','Times New Roman','FontSize', 16)
legend('x','y','z')
set(gca, 'FontName', 'Times New Roman','LineWidth', 1)
set(gca, 'XColor', 'k', 'YColor', 'k', 'LineWidth', 1)
set(gca, 'FontSize', 16);  % Make tick label numbers larger
% Enable minor ticks for both x and y axes
set(gca, 'XMinorTick', 'on', 'YMinorTick', 'on');
box on
grid on
hold off;
% cleanfigure;
% filepath = 'C:/Users/anthe/OneDrive - University of Pretoria/UP/Final Year/EPR 400/Report/EPR 400 Template v2/Figures/Design/Gyro_realistic.tex';
% matlab2tikz(filepath, 'width', '\fwidth', 'simplify', true, 'minimumPointsDistance', 0.01);