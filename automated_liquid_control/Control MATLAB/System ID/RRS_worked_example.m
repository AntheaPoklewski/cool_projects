%% 3RRS Worked Example from Paper

% 1) Position Analysis --------------------------------------------
% Constants
pi = 3.141592654;

ra1 = [0.45 0 0]'; % (m)
ra2 = [-0.225 0.3897 0]'; % (m)
ra3 = [-0.225 -0.3897 0]'; % (m)

rb1 = [7 0 0]';
rb2 = [-0.35 0.6062 0]'; % (m)
rb3 = [-0.35 -0.6062 0]'; % (m)

yb1_dash = [0 0 0];
yb2_dash = [0 0 0];
yb3_dash = [0 0 0];

xb1_dash = [0 0 0];
xb2_dash = [0 0 0];
xb3_dash = [0 0 0];

zb1_dash = [0 0 0];
zb2_dash = [0 0 0];
zb3_dash = [0 0 0];

% unit vectors
ub1 = [0 1 0]';
ub2 = [-sqrt(3)/2 -1/2 0]';
ub3 = [sqrt(3)/2 -1/2 0]';

Rob1 = [0 -1 0;
        1 0 0;
        0 0 1];

Rob2 = [-sqrt(3)/2 1/2 0;
        -1/2 -sqrt(3)/2 0;
        0 0 1];

Rob3 = [sqrt(3)/2 1/2 0;
        -1/2 sqrt(3)/2 0;
        0 0 1];

ru1_0 = [0 0 0.5]';
ru2_0 = [0 0 0.5]';
ru3_0 = [0 0 0.5]';

rd1_0 = [0 0 0.5]';
rd2_0 = [0 0 0.5]';
rd3_0 = [0 0 0.5]';

mu1 = 12; % kg
mu2 = 12;
mu3 = 12;

md1 = 12; % kg
md2 = 12;
md3 = 12;
mp = 68; 

Iu1_0 = [6.2 0 0;
         0 6.2 0;
         0 0 0.5]; % kg.m2

Iu2_0 = [6.2 0 0;
         0 6.2 0;
         0 0 0.5]; % kg.m2

Iu3_0 = [6.2 0 0;
         0 6.2 0;
         0 0 0.5]; % kg.m2

Id1_0 = [6.2 0 0;
         0 6.2 0;
         0 0 0.5]; % kg.m2

Id2_0 = [6.2 0 0;
         0 6.2 0;
         0 0 0.5]; % kg.m2

Id3_0 = [6.2 0 0;
         0 6.2 0;
         0 0 0.5]; % kg.m2

Ip = [28 0 0;
      0 36 0;
      0 0 20]; % kg.m2

rp = [0.1 0 1]';

Rop = [cos(-0.25) 0 sin(-0.25);
      0 1 0;
      -sin(-0.25) 0 cos(-0.25)]; 

T = 6;
fs = 6664; % Hz <- IMU has 100 Hz <- 100 Hz test
ts = 1/fs;
t_len = 6; 
n = 10;
totalNumSamples = n*(t_len/ts);  
t = (0:(totalNumSamples-1)).'/fs;

vx_dot = [(0.12/T.^2)*(60*t/T - (180*t.^2)/(T.^2) + (120*t.^2)/(T.^3));
          (0.1/T.^2)*(60*t/T - (180*t.^2)/(T.^2) + (120*t.^2)/(T.^3));
          (0.5/T.^2)*(60*t/T - (180*t.^2)/(T.^2) + (120*t.^2)/(T.^3))];

Lbc_length = [1 1 1];
Lca_length = [1 1 1];

% Vectors 
% Lba 
Lba1 = rp + Rop*ra1 - rb1;
Lba2 = rp + Rop*ra2 - rb2;
Lba3 = rp + Rop*ra3 - rb3;

% Joint angles 
alpha1 = acos((Lbc_length(1).^2 + norm(Lba1).^2 - Lca_length(1).^2)/(2*Lbc_length(1)*norm(Lba1)));
alpha2 = acos((Lbc_length(2).^2 + norm(Lba2).^2 - Lca_length(2).^2)/(2*Lbc_length(2)*norm(Lba2)));
alpha3 = acos((Lbc_length(3).^2 + norm(Lba3).^2 - Lca_length(3).^2)/(2*Lbc_length(3)*norm(Lba3)));

beta1 = acos(dot(Lba1, yb1_dash)/norm(Lba1));
beta2 = acos(dot(Lba2, yb2_dash)/norm(Lba2));
beta3 = acos(dot(Lba3, yb3_dash)/norm(Lba3));

lamda1 = acos((Lca_length(1).^2 + Lbc_length(1).^2 - norm(Lba1).^2)/(2*Lca_length(1)*Lbc_length(1)));
lamda2 = acos((Lca_length(2).^2 + Lbc_length(2).^2 - norm(Lba2).^2)/(2*Lca_length(2)*Lbc_length(2)));
lamda3 = acos((Lca_length(3).^2 + Lbc_length(3).^2 - norm(Lba3).^2)/(2*Lca_length(3)*Lbc_length(3)));

% Leg Position 1 (positive) (i=1,2,3)
qb1 = alpha1 + beta1 - pi/2; % (rad)
qb2 = alpha2 + beta2 - pi/2; % (rad)
qb3 = alpha3 + beta3 - pi/2; % (rad)

qc1 = lamda1 - pi; % (rad)
qc2 = lamda2 - pi; % (rad)
qc3 = lamda3 - pi; % (rad)

% % Leg Position 1 (negative) (i=1,2,3)
% qb1 = beta1 - alpha1 - pi/2;
% qb2 = beta2 - alpha2 - pi/2;
% qb3 = beta3 - alpha3 - pi/2;
% 
% qc1 = pi - lamda1;
% qc2 = pi - lamda2;
% qc3 = pi - lamda3;

% Referece change
Rub1 = [1 0 0;
        0 cos(qb1) -sin(qb1);
        0 sin(qb1) cos(qb1)];

Rub2 = [1 0 0;
        0 cos(qb2) -sin(qb2);
        0 sin(qb2) cos(qb2)];

Rub3 = [1 0 0;
        0 cos(qb2) -sin(qb2);
        0 sin(qb2) cos(qb2)];

Ruc1 = [1 0 0;
        0 cos(qc1) -sin(qc1);
        0 sin(qc1) cos(qc1)];

Ruc2 = [1 0 0;
        0 cos(qc2) -sin(qc2);
        0 sin(qc2) cos(qc2)];

Ruc3 = [1 0 0;
        0 cos(qc3) -sin(qc3);
        0 sin(qc3) cos(qc3)];

% Leg vectors
% Lbc
% Lca
Lbc1 = (Rob1.*Rub1).*[0, 0, Lbc_length(1)]';
Lbc2 = (Rob2.*Rub2).*[0 0 Lbc_length(2)]';
Lbc3 = (Rob3.*Rub3).*[0 0 Lbc_length(3)]';

Lca1 = Lba1 - Lbc1;
Lca2 = Lba2 - Lbc2;
Lca3 = Lba3 - Lbc3;

% Position vectors upper and lower links
ru1 = Lbc1 + Rob1.*Ruc1.*ru1_0;
ru2 = Lbc2 + Rob2.*Ruc2.*ru2_0;
ru3 = Lbc3 + Rob3.*Ruc3.*ru3_0;

rd1 = Rob1.*Rub1.*rd1_0;
rd2 = Rob2.*Rub2.*rd2_0;
rd3 = Rob3.*Rub3.*rd3_0;

% 2) Velocity Analysis ---------------------------------------------------
omega = zeros(3, 3); % omega_x, omega_y, omega_z
v = zeros(3, 3); % vx, vy, vz

va1 = v + cross(omega, Rop.*ra1);
va2 = v + cross(omega, Rop.*ra2);
va3 = v + cross(omega, Rop.*ra3);


