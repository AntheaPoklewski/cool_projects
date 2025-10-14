r = 9;
L1 = 15; 
L2 = 7;
h = 13.27;

PI = 3.141592654;
rad_to_deg = 180/PI;
deg_to_rad = PI/180;

theta_pitch = 6.2*deg_to_rad; % max = 62 -> if -ve-> same angle opp direction
phi_roll = 10.7*deg_to_rad; % max = 65

body_pitch = zeros(1, 3);
body_roll1 = zeros(1, 3);
body_roll2 = zeros(1, 3);

A_p = zeros(1, 3);
A_r = zeros(1, 3);
B_p = zeros(1, 3);
B_r = zeros(1, 3);
C_p = zeros(1, 3);
C_r = zeros(1, 3);

% global_val = [0, 0, 17]; % origin plate
% global_val = [9, 0, 17]; % legA
% global_val = [-4.5, -9*sqrt(3)/2, 17]; % legB
% global_val = [-4.5, 9*sqrt(3)/2, 17]; % legC

% global_val = [9, 0, 14.4]; % legA
% body_pitch(1) = global_val(1)*cos(theta_pitch) - global_val(3)*sin(theta_pitch);
% body_pitch(2) = 0;
% body_pitch(3) = global_val(1)*sin(theta_pitch) + global_val(3)*cos(theta_pitch);
% 
% global_val = [-4.5, -9*sqrt(3)/2, 14.4]; % legB
% body_roll1(1) = global_val(1);
% body_roll1(2) = global_val(2)*cos(phi_roll) + global_val(3)*sin(phi_roll);
% body_roll1(3) = global_val(2)*sin(phi_roll) + global_val(3)*cos(phi_roll);
% 
% global_val = [-4.5, 9*sqrt(3)/2, 14.4]; % legC
% body_roll2(1) = global_val(1);
% body_roll2(2) = global_val(2)*cos(phi_roll) + global_val(3)*sin(phi_roll);
% body_roll2(3) = global_val(2)*sin(phi_roll) + global_val(3)*cos(phi_roll);

% theta = atan(ny/nx); % rad
% phi = sqrt(nx*nx + ny*ny); % rad
% 
% nz_SP = cos(phi);
% r_norm = sin(phi);
% nx_SP = r_norm*cos(theta);
% ny_SP = r_norm*sin(theta);

% nx = body1(2)*body2(3)-body2(2)*body1(3);
% ny = -(body1(1)*body2(3)-body2(1)*body1(3));
% nz = body1(1)*body2(2)-body2(1)*body1(2);

% % Calc norm
% nx_SP = r*cos(x_angle);
% ny_SP = r*cos(y_angle);
% nz_SP = cos(sqrt(nx_SP*nx_SP)+(ny_SP*ny_SP));

global_val = [0, 0, h]; % origin plate
motor = 2;

if (motor == 1)
    nx = global_val(1)*cos(theta_pitch) - global_val(3)*sin(theta_pitch);
    ny = 0;
    nz = global_val(1)*sin(theta_pitch) + global_val(3)*cos(theta_pitch);
end

if (motor == 2)
    nx = global_val(1);
    ny = global_val(2)*cos(phi_roll) + global_val(3)*sin(phi_roll);
    nz = -global_val(2)*sin(phi_roll) + global_val(3)*cos(phi_roll);
end

if (motor == 3)
    nx = global_val(1);
    ny = global_val(2)*cos(phi_roll) + global_val(3)*sin(phi_roll);
    nz = -global_val(2)*sin(phi_roll) + global_val(3)*cos(phi_roll);
end

% Debugging full angle for last 2 legs
% if (motor == 2)
%     nx = global_val(1);
%     ny = global_val(2)*cos(phi_roll) + global_val(3)*sin(phi_roll);
%     nz = -global_val(2)*sin(phi_roll) + global_val(3)*cos(phi_roll);
% end
% 
% if (motor == 3)
%     nx = global_val(1);
%     ny = global_val(2)*cos(phi_roll) + global_val(3)*sin(phi_roll);
%     nz = -global_val(2)*sin(phi_roll) + global_val(3)*cos(phi_roll);
% end

if (motor == 1)
    % case 1 % Motor 1 on leg 1 -> pitch
    % Find leg orientation in space ito x, y, z
    A_p(1) = r*nz/sqrt(nx*nx + nz*nz);
    A_p(3) = h - (nx*r)/sqrt(nz*nz+nx*nx);
    A_p(2) = 0;

    % Find orientation of revolute joint between 2 legs in space
    A_mid = (r-A_p(1))/A_p(3);
    B_mid = (A_p(1)*A_p(1) + A_p(3)*A_p(3) + L2*L2 - L1*L1 - r*r)/(2*A_p(3));
    C_mid = A_mid*A_mid + 1;
    D_mid = 2*(A_mid*B_mid - r);
    E_mid = B_mid*B_mid + r*r - L2*L2;

    A_r(1) = (-D_mid + sqrt(D_mid*D_mid - 4*C_mid*E_mid))/(2*C_mid);
    A_r(2) = 0;
    A_r(3) = sqrt(L2*L2 - A_r(1)*A_r(1) + 2*A_r(1)*r - r*r);

    % A_r(3) musn't go less than 0

    angle = atan(A_r(3)/(A_r(1)-r))*rad_to_deg;
	if (isnan(angle))
		angle = 90;
    end
end

if (motor == 2)
    % case 2
    B_p(1) = -(r*nz)/(sqrt(nx*nx + 3*ny*ny + 4*nz*nz + 2*sqrt(3)*nx*ny));
    B_p(2) = -(sqrt(3)*r*nz)/(sqrt(nx*nx + 3*ny*ny + 4*nz*nz + 2*sqrt(3)*nx*ny));
    B_p(3) = h + (r*(sqrt(3)*ny + nx)/(sqrt(nx*nx + 3*ny*ny + 4*nz*nz + 2*sqrt(3)*nx*ny)));

    A_mid = -(B_p(1) + sqrt(3)*B_p(2) + 2*r)/B_p(3);
    B_mid = (B_p(1)*B_p(1) + B_p(2)*B_p(2) + B_p(3)*B_p(3) + L2*L2 - L1*L1 - r*r)/(2*B_p(3));
    C_mid = A_mid*A_mid + 4;
    D_mid = 2*A_mid*B_mid + 4*r;
    E_mid = B_mid*B_mid - L2*L2 + r*r;

    B_r(1) = (-D_mid - sqrt(D_mid*D_mid - 4*C_mid*E_mid))/(2*C_mid);
    B_r(2) = sqrt(3)*B_r(1);
    B_r(3) = sqrt(L2*L2 - 4*r*B_r(1) - 4*B_r(1)*B_r(1) - r*r);

   % B_r(3) musn't go less than 0

    angle = atan(B_r(3)/(sqrt(B_r(1)*B_r(1) + B_r(2)*B_r(2)) - r))*rad_to_deg;
    
    if (isnan(angle)) % checks for error
        angle = 90;
    end

    angle = angle/2;
end

if(motor == 3)
    % case 3
    C_p(1) = -(r*nz)/(sqrt(nx*nx + 3*ny*ny + 4*nz*nz - 2*sqrt(3)*nx*ny));
    C_p(2) = (sqrt(3)*r*nz)/(sqrt(nx*nx + 3*ny*ny + 4*nz*nz - 2*sqrt(3)*nx*ny));
    C_p(3) = h - (r*(-sqrt(3)*ny + nx)/(sqrt(nx*nx + 3*ny*ny + 4*nz*nz - 2*sqrt(3)*nx*ny)));

    A_mid = -(C_p(1) - sqrt(3)*C_p(2) + 2*r)/C_p(3);
    B_mid = (C_p(1)*C_p(1) + C_p(2)*C_p(2) + C_p(3)*C_p(3) + L2*L2 - L1*L1 - r*r)/(2*C_p(3));
    C_mid = A_mid*A_mid + 4;
    D_mid = 2*A_mid*B_mid + 4*r;
    E_mid = B_mid*B_mid - L2*L2 + r*r;

    C_r(1) = (-D_mid - sqrt(D_mid*D_mid - 4*C_mid*E_mid))/(2*C_mid);
    C_r(2) = -sqrt(3)*C_r(1);
    C_r(3) = sqrt(L2*L2 - 4*r*C_r(1) - 4*C_r(1)*C_r(1) - r*r);

    % C_r(3) musn't go less than 0

    angle = atan(C_r(3)/(sqrt(C_r(1)*C_r(1) + C_r(2)*C_r(2)) - r))*rad_to_deg;
    if (isnan(angle))
        angle = 90;
    end

    angle = angle/2;
end