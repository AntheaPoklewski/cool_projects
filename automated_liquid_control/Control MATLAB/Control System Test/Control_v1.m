% Initialize output variables.
function [dxdt,M,C,G] = Control_v1(x,u,param)

m1 = param.m1; % Mass 1
m2 = param.m2; % Mass 2
r1 = param.r1; % Link length 1
r2 = param.r2; % Link length 2
J1 = param.J1; % Inertia 1
J2 = param.J2; % Inertia 2
g  = param.g; % Gravity constant

dxdt = zeros(4,1);
M = zeros(2,2);
C = zeros(2,2);
G = zeros(2,1);

% Extract state variables 
q1 = x(1); % Joint angle 1
q2 = x(2); % Joint angle 2
dq1 = x(3); % Joint velocity 1
dq2 = x(4); % Joint velocity 2

% Compute p1, p2, p3, p4, p5, p6.
p1 = (m1 + m2)*r1^2 + m2*r2^2 + J1;
p2 = m2*r1*r2;
p3 = m2*r2^2;
p4 = p3 + J2;
p5 = (m1 + m2)*r1*g;
p6 = m2*r2*g;

% Compute M matrix 2-by-2 matrix of inertia
M = [p1 + 2*p2*cos(q2), p3 + p2*cos(q2);
    p3 + p2*cos(q2), p4];

% Compute C matrix of Coriolis and centrifugal forces
C = [-p2*sin(q2)*dq1, -2*p2*sin(q2)*dq1;
    0, p2*sin(q2)*dq2];

% Compute G vector of gravity
G = [p5*cos(q1) + p6*cos(q1 + q2);
    p6*cos(q1 + q2)];

if nargout == 1
    % Compute the derivative of the state (dxdt) - velocity and
    % acceleration of arm
    dq = [dq1; dq2];
    ddq = M\(u - C*dq - G);
    dxdt = [dq; ddq];
end
end

