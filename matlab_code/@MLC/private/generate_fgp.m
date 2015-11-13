function fingerprint=generate_fgp(m,gen_param)
    sensors=gen_param.sensors;
    opset=gen_param.opset;
    nbop=length(opset);   
    for i=1:sensors
       opset(nbop+i).op=['S' num2str(i-1)];
    end
   for i=1:(nbop)
       m=strrep(m,['(' opset(i).op ' '],num2str(i));
   end
   for i=(nbop)+1:length(opset)
       m=strrep(m,[ opset(i).op],num2str(i));
   end
   m=strrep(m,'-','8');m=strrep(m,'.','9');
   m=strrep(m,' ','');m=strrep(m,')','');
   fingerprint=str2double(m);
end
   
