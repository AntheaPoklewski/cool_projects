% Open the sample file and plot it 
% Making IMU simulator for acceleration and gyroscope measurements
% Acc = delta(s)/delta(t) 
% Gyro = delta(theta)/delta(t) 

% Properies 

% IMU = imuSensor
% IMU = 
%   imuSensor with properties:
% 
%           IMUType: 'accel-gyro'
%        SampleRate: 100
%       Temperature: 25
%     Accelerometer: [1x1 accelparams]
%         Gyroscope: [1x1 gyroparams]
%      RandomStream: 'Global stream'

% IMU.Gyroscope
% ans = 
%   gyroparams with properties:
% 
%     MeasurementRange: Inf             rad/s      
%           Resolution: 0               (rad/s)/LSB
%         ConstantBias: [0 0 0]         rad/s      
%     AxesMisalignment: [3⨯3 double]    %          
% 
%                    NoiseDensity: [0 0 0]           (rad/s)/√Hz
%                 BiasInstability: [0 0 0]           rad/s      
%                      RandomWalk: [0 0 0]           (rad/s)*√Hz
%                       NoiseType: "double-sided"               
%     BiasInstabilityCoefficients: [1⨯1 struct]                 
% 
%            TemperatureBias: [0 0 0]    (rad/s)/°C    
%     TemperatureScaleFactor: [0 0 0]    %/°C          
%           AccelerationBias: [0 0 0]    (rad/s)/(m/s²)

% IMU.Accelerometer
% ans = 
%   accelparams with properties:
% 
%     MeasurementRange: 19.62                     m/s²      
%           Resolution: 0.00059875                (m/s²)/LSB
%         ConstantBias: [0.4905 0.4905 0.4905]    m/s²      
%     AxesMisalignment: [3⨯3 double]              %         
% 
%                    NoiseDensity: [0.003924 0.003924 0.003924]    (m/s²)/√Hz
%                 BiasInstability: [0 0 0]                         m/s²      
%                      RandomWalk: [0 0 0]                         (m/s²)*√Hz
%                       NoiseType: "double-sided"                            
%     BiasInstabilityCoefficients: [1⨯1 struct]                              
% 
%            TemperatureBias: [0.34335 0.34335 0.5886]    (m/s²)/°C
%     TemperatureScaleFactor: [0.02 0.02 0.02]            %/°C  

% SpecSheet1 = accelparams( ...
%     'MeasurementRange',19.62, ...
%     'Resolution',0.00059875, ...
%     'ConstantBias',0.4905, ...
%     'AxesMisalignment',2, ...
%     'NoiseDensity',0.003924, ...
%     'BiasInstability',0, ...
%     'TemperatureBias', [0.34335 0.34335 0.5886], ...
%     'TemperatureScaleFactor', 0.02);
% 
% IMU.Accelerometer = SpecSheet1;



%% Using Matlab's built-in IMU simulator 
% Testing basic IMU function

% IMU = imuSensor('accel-gyro');
% 
% numSamples = 1000;
% acceleration = zeros(numSamples,3);
% angularVelocity = zeros(numSamples,3);
% 
% [accelReading,gyroReading] = IMU(acceleration, angularVelocity);
% 
% t = (0:(numSamples-1))/IMU.SampleRate;
% subplot(2,1,1)
% plot(t,accelReading)
% legend('X-axis','Y-axis','Z-axis')
% title('Accelerometer Readings')
% ylabel('Acceleration (m/s^2)')
% 
% subplot(2,1,2)
% plot(t,gyroReading)
% legend('X-axis','Y-axis','Z-axis')
% title('Gyroscope Readings')
% ylabel('Angular Velocity (rad/s)')


%% Orientation sequence using MATLAB's IMU

% yaw: 120 degrees over two seconds
% pitch: 60 degrees over one second
% roll: 30 degrees over one-half second
% roll: -30 degrees over one-half second
% pitch: -60 degrees over one second
% yaw: -120 degrees over two seconds
% IMU.SampleRate = 6664; % <- need the release method

load y120p60r30.mat motion fs % <- this is a file I need to load <- contains acceleration, angular velocity and quaternians pertianing to angles
acc = motion.Acceleration;
angVel = motion.AngularVelocity;
orient = motion.Orientation;
IMU = imuSensor('accel-gyro','SampleRate',fs);

% For lsm6dsox accelerometer on IMU:
specsheet1 = accelparams( ...
    'MeasurementRange', 156.9064, ...
    'Resolution', 0.00059875, ...
    'ConstantBias', [0.196133 0.196133 0.196133], ...
    'AxesMisalignment', 0, ... % Assume ideal sense
    'NoiseDensity', [0.0010787 0.0010787 0.0010787], ...
    'BiasInstability', [0.0003717 0.0003967 0.0002893], ...
    'TemperatureBias', [0.000981 0.000981 0.000981], ...
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
    'TemperatureScaleFactor', 0.007);

IMU.Gyroscope = specsheet2;

numSamples = size(motion.Orientation,1); % returns length of 1st dimension of motion.Oriemtation
t = (0:(numSamples-1)).'/fs;
aFilter = imufilter('SampleRate',fs); % default IMU filter object
orientation = zeros(numSamples,1,'quaternion');

for i = 1:numSamples % indexing starts at 1 in MATLAB
    [accelBody,gyroBody] = IMU(acc(i,:), angVel(i,:), orient(i,:));
    orientation(i) = aFilter(accelBody,gyroBody);
end
release(aFilter)

figure(1)
plot(t,eulerd(orientation,'ZYX','frame'))
xlabel('Time (s)')
ylabel('Rotation (degrees)')
title('Orientation Estimation -- Ideal IMU Data, Default IMU Filter')
legend('Z-axis','Y-axis','X-axis')

%% My Simulator

motion = readtable('AngleTest.xlsx');
save AngleTest.mat motion

load AngleTest.mat
angle = AngleTest;

acc = motion.Acceleration;
angVel = motion.AngularVelocity;
orient = motion.Orientation;
IMU = imuSensor('accel-gyro','SampleRate',fs);

% For lsm6dsox accelerometer on IMU:
specsheet1 = accelparams( ...
    'MeasurementRange', 156.9064, ...
    'Resolution', 0.00059875, ...
    'ConstantBias', [0.196133 0.196133 0.196133], ...
    'AxesMisalignment', 0, ... % Assume ideal sense
    'NoiseDensity', [0.0010787 0.0010787 0.0010787], ...
    'BiasInstability', [0.0003717 0.0003967 0.0002893], ...
    'TemperatureBias', [0.000981 0.000981 0.000981], ...
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
    'TemperatureScaleFactor', 0.007);

IMU.Gyroscope = specsheet2;

numSamples = size(motion.Orientation,1); % returns length of 1st dimension of motion.Oriemtation
t = (0:(numSamples-1)).'/fs;
aFilter = imufilter('SampleRate',fs); % default IMU filter object
orientation = zeros(numSamples,1,'quaternion');

for i = 1:numSamples % indexing starts at 1 in MATLAB
    [accelBody,gyroBody] = IMU(acc(i,:), angVel(i,:), orient(i,:));
    orientation(i) = aFilter(accelBody,gyroBody);
end
release(aFilter)

figure(1)
plot(t,eulerd(orientation,'ZYX','frame'))
xlabel('Time (s)')
ylabel('Rotation (degrees)')
title('Orientation Estimation -- Ideal IMU Data, Default IMU Filter')
legend('Z-axis','Y-axis','X-axis')



