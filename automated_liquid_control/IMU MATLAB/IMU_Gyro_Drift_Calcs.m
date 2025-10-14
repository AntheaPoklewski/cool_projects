%% Testing IMU Gyro Drift

accelVals_OG = readmatrix('C:\Users\anthe\OneDrive - University of Pretoria\UP\Final Year\EPR 400\IMU Testing for Proposal\MATLAB\acceleration.xlsx'); % <- Gs
gyroVals_OG = readmatrix('C:\Users\anthe\OneDrive - University of Pretoria\UP\Final Year\EPR 400\IMU Testing for Proposal\MATLAB\gyroscope.xlsx'); % <- deg/s

accelVals_drift = readmatrix('C:\Users\anthe\OneDrive - University of Pretoria\UP\Final Year\EPR 400\IMU Testing for Proposal\MATLAB\MATLAB_IMU_accelerometer.xlsx'); % <- Gs
gyroVals_drift = readmatrix('C:\Users\anthe\OneDrive - University of Pretoria\UP\Final Year\EPR 400\IMU Testing for Proposal\MATLAB\MATLAB_IMU_gyroscope.xlsx'); % <- deg/s

% Set up
fs = 6664; % 100 Hz test
ts = 1/fs;
t_len = 5; 
numSamples = 10*t_len/ts;
t = (0:(numSamples-1)).'/fs;

errorAccelAbsAve = zeros(numSamples, 3);
errorGyroAbsAve = zeros(numSamples, 3);

errorAccelAve = zeros(numSamples, 3);
errorGyroAve = zeros(numSamples, 3);

% Calculate error
for i = 1:numSamples
    errorAccelAbsAve(i, :) = [abs(abs(accelVals_drift(i, 1)) - abs(accelVals_OG(i, 1))) abs(abs(accelVals_drift(i, 2)) - abs(accelVals_OG(i, 2))) abs(abs(accelVals_drift(i, 3)) - abs(accelVals_OG(i, 3)))];
    errorGyroAbsAve(i, :) = [abs(abs(gyroVals_drift(i, 1)) - abs(gyroVals_OG(i, 1))) abs(abs(gyroVals_drift(i, 2)) - abs(gyroVals_OG(i, 2))) abs(abs(gyroVals_drift(i, 3)) - abs(gyroVals_OG(i, 3)))];

    errorAccelAve(i, :) = [(abs(accelVals_drift(i, 1)) - abs(accelVals_OG(i, 1))) (abs(accelVals_drift(i, 2)) - abs(accelVals_OG(i, 2))) (abs(accelVals_drift(i, 3)) - abs(accelVals_OG(i, 3)))];
    errorGyroAve(i, :) = [abs((gyroVals_drift(i, 1)) - (gyroVals_OG(i, 1))) abs((gyroVals_drift(i, 2)) - (gyroVals_OG(i, 2))) abs((gyroVals_drift(i, 3)) - (gyroVals_OG(i, 3)))];
end

AbsAccelerationError = sum(errorAccelAbsAve)/numSamples;
AbsGyroscopeError = sum(errorGyroAbsAve)/numSamples;

AveAccelerationError = sum(errorAccelAve)/numSamples;
AveGyroscopeError = sum(errorGyroAve)/numSamples;

disp("Absolute errors")
disp(AbsAccelerationError) % <- Gs 
disp(AbsGyroscopeError) % <- deg/s

disp("Average errors")
disp(AveAccelerationError) % <- Gs 
disp(AveGyroscopeError) % <- deg/s

