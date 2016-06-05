close all;
clear all;

%-------------%
% Add paths to run MLC. Run the script from this folder to work properly
addpath(genpath('../matlab_code'));

% Create simulation
mlc = MLC2();
mlc.go(7,0);


% File Format: property1=value@property2=value@...@propertyN=value
indiv_format = ['value=%s@' ...
                'cost=%.5f@' ...
                'appearences=%d@' ...
                'complexity=%d\n'];

indiv = mlc.table.individuals(1:mlc.table.number);
filename = './individuals.txt';
file = fopen(filename, 'wt');
for idx = 1:numel(indiv)
    fprintf(file, ...
            indiv_format, ...
            indiv(idx).value, ...
            indiv(idx).cost, ...
            indiv(idx).appearences, ...
            indiv(idx).complexity);
end
fclose(file);

% File Format: Population_Number@property1=value@...@propertyN=value
% index=value@property1=value@...@property2=value$index=value@cost=value 
% (Every line is a different population)
filename = './populations.txt';
file = fopen(filename, 'wt');
indiv_format = ['index=%d@' ...
                'cost=%.10f@' ...
                'gen_method=%d'];

pop = mlc.population;
for idx = 1:numel(pop)
    for i = 1:length(pop(idx).costs)
        fprintf(file, ...
                indiv_format, ...
                pop(idx).individuals(i), ...
                pop(idx).costs(i), ...
                pop(idx).gen_method(i));

        if i ~= length(pop(idx).costs)
            fprintf(file, '$');
        end
    end
    fprintf(file, '\n');
end
fclose(file);

exit(0);
