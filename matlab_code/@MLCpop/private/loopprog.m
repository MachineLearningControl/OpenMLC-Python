function loopprog(n)
    fid=fopen('looppg.txt','a+');
    txt=fscanf(fid,'%s');
    fprintf(fid,'X');
    fclose(fid);
    if isempty(txt)
        ach=1;
    elseif length(txt)==n-1
        ach=n;
        delete('looppg.txt')
    else 
        ach=length(txt)+1;
    end   
%     if ach/n >=0.1 && (ach-1)/n <0.1
%         fprintf('10%% done\n')
%     elseif ach/n >=0.2 && (ach-1)/n <0.2
%         fprintf('20%% done\n')
%     elseif ach/n >=0.3 && (ach-1)/n <0.3
%         fprintf('30%% done\n')
%     elseif ach/n >=0.4 && (ach-1)/n <0.4
%         fprintf('40%% done\n')
%     elseif ach/n >=0.5 && (ach-1)/n <0.5
%         fprintf('50%% done\n')
%     elseif ach/n >=0.6 && (ach-1)/n <0.6
%         fprintf('60%% done\n')
%     elseif ach/n >=0.7 && (ach-1)/n <0.7
%         fprintf('70%% done\n')
%     elseif ach/n >=0.8 && (ach-1)/n <0.8
%         fprintf('80%% done\n')
%     elseif ach/n >=0.9 && (ach-1)/n <0.9
%         fprintf('90%% done\n')
%     elseif ach==n 
%         fprintf('100%% done\n')
%     end
       fprintf('%2.2f %% evaluated\n',ach/n*100)
            
    end

    