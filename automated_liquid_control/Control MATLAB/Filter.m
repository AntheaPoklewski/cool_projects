% n = 1;  % Order of the Bessel function
% j = 1;  % The j-th root we want to find
% 
% % Define the derivative of the Bessel function
% bessel_deriv = @(x) (besselj(n-1, x) - besselj(n+1, x)) / 2;
% 
% % Use fzero to find the roots of the derivative
% initial_guess = j * pi; % Initial guess for the j-th root
% root_jth = fzero(bessel_deriv, initial_guess);
% 
% disp(['The ', num2str(j), '-th root of the derivative of J_', num2str(n), '(x) is: ', num2str(root_jth)]);

delta = 0.0033;
% delta = 5.4854;
omega = 20.6122;
gamma = -delta*omega;
pi = 3.141592;

% T = (3/2)*(2*pi/(omega*sqrt(1-delta*delta)));
% K = (delta*delta + (pi/T)*(pi/T))/(1 + exp(delta*T));
% 
% s = tf('s');
% F = K*(1 + exp(-s*T)*exp(delta*T))/((s-delta)^2 + (pi/T)^2); 
% Ts = 0.01; % Sampling period is 10 ms
% sys_z = c2d(F, Ts, 'zoh'); % discrete equivalent
% 
% [num_z, den_z] = tfdata(sys_z, 'v');
% disp(num_z);
% disp(den_z);

fs = 100; % Hz <- IMU has 6664 Hz <- 100 Hz test
ts = 1/fs;
t_len = 5; 
n = 10;
totalNumSamples = n*(t_len/ts);   
% t = (0:(totalNumSamples-1)).'/fs;

% q0 = 0;
% h_disp = 30;
% 
% for t = 0:totalNumSamples
%     q_h = q0 + (h_disp/(1 + exp(delta*T)))*(1 + exp(delta*t)*((delta*T/pi)*sin(pi*t/T)-cos(pi*t/T)));
% end
% 
% plot(q_h)

% State space of slosh model 
A = [0 1; -424.85 -0.136];
B = [0; 1];
C = [1 0];
D = 0;

sys = ss(A, B, C, D);
E = eig(A);

% P = [-2 -1]; % <- the more left, the more aggressive the controller - not always possible with actuators [-10 -8]
P = [-10 -7];
K = place(A, B, P);

Acl  = A - B*K;
Ecl = eig(Acl);

syscl = ss(Acl, B, C, D);
[val1, t1] = step(sys);

figure(1)
plot(t1, val1,'b')
xlabel('');
ylabel('');
xlabel('Time (s)','FontName','Times New Roman','FontSize', 18)
ylabel('Amplitude (Degrees)','FontName','Times New Roman','FontSize', 18)
set(gca, 'FontName', 'Times New Roman','LineWidth', 1.8)
set(gca, 'XColor', 'k', 'YColor', 'k', 'LineWidth', 1.8)
set(gca, 'FontSize', 18);  % Make tick label numbers larger
title('');
box on
grid on
hold off;
cleanfigure;
% filepath = 'C:/Users/anthe/OneDrive - University of Pretoria/UP/Final Year/EPR 400/Report/EPR 400 Template v2/Figures/Design/SID.tex';
% matlab2tikz(filepath, 'width', '\fwidth', 'simplify', true, 'minimumPointsDistance', 0.01);

figure(2)
step(syscl)

Kdc = dcgain(syscl);
Kr = 1/Kdc;

syscl_scaled = ss(Acl, B*Kr, C, D);
[val2, t2] = step(syscl_scaled);

figure(3)
plot(t2, val2, 'b','LineWidth', 1)
hold on
plot([0.7188 0.7188],[0 0.9799],'Color','r', 'Linestyle', '--', 'Linewidth', 2) % Ts
hold on
plot([0.47458 0.47458],[0 0.9],'Color','g', 'Linestyle', '--', 'Linewidth', 2) % Tr
hold on
plot([0.98 0.98],[0 0.9966],'Color','m', 'Linestyle', '--', 'Linewidth', 2) % Tp
hold on
plot([0 0.98],[0.9966 0.9966],'Color','m', 'Linestyle', '--', 'Linewidth', 2) % Tp
hold on
plot([0 0.7188],[0.9799 0.9799],'Color','r', 'Linestyle', '--', 'Linewidth', 2) % Ts
hold on
plot([0 0.47458],[0.9 0.9],'Color','g', 'Linestyle', '--', 'Linewidth', 2) % Tr
hold on
plot([0.0636 0.0636],[0 0.1],'Color','g', 'Linestyle', '--', 'Linewidth', 2) % Tr
hold on
plot([0 0.0636],[0.1 0.1],'Color','g', 'Linestyle', '--', 'Linewidth', 2) % Tr
hold on
xlabel('Time (s)','FontName','Times New Roman','FontSize', 18)
ylabel('Amplitude (Degrees)','FontName','Times New Roman','FontSize', 18)
set(gca, 'FontName', 'Times New Roman','LineWidth', 1.8)
set(gca, 'XColor', 'k', 'YColor', 'k', 'LineWidth', 1.8)
set(gca, 'FontSize', 18);  % Make tick label numbers larger
xlim([0 1.0]);
ylim([0 1.03]);
legend({'Step', 'Ts', 'Tr', 'Tp'}, 'Location','southeast')
grid on
hold off;
cleanfigure;

S = stepinfo(syscl_scaled);


