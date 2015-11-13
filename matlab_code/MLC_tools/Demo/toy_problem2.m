function J=toy_problem2(ind,parameters,i,fig)
xmin=-1;
xmax=1;
ymin=-1;
ymax=1;
dx=0.5;
dy=0.5;

[x0,y0]=meshgrid(xmin:dx:xmax,ymin:dy:ymax);
z0=cos(x0).*sin(y0)-x0.*y0;%mlc+(rand(size(x0))-0.5)/10;

%% calculating the surface over the grid
try
m=readmylisp_to_formal_MLC(ind,parameters);
m=strrep(m,'S0','x0');
m=strrep(m,'S1','y0');
z0_2=x0*0;
eval(['z0_2=' simplify_my_LISP(m) ';']);
z0_2=z0_2+x0*0;
J=sum((z0(:)-z0_2(:)).^2);


[x,y]=meshgrid(xmin:dx/100:xmax,ymin:dy/100:ymax);
m=strrep(m,'x0','x');
m=strrep(m,'y0','y');
z=x*0;
eval(['z=' simplify_my_LISP(m) ';']);
    

if nargin==4
    s=surf(x,y,z);hold on
    plot3(x0,y0,z0,'o','color','k','markerfacecolor','k','markersize',10);
    for i=1:length(x0(:))
    plot3([x0(i) x0(i)],[y0(i) y0(i)],[0 z0(i)],'k','linewidth',3);
    end
    hold off
    shading interp
    set(s,'facealpha',0.5);
end

catch err
    J=parameters.badvalue;
end