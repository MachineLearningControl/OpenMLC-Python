close all;
clear all;

%--------------------- %

x = -10:0.1:10;
% m = 'exp(((-6.3726) - ((-7.1746) .* S0)))';
m = '((-6.3726) - ((-7.1746) .* S0))';
y = tanh(x.^3-x.^2-1);
m = strrep(m, 'S0', 'x'); y2=eval(m); J=sum((y2-y).^2); fprintf('%.10f\n', J);

filename = './costs_matlab.txt';
file = fopen(filename, 'w');

for i=1:length(x)
    fprintf(file, '%50.50f\n', y2(i));
end

fclose(file);
