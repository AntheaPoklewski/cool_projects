SID_Roll = readmatrix('C:\Users\anthe\OneDrive - University of Pretoria\UP\Final Year\EPR 400\STM Things\SID\Roll_Data.xlsx'); 
SID_Pitch = readmatrix('C:\Users\anthe\OneDrive - University of Pretoria\UP\Final Year\EPR 400\STM Things\SID\Pitch_Data.xlsx');

SID1_Input = SID_Roll(:, 1);
SID1_Roll =  SID_Roll(:, 2);
SID1_Pitch =  SID_Roll(:, 3);

SID2_Input = SID_Pitch(:, 1);
SID2_Roll = SID_Pitch(:, 2);
SID2_Pitch = SID_Pitch(:, 3);

% New input data 
figure(1)
T = 31*(0.16);

fs = 416;
t = 0:1/fs:T-1/fs;

x = 25*((sawtooth(2*pi*(1/0.16)*t,1/2))+1);
plot(t,x)

x = x';
x = x(1:2002, 1);
grid on


Ts = 1/416;

% ARX Modelling - Load Data
% Can be edited by adding in motion of all three servos and corresponding 
% z = iddata([SID1_Roll, SID1_Pitch],[SID1_Input, SID1_Input], Ts); % [out out][in in]
% z.InputName  = {'Servo Angle P1';'Servo Angle P2'};
% z.OutputName = {'Roll (degrees)';'Pitch (degrees)'};
% 
% z_valid = iddata([SID2_Roll, SID2_Pitch],[SID2_Input, SID2_Input], Ts);
% z_valid.InputName  = {'Servo Angle R1 Valid';'Servo Angle R2 Valid'};
% z_valid.OutputName = {'Roll Valid (degrees)';'Pitch Valid (degrees)'};
% 

z_valid = iddata(SID1_Pitch, SID1_Input, 416); 
figure(2)
plot(z_valid(:,1,1))
% 
% figure(2)
% plot(z(:,2,2))
% 
% figure(3)
% plot(z_valid(:,1,1))
% 
% figure(4)
% plot(z_valid(:,2,2))

% NN = [ones(2,2), ones(2,6), ones(2,6)]; % the orders
% mw1 = nlarx(z, NN, idWaveletNetwork);
% compare(z,mw1)

z = iddata(SID1_Pitch, x, 416); 

figure(3)
plot(z)

% figure(3)
% mi = impulseest(z,50);
% clf, step(mi)
% 
% figure(4)
% showConfidence(impulseplot(mi),3)
% 
% figure(5)
% mp = ssest(z(100: 450));
% h = stepplot(mi,'b',mp,'r',2); % Blue for direct estimate, red for mp
% showConfidence(h)
% 
% figure(6)
% title("Plot Data")
% compare(z,mp)
% 
% figure(7)
% title("Plot Validation")
% compare(z_valid,mp)

%% Trying non-linear model ARX

% nx = 2;
% sys = ssest(z,nx);
% 
% figure(3)
% compare(z,sys)

z1 = z(50:1500);
% z2 = z(1001:2002);
% 
% V = arxstruc(z1, z2, struc(1:2, 1:2, 1:2));
% nn = selstruc(V,'aic');
% 
% mw1 = nlarx(z1,[2 1 1], idWaveletNetwork);
% NLFcn = mw1.OutputFcn;
% NLFcn.NonlinearFcn.NumberOfUnits
% 
% figure(3)
% compare(z1,mw1);

% Options = n4sidOptions;                            
% Options.Display = 'on';                            
% Options.N4Horizon = [15 34 34];                    
% 
%  ss2 = n4sid(z, 3, 'Form', 'free', 'Ts', 0, Options);
% 
% figure(3)
% compare(z, ss2);

figure(4)
% opt = arxOptions('Focus','simulation');
% LinearModel = arx(z1,[2 1 1], opt);
% 
% optNL = nlarxOptions('Focus','simulation');
% NonlinearModel = nlarx(z1,LinearModel,'idSigmoidNetwork');
% compare(NonlinearModel, z1);

% mw2 = nlarx(z1,[2 1 2], idWaveletNetwork(8));
% compare(z1, mw2);

na = 1;
nb = 1;
nk = 2;
NN = [na nb nk]; % the orders
mw1 = arx(z1, NN);
mw2 = nlarx(z1, NN, idSigmoidNetwork);
compare(z1, mw1)

figure(5)
compare(z1, mw2)
getreg(mw2)

