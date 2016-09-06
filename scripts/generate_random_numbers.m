close all;
clear all;

% Set the random seed
rand('seed', 20.0);

% Create the random file
filename = './matlab_randoms.txt';
file = fopen(filename, 'w');
for i=1:1000000
    fprintf(file, '%f\n', rand());
end
fclose(file);
exit(0);
