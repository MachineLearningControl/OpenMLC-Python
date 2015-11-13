function xp=poincarre_map(Y);
    dx=diff(sign(Y(:,1)));
    idx=find(dx==2);
    length=Y(idx,:)-Y(idx+1,:);
    ratio=abs(Y(idx,1))./length(:,1);
    xp=Y(idx,:)+length.*repmat(ratio,[1 3]);
    
        