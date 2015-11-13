function R=recurrence_plot(T,Y,n,threshold);
for i=1:3
    yy(:,i)=interp1(T,Y(:,1),linspace(0,max(T),n));
end

    for i=1:n;
        for j=1:n;
            R(i,j)=sqrt(sum((yy(i,:)-yy(j,:)).^2));
        end
    end
    if nargin==4
        R=(R<threshold)-1+1;
    end
    surf(repmat(linspace(0,max(T),n)',[1 n]),repmat(linspace(0,max(T),n),[n 1]),R)
    view(0,90)