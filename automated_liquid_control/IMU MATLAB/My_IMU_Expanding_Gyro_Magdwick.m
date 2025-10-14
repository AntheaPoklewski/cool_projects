%% Expanding gyroscope of CF Magdwick
% get gyro and accel values from My_IMU
accelVals = readmatrix('C:\Users\anthe\OneDrive - University of Pretoria\UP\Final Year\EPR 400\IMU Testing for Proposal\MATLAB\acceleration.xlsx'); % <- Gs
gyroVals = readmatrix('C:\Users\anthe\OneDrive - University of Pretoria\UP\Final Year\EPR 400\IMU Testing for Proposal\MATLAB\gyroscope.xlsx')*(pi/180); % <- rad/s

% Step time
fs = 6664; % Hz
ts = 1/fs;
dt = 0.5;
t_len = 5; 
numSamples = t_len/ts;

% Initial quaternion
Q = zeros(numSamples, 4);
Q(1,:) = [1 0 0 0]; % <- [q0 q1 q2 q3]

% Initial coordinates of the point
P(1,:) = [1,2,3];
PX(1,:) = [2,2,3];
PY(1,:) = [1,3,3];
PZ(1,:) = [1,2,4];

% Main loop
for i = 2:100 % <- first 2 sample groups
    % w = [0 accelVals(i + numSamples, 1) accelVals(i + numSamples, 2) accelVals(i + numSamples, 3)];
    w = [0 9*(pi/180) 0 0]; % <- M = [45*((pi/180)/2) 0 0]

    % Update orientation
    % Compute the quaternion derivative
    % Qdot = quatmultiply(0.5*Q(i-1,:),w);
    Qdot = 0.5*[Q(i-1, 1)*w(1) - Q(i-1, 2)*w(2) - Q(i-1, 3)*w(3) - Q(i-1, 4)*w(4);
                Q(i-1, 1)*w(2) + Q(i-1, 2)*w(1) + Q(i-1, 3)*w(4) - Q(i-1, 4)*w(3);
                Q(i-1, 1)*w(3) - Q(i-1, 2)*w(4) + Q(i-1, 3)*w(1) + Q(i-1, 4)*w(2);
                Q(i-1, 1)*w(4) + Q(i-1, 2)*w(3) - Q(i-1, 3)*w(2) + Q(i-1, 4)*w(1)]';

    % Update the estimated position
    Q(i,:) = Q(i-1,:) + Qdot*dt;

    % Normalize quaternion
    % Q(i,:) = Q(i,:)/norm(Q(i,:));
    Q(i,:) = Q(i,:)/sqrt(Q(i, 1)^2 + Q(i, 2)^2 + Q(i, 3)^2 + Q(i, 4)^2);
  
    % Update point coordinates
    % Compute the associated transformation marix
    % M = quat2rotm(Q(i,:));     
    q0 = Q(i, 1);
    q1 = Q(i, 2);
    q2 = Q(i, 3);
    q3 = Q(i, 4);

    % First row of the rotation matrix
    r00 = 2 * (q0 * q0 + q1 * q1) - 1;
    r01 = 2 * (q1 * q2 - q0 * q3);
    r02 = 2 * (q1 * q3 + q0 * q2);
     
    % Second row of the rotation matrix
    r10 = 2 * (q1 * q2 + q0 * q3);
    r11 = 2 * (q0 * q0 + q2 * q2) - 1;
    r12 = 2 * (q2 * q3 - q0 * q1);
     
    % Third row of the rotation matrix
    r20 = 2 * (q1 * q3 - q0 * q2);
    r21 = 2 * (q2 * q3 + q0 * q1);
    r22 = 2 * (q0 * q0 + q3 * q3) - 1;
     
    % 3x3 rotation matrix
    M = [r00 r01 r02;
         r10 r11 r12;
         r20 r21 r22];

    % Calculate the coordinate of the new point
    P(i,:) = (M * P(1,:)')';
    PX(i,:) = (M * PX(1,:)')';
    PY(i,:) = (M * PY(1,:)')';
    PZ(i,:) = (M * PZ(1,:)')';

    % Display the new point
    plot3 (P(i,1),P(i,2),P(i,3),'k.');
    plot3 (PX(i,1),PX(i,2),PX(i,3),'r.');
    plot3 (PY(i,1),PY(i,2),PY(i,3),'g.');
    plot3 (PZ(i,1),PZ(i,2),PZ(i,3),'b.');
    line ( [ P(i,1) , PX(i,1) ] , [ P(i,2) , PX(i,2) ],  [ P(i,3) , PX(i,3) ] ,'Color','r');
    line ( [ P(i,1) , PY(i,1) ] , [ P(i,2) , PY(i,2) ],  [ P(i,3) , PY(i,3) ] ,'Color','g');
    line ( [ P(i,1) , PZ(i,1) ] , [ P(i,2) , PZ(i,2) ],  [ P(i,3) , PZ(i,3) ] ,'Color','b');
    hold on;
    axis square equal;
    grid on;
    drawnow;

end

% Display point trajectory
plot3 (P(:,1),P(:,2),P(:,3),'r.');
axis square equal;
grid on;
xlabel ('x');
ylabel ('y');
zlabel ('z');













