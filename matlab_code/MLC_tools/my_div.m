function b=my_div(arg1,arg2)
    protection = 0.001;
    sign_array = sign(arg2);
    protect_array = abs(arg2) < protection;
    elements_to_modify = sum(protect_array);

    if elements_to_modify == 0
        b=arg1 ./ arg2;
    else
        inverse_protect_array = ~protect_array;
        valid_elements = arg2 .* inverse_protect_array;
        non_valid_elements = protect_array .* protection;
        new_arg2 = valid_elements + non_valid_elements;
        b = sign_array .* arg1 ./ new_arg2;
    end

% function b=my_div(arg1,arg2)
%     protec=0.001;
%     if abs(arg2)>protec
%         b=arg1./arg2;
%     else
%         b=sign(arg2).*arg1./protec;
%     end
% end
