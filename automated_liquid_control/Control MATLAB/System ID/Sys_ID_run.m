% Load data
SID_Roll = readmatrix('C:\Users\anthe\OneDrive - University of Pretoria\UP\Final Year\EPR 400\STM Things\SID\Roll_Data.xlsx'); 
SID_Pitch = readmatrix('C:\Users\anthe\OneDrive - University of Pretoria\UP\Final Year\EPR 400\STM Things\SID\Pitch_Data.xlsx');

SID1_Input = SID_Roll(:, 1);
SID1_Roll =  SID_Roll(:, 2);
SID1_Pitch =  SID_Roll(:, 3);

SID2_Input = SID_Pitch(:, 1);
SID2_Roll = SID_Pitch(:, 2);
SID2_Pitch = SID_Pitch(:, 3);

figure(1)
plot(SID1_Pitch)

figure(2)
plot(SID1_Input)

% New input data 
T = 31.33*(1/6.51);
fs = 416;
t = 0:1/fs:T-1/fs;
x = 25*((sawtooth(2*pi*(6.51)*t,1/2))+1);

figure(3)
plot(t,x)

x_trans = x';
x_trans = x_trans(1:2002, 1);
grid on

Ts = 1/416;

% iddata
z = iddata(SID1_Pitch, x_trans, 416); 
figure(4)
plot(z)

z1 = z(65:1000);
z2 = z(1001:2002);

% NLARX
mw1 = nlarx(z1,[6 6 2], idWaveletNetwork); % 5 4 4 % 2 2 1

% Run model
model = 'SID_controller';
open_system(model)
simOut = sim(model);
open_system([model '/Scope'])

x0 = findstates(mw1,z1,Inf);
set_param([model '/Nonlinear ARX Model'],'ICspec','State values','X0','x0');
simOut = sim(model);

