function textoutput(mlcind);

switch mlcind.type
    case 'tree'
        fprintf([mlcind.value '\n']);
end