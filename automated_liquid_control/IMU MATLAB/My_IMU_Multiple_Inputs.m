%% Define Variables:
% addpath('C:/Users/anthe/Documents/MATLAB/matlab2tikz-master/src/');
% Input Parameters <- true IMU
fs = 600; % Hz (100) <- 6664 for Madgwick <- 400 CF  
ts = 1/fs;
t_len = 5; 
numSamples = t_len/ts;
t = (0:(10*numSamples-1)).'/fs; % <- needs to be increased based on no rotations

% Initialise motion inputs
rollPlot = zeros(1, numSamples);
pitchPlot = zeros(1, numSamples);
yawPlot = zeros(1, numSamples);

% Plot
M0 = [0 0 0];
M1 = [45*((pi/180)/2) 0 0];
M2 = [-45*((pi/180)/2) 0 0];
M3 = [0 0 0];
M4 = [0 50*((pi/180)/2) 0];
M5 = [0 -50*((pi/180)/2) 0]; 
M6 = [0 0 0];
M7 = [30*((pi/180)/2) 0 0];
M8 = [-30*((pi/180)/2) 0 0];
M9 = [0 0 0];

% Orientation plot
orientVals0 = OrientationFunction(M0, numSamples);
orientVals1 = OrientationFunction(M1, numSamples);
orientVals2 = OrientationFunction(M2, numSamples);
orientVals3 = OrientationFunction(M3, numSamples);
orientVals4 = OrientationFunction(M4, numSamples);
orientVals5 = OrientationFunction(M5, numSamples);
orientVals6 = OrientationFunction(M6, numSamples);
orientVals7 = OrientationFunction(M7, numSamples);
orientVals8 = OrientationFunction(M8, numSamples);
orientVals9 = OrientationFunction(M9, numSamples);
orientValsTotal = vertcat(orientVals0, orientVals1, orientVals2, orientVals3, orientVals4, orientVals5, orientVals6, orientVals7, orientVals8, orientVals9);

% Acceleration plot
vRes = [0 0 0];
[vRes, accVals0] = AccelerationFunction(M0, vRes, numSamples);
[vRes, accVals1] = AccelerationFunction(M1, vRes, numSamples);
[vRes, accVals2] = AccelerationFunction(M2, vRes, numSamples);
[vRes, accVals3] = AccelerationFunction(M3, vRes, numSamples);
[vRes, accVals4] = AccelerationFunction(M4, vRes, numSamples);
[vRes, accVals5] = AccelerationFunction(M5, vRes, numSamples);
[vRes, accVals6] = AccelerationFunction(M6, vRes, numSamples);
[vRes, accVals7] = AccelerationFunction(M7, vRes, numSamples);
[vRes, accVals8] = AccelerationFunction(M8, vRes, numSamples);
[vRes, accVals9] = AccelerationFunction(M9, vRes, numSamples);
accValsTotal = vertcat(accVals0, accVals1, accVals2, accVals3, accVals4, accVals5, accVals6, accVals7, accVals8, accVals9);

writematrix(accValsTotal,'C:\Users\anthe\OneDrive - University of Pretoria\UP\Final Year\EPR 400\IMU Testing for Proposal\MATLAB\acceleration.xlsx', WriteMode='overwritesheet')

% Gyroscope plot
gyroVals0 = GyroscopeFunction(M0, numSamples, ts);
gyroVals1 = GyroscopeFunction(M1, numSamples, ts);
gyroVals2 = GyroscopeFunction(M2, numSamples, ts);
gyroVals3 = GyroscopeFunction(M3, numSamples, ts);
gyroVals4 = GyroscopeFunction(M4, numSamples, ts);
gyroVals5 = GyroscopeFunction(M5, numSamples, ts);
gyroVals6 = GyroscopeFunction(M6, numSamples, ts);
gyroVals7 = GyroscopeFunction(M7, numSamples, ts);
gyroVals8 = GyroscopeFunction(M8, numSamples, ts);
gyroVals9 = GyroscopeFunction(M9, numSamples, ts);
gyroValsTotal = vertcat(gyroVals0, gyroVals1, gyroVals2, gyroVals3, gyroVals4, gyroVals5, gyroVals6, gyroVals7, gyroVals8, gyroVals9);

writematrix(gyroValsTotal,'C:\Users\anthe\OneDrive - University of Pretoria\UP\Final Year\EPR 400\IMU Testing for Proposal\MATLAB\gyroscope.xlsx', WriteMode='overwritesheet')

% imuVals = ImuFunction(accValsTotal, gyroValsTotal, orientValsTotal, numSamples, fs);

% Plot results Accelerometer
figure(1)
plot(t, accValsTotal(:, 1), 'r','LineWidth', 1.5)
hold on;
plot(t, accValsTotal(:, 2), 'b','LineWidth', 1.5)
hold on;
plot(t, accValsTotal(:, 3),  'Color', [1 0.5 0],'LineWidth', 1.5)
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
% filepath = 'C:/Users/anthe/OneDrive - University of Pretoria/UP/Final Year/EPR 400/Report/EPR 400 Template v2/Figures/Design/Acc.tex';
% matlab2tikz(filepath, 'width', '\fwidth');

% Plot results Gyroscope
figure(2)
plot(t, gyroValsTotal(:, 2), 'r','LineWidth', 1.5)
hold on;
plot(t, gyroValsTotal(:, 1), 'b','LineWidth', 1.5)
hold on;
plot(t, gyroValsTotal(:, 3), 'Color', [1 0.5 0],'LineWidth', 1.5)
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
% filepath = 'C:/Users/anthe/OneDrive - University of Pretoria/UP/Final Year/EPR 400/Report/EPR 400 Template v2/Figures/Design/Gyro.tex';
% matlab2tikz(filepath, 'width', '\fwidth');

%% System Functions

% Find system orientation
function quat = orientation(r, p, y)
    q0 = cos(p)*cos(r)*cos(y) + sin(p)*sin(r)*sin(y);
    q1 = -cos(p)*sin(r)*sin(y) + sin(p)*cos(r)*cos(y);
    q2 = cos(p)*sin(r)*cos(y) + sin(p)*cos(r)*sin(y);
    q3 = cos(p)*cos(r)*sin(y) - sin(p)*sin(r)*cos(y);
    quat = [q0 q1 q2 q3];
end  

% Find acceleration of quaternion vectors
function resVectorAcc = Accel(r, p, y)
    % Create quaternions from roll, ptch and yaw angles q = ( q0 , ( q1 i +
    % q2 j + q3 k) ) ≡ ( q0 q1 q2 q3 ) From xyz Euler Angle rotations <-
    % yaw, pitch, roll sequency
    
    q0 = cos(p)*cos(r)*cos(y) + sin(p)*sin(r)*sin(y);
    q1 = -cos(p)*sin(r)*sin(y) + sin(p)*cos(r)*cos(y);
    q2 = cos(p)*sin(r)*cos(y) + sin(p)*cos(r)*sin(y);
    q3 = cos(p)*cos(r)*sin(y) - sin(p)*sin(r)*cos(y);
    % q = [q0 q1 q2 q3];
    
    % Create transformation matrix to transform quaternion from reference
    % frame A to B -> r = q*Rq -> r = DCM*R transforming components of
    % fixed vector R in one reference frame into componnets r in another
    
    % DCM = [1-2*(q2^2 + q3^2) 2*(q0*q3 + q1*q2) 2*(q1*q3-q0*q2);
    %      2*(q1*q2-q0*q3) 1-2*(q1^2 + q3^2) 2*(q0*q1 + q2*q3);
    %     2*(q0*q2 + q1*q3) 2*(q2*q3 - q0*q1) 1-2*(q1^2 + q2^2)];

    v = [0 0 -9.807]/-9.807;

    Cn = [(q0^2 + q1^2 - q2^2 - q3^2) 2*(q1*q2 + q0*q3) 2*(q1*q3 - q0*q2);
         2*(q1*q2 - q0*q3) (q0^2 - q1^2 + q2^2 - q3^2) 2*(q2*q3 + q0*q1);
         2*(q1*q3 + q0*q2) 2*(q2*q3 + q0*q1) (q0^2 - q1^2 - q2^2 + q3^2)];

    resVectorAcc = Cn * v';
end

% Fund angular velocity of quaternion axes
function resVectorGyro = Gyro(r, p, y)
    % Create quaternions from roll, ptch and yaw angles
    % q = ( q0 , ( q1 i + q2 j + q3 k) ) ≡ ( q0 q1 q2 q3 )
    % From xyz Euler Angle rotations <- roll, pitch, yaw sequence (yxz)
    
    q0 = cos(p)*cos(r)*cos(y) + sin(p)*sin(r)*sin(y);
    q1 = -cos(p)*sin(r)*sin(y) + sin(p)*cos(r)*cos(y);
    q2 = cos(p)*sin(r)*cos(y) + sin(p)*cos(r)*sin(y);
    q3 = cos(p)*cos(r)*sin(y) - sin(p)*sin(r)*cos(y);
    % q = [q0 q1 q2 q3];
    
    theta = asin(-2*(q1*q2 - q0*q2)); % <- roll (y)
    phi = atan(2*(q0*q1 + q2*q3)/(q0^2 - q1^2 - q2^2 + q3^2)); % <- pitch (x)
    psi = atan(2*(q0*q3 + q1*q2)/(q0^2 + q1^2 - q2^2 - q3^2)); % <- yaw (z)
    
    resVectorGyro = [phi theta psi];
end

% Main

% Store quaternions showing orientation
function OrientVals = OrientationFunction(motion, numSamples)
    roll = zeros(1, numSamples);
    pitch = zeros(1, numSamples);
    yaw = zeros(1, numSamples);

    for i = 1:numSamples
        roll(1, i) = (motion(1)/numSamples)*i;
        pitch(1, i) = (motion(2)/numSamples)*i;
        yaw(1, i) = (motion(3)/numSamples)*i;
    end

    OrientVals = zeros(numSamples, 1, 'quaternion');
    for i = 1:numSamples
        OrientValsTemp = orientation(roll(1,i), pitch(1,i), yaw(1,i));
        OrientVals(i, 1) = quaternion(OrientValsTemp(1), OrientValsTemp(2), OrientValsTemp(3), OrientValsTemp(4));
    end
end

% Find acceleration
function [vRes, AccelPlot] = AccelerationFunction(motion, vRes, numSamples)
    roll = zeros(1, numSamples);
    pitch = zeros(1, numSamples);
    yaw = zeros(1, numSamples);

    for i = 1:numSamples
        roll(1, i) = (motion(1)/numSamples)*i;
        pitch(1, i) = (motion(2)/numSamples)*i;
        yaw(1, i) = (motion(3)/numSamples)*i;
    end
   
    AccelPlot = zeros(numSamples,  3);
    for i = 1:numSamples
        AccelVectors = Accel(roll(1,i), pitch(1,i), yaw(1,i));
        AccelPlot(i, 1) = (vRes(1) + AccelVectors(1)); % <- change in i
        AccelPlot(i, 2) = (vRes(2) - AccelVectors(2)); % <- change in j
        if roll(1, i) < 0 || pitch(1, i) < 0
            AccelPlot(i, 3) = (vRes(3) + (1 - AccelVectors(3))); % <- change in k
        else
            AccelPlot(i, 3) = (AccelVectors(3)); % <- change in k
        end
    end 
    vRes = [AccelPlot(i, 1) AccelPlot(i, 2) AccelPlot(i, 3)];
end

% Find gyroscope
function GyroPlot = GyroscopeFunction(motion, numSamples, ts)
    roll = zeros(1, numSamples);
    pitch = zeros(1, numSamples);
    yaw = zeros(1, numSamples);

    for i = 1:numSamples
        roll(1, i) = (motion(1)/numSamples)*i;
        pitch(1, i) = (motion(2)/numSamples)*i;
        yaw(1, i) = (motion(3)/numSamples)*i;
    end

    GyroAngles = zeros(numSamples, 3);
    for i = 1:numSamples
        GyroAnglesTemp = Gyro(roll(1,i), pitch(1,i), yaw(1,i));
        GyroAngles(i, 1) = (GyroAnglesTemp(1)); % <- 0.157 radians per sec <- pitch about x (phi)  
        GyroAngles(i, 2) = (GyroAnglesTemp(2)); % <- roll about y (theta)
        GyroAngles(i, 3) = (GyroAnglesTemp(3)); % <- yaw about z (psi)
    end

    GyroPlot = zeros(numSamples,  3);
    for i = 1:numSamples-1
        GyroPlot(i, 1) = (GyroAngles(i+1, 1) - GyroAngles(i, 1))*(180/pi)/ts;
        GyroPlot(i, 2) = (GyroAngles(i+1, 2) - GyroAngles(i, 2))*(180/pi)/ts;
        GyroPlot(i, 3) = (GyroAngles(i+1, 3) - GyroAngles(i, 3))*(180/pi)/ts;
    end
end


