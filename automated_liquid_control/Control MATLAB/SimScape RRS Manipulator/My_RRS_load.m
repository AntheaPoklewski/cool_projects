Ts = 0.001;
[DOF_My_RRS, Info] = importrobot("My_RRS", "BreakChains", "remove-joints", 'ConvertJoints','convert-to-fixed');