% Continuous PID with tuning
G = zpk([],[-1,-1],1); % Plant
C = pid(2,1.3,0.3,0.5); % Controller
F = tf(1,[1 1]);
open_loop = G*C;
T = feedback(G*C,S);
Try = T*F;


stepplot(Try)




% Discrete PID things
% Need a PID response in the x direction related to the pitch
% Step time
fs = 6664; % Hz <- IMU has 100 Hz <- 100 Hz test
ts = 1/fs;
t_len = 5; % 5 seconds
n = 10;
totalNumSamples = n*(t_len/ts);   
t = (0:(totalNumSamples-1)).'/fs;

setpointPitch = 10; % Force applied in x direction corresponds to pitch

for i = 1:totalNumSamples
    errorPrev[i] = error[i] 
end

% Need a PID response in the y direction related to the roll