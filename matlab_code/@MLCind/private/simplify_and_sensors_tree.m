function m=simplify_and_sensors_tree(m,gen_param)

    
    if gen_param.sensor_spec
        slist=sort(gen_param.sensor_list);
        for i=length(slist):-1:1
            m=strrep(m,['z' num2str(i-1)],['S' num2str(slist(i))]);
        end
    else
        for i=gen_param.sensors:-1:1
            m=strrep(m,['z' num2str(i-1)],['S' num2str(i-1)]);
        end
    end
    
    if gen_param.simplify
        m=simplify_my_LISP(m,gen_param);
    end