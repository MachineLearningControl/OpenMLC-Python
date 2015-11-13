function create_script(mlc,scriptname)
%CREATE_SCRIPT    Method of the MLC class. Writes MLC parameters in a M-file script. 
%   MLC_OBJ.CREATE_SCRIPT opens a GUI to select the file to write.
%   MLC_OBJ.CREATE_SCRIPT(FILENAME) creates the script in the current
%   folder with FILENAME.
%
%   All current members of the <a href="matlab:help
%   MLC/parameters">parameters</a> are written. Only strings and 1-D
%   arrays are supported. To create a script, it is easier to have the file
%   created then edit inside the file than change all parameters manually
%   and then create the script. But it is just my opinion, you do what you
%   want.
%
%   Ex: 
%      mlc=MLC;mlc.create_script('merguez');open('merguez.m');
%
%   See also MLC, PARAMETERS, Set_MLC_parameters, OPSET
%
%   Copyright (C) 2013 Thomas Duriez (thomas.duriez@gmail.com)
%   This file is part of the TUCOROM MLC Toolbox

if nargin<2
    [fichier, chemin]=uiputfile('my_script.m','Choose your script file');
    scriptname=fichier;
else
    fichier=scriptname;
    chemin='';
end
k=strfind(scriptname,'.m');
    if isempty(k)
        fichier=[scriptname '.m'];
    else
        scriptname=scriptname(1:k-1);
    end
fid=fopen(fullfile(chemin,fichier),'w');
string=['%%' upper(scriptname) '    parameters script for MLC\n'];
fprintf(fid,string);
fprintf(fid,['%%    Type mlc=MLC(''' scriptname ''') to create corresponding MLC object\n']);
fields=fieldnames(mlc.parameters);
excludefields={'opset','dispswitch'};
for i=1:length(fields);
    if ~strcmp(fields{i},excludefields)        
        value=getfield(mlc.parameters,fields{i});
        if ischar(value)
            fieldvalue=['''' value ''''];
        elseif isstruct(value)
            fprintf(1,['Field "' fields{i} '" is a structure, add it later manually in the file.\n']);
            fprintf(1,'(I am lazy)\n');
        elseif isnumeric(value)
            if min(size(value))==1
                fieldvalue=['[' sprintf([repmat('%g ',[1 length(value)-1]) '%g'],value) ']'];
                if length(value)==1;
                    fieldvalue=fieldvalue(2:end-1);
                end
            else
                fprintf(1,['Field "' fields{i} '" is a matrix, add it later manually in the file.\n']);
                fprintf(1,'(Did you HAVE to do this ?)\n');
            end
        end
        fprintf(fid,['parameters.' fields{i} '=' fieldvalue ';\n']);
    end
end
end

