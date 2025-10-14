%% Complementary Filter - Magdwick - Acceleration and full system

%% My IMU simulated values
addpath('C:/Users/anthe/Documents/MATLAB/matlab2tikz-master/src/');
% Get gyro and accel values from My_IMU - Ideal Vals
% accelVals = readmatrix('C:\Users\anthe\OneDrive - University of Pretoria\UP\Final Year\EPR 400\IMU Testing for Proposal\MATLAB\acceleration.xlsx'); % <- Gs
% gyroVals = readmatrix('C:\Users\anthe\OneDrive - University of Pretoria\UP\Final Year\EPR 400\IMU Testing for Proposal\MATLAB\gyroscope.xlsx'); % <- deg/s;
% 
% Add in some noise
% accelVals = accelVals + 0.2*(rand(size(accelVals))-0.5);
% gyroVals = gyroVals + 0.2*(rand(size(gyroVals))-0.5);

% % Get gyro and accel values from MATLAB realistic IMU
accelVals = readmatrix('C:\Users\anthe\OneDrive - University of Pretoria\UP\Final Year\EPR 400\IMU Testing for Proposal\MATLAB\MATLAB_IMU_accelerometer.xlsx'); % <- Gs
gyroVals = readmatrix('C:\Users\anthe\OneDrive - University of Pretoria\UP\Final Year\EPR 400\IMU Testing for Proposal\MATLAB\MATLAB_IMU_gyroscope.xlsx'); % <- deg/s;

% Step time
fs = 6664; % Hz <- IMU has 100 Hz <- 100 Hz test
ts = 1/fs;
t_len = 5; 
n = 10;
totalNumSamples = n*(t_len/ts);   
t = (0:(totalNumSamples-1)).'/fs;

% Correct static errors
constantBiasRoll = 1.0640;
constantBiasPitch = 0.8084;
constantBiasYaw = 1.1199;

% Correct gyro drift static
for i = 1:totalNumSamples
    gyroVals(i, :) = [gyroVals(i, 1)-constantBiasRoll gyroVals(i, 2)-constantBiasPitch gyroVals(i, 3)-constantBiasYaw]; % <- deg/s
end

%% Online Magdwick Example IMU values
% 
% load('ExampleData.mat');
% 
% figure()
% figure('Name', 'Sensor Data');
% axis(1) = subplot(2,1,1);
% hold on;
% plot(time, Gyroscope(:,1), 'r');
% plot(time, Gyroscope(:,2), 'g');
% plot(time, Gyroscope(:,3), 'b');
% legend('X', 'Y', 'Z');
% xlabel('Time (s)');
% ylabel('Angular rate (deg/s)');
% title('Gyroscope');
% hold off;
% axis(2) = subplot(2,1,2);
% hold on;
% plot(time, Accelerometer(:,1), 'r');
% plot(time, Accelerometer(:,2), 'g');
% plot(time, Accelerometer(:,3), 'b');
% legend('X', 'Y', 'Z');
% xlabel('Time (s)');
% ylabel('Acceleration (g)');
% title('Accelerometer');
% hold off;
% linkaxes(axis, 'x');

%% Magdwick Calculations
% Convert from deg/s to rad/s for gyroscope as needed for Magdwick
% Accel -> Gs
% Gyro -> rad/s
gyroVals = gyroVals*(pi/180);

% Initial quaternion
Q = zeros(totalNumSamples, 4);
Q(1,:) = [1 0 0 0]; % <- [q0 q1 q2 q3] <- initial value

% Attitude initialisation
theta = asin(-2*(Q(1,2)*Q(1,3) - Q(1,1)*Q(1,3)));
phi = atan(2*(Q(1,1)*Q(1,2) + Q(1,3)*Q(1,4))/(Q(1,1)^2 - Q(1,2)^2 - Q(1,3)^2 + Q(1,4)^2));
psi = atan(2*(Q(1,1)*Q(1,4) + Q(1,2)*Q(1,3))/(Q(1,1)^2 + Q(1,2)^2 - Q(1,3)^2 - Q(1,4)^2));

attitude = zeros(totalNumSamples, 3);
attitude(1,:) = [theta phi psi]*(180/pi); % <- roll pitch yaw for initial quaternion

acceleration = zeros(totalNumSamples, 3);
gyroscope = zeros(totalNumSamples, 3);

gyroMeasurementError = (0.1)*(pi/180); % <- maximum gyro error around 1 degree
B = sqrt(3/4)*gyroMeasurementError;

%% Main loop 
for i = 2:totalNumSamples 
    qMagdwick = Magdwick(accelVals(i,:), gyroVals(i,:), Q(i-1, :), B, ts);
    Q(i, :) = qMagdwick;

    % Plot roll, pitch, yaw
    q0 = qMagdwick(1);
    q1 = qMagdwick(2);
    q2 = qMagdwick(3);
    q3 = qMagdwick(4);

    theta = asin(-2*(q1*q2 - q0*q2)); % <- roll (y)
    phi = atan(2*(q0*q1 + q2*q3)/(q0^2 - q1^2 - q2^2 + q3^2)); % <- pitch (x)
    psi = atan(2*(q0*q3 + q1*q2)/(q0^2 + q1^2 - q2^2 - q3^2)); % <- yaw (z)

    attitude(i, :) = [theta phi psi]*(180/pi);

end

% % Plot results IMU
% figure(5)
% plot(t, attitude)
% xlabel('Time (s)')
% ylabel('Degrees')
% legend('Roll - x','Pitch - y','Yaw - z')
% grid on

% Plot results Gyroscope
figure(5)
plot(t, -attitude(:, 1), 'm', 'LineWidth', 1.5)
hold on;
plot(t, -attitude(:, 2), 'Color', [0.9290, 0.6940, 0.1250], 'LineWidth', 1.5)
hold on;
plot(t, -attitude(:, 3), 'g', 'LineWidth', 1.5)
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
% filepath = 'C:/Users/anthe/OneDrive - University of Pretoria/UP/Final Year/EPR 400/Report/EPR 400 Template v2/Figures/Design/Mad_orient_noise.tex';
% matlab2tikz(filepath, 'width', '\fwidth', 'simplify', true, 'minimumPointsDistance', 0.01);

% Write Magdwick values to excel for comparison RMSE
writematrix(attitude,'C:\Users\anthe\OneDrive - University of Pretoria\UP\Final Year\EPR 400\IMU Testing for Proposal\MATLAB\Magdwick_attitude.xlsx', WriteMode='overwritesheet')


%% Magdwick Filter Function
function quat = Magdwick(acc, gyro, q, B, ts) % <- current quat determined from prev estimation
    q0 = q(1);
    q1 = q(2);
    q2 = q(3);
    q3 = q(4);
    acc =  acc/norm(acc);	% normalise magnitude

    % q0A = qA(1);
    % q1A = qA(2);
    % q2A = qA(3);
    % q3A = qA(4);

    % Gradient decent algorithm corrective step
    F = [2*(q1*q3 - q0*q2)-acc(1);
         2*(q0*q1 + q2*q3)-acc(2);
         2*(0.5 - q1^2 - q2^2)-acc(3)];

    J = [-2*q2 2*q3 -2*q0 2*q1;
          2*q1 2*q0 2*q3 2*q2;
          0 -4*q1 -4*q2 0];

    step = (J'*F);
    step = step / norm(step);	% normalise step magnitude

    % Fusion algorithm <- Expanded in gyro expansion of Magdwick
    qDot = 0.5*quatmultiply([q0 q1 q2 q3],[0 gyro(1) gyro(2) gyro(3)]) - B*step';

    % Integrate to yield quaternion
    q = q + qDot*ts; % <- new estimate
    quat = q / norm(q); % normalise quaternion and return value of new orientation estimate
end

