function b=my_log(arg1)
    protection = 0.00001;
    sign_array = sign(arg1);
    protect_array = abs(arg1) < protection;
    elements_to_modify = sum(protect_array);

    if elements_to_modify == 0
        b = log(abs(arg1));
    else
        inverse_protect_array = ~protect_array;
        valid_elements = arg1 .* inverse_protect_array;
        non_valid_elements = protect_array .* protection;
        new_arg1 = valid_elements + non_valid_elements;
        b = log(abs(new_arg1));
    end
end

% function b=my_log(arg1)
%     protec=0.00001;
%     if abs(arg1)>protec
%         b=log(abs(arg1));
%     else
%         b=log(protec);
%     end
% end