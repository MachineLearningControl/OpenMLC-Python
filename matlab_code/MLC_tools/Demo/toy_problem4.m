function J=toy_problem4(ind,gen_param,i,fig)
problemvars.x0=[-5 7 -8];
problemvars.y0=[-7 0 9]; 
problemvars.z0=[-3 4 4];
problemvars.gamma=2;
problemvars.xmin=-10;
problemvars.xmax=10;
problemvars.ymin=-10;
problemvars.ymax=10;
problemvars.dx=1;
problemvars.dy=1;

x0=problemvars.x0;
y0=problemvars.y0;
z0=problemvars.z0;
gamma=problemvars.gamma;
xmin=problemvars.xmin;
xmax=problemvars.xmax;
ymin=problemvars.ymin;
ymax=problemvars.ymax;
dx=problemvars.dx;
dy=problemvars.dy;
[xx,yy]=meshgrid(xmin:dx:xmax,ymin:dy:ymax); %creating the grid points
zz=xx*0; % memory allocation
dist=x0*0; % memory allocation
%% calculating the surface over the grid
m=readmylisp_to_formal_MLC(ind,gen_param);
m=strrep(m,'y(1)','xx');
m=strrep(m,'y(2)','yy');

eval(['zz=' simplify_my_LISP(m) ';']);
zz=zz+xx*0;
J1=sum(zz(:).^2)/(20*20);

%% calculating distance to points
m=strrep(m,'xx','x0');
m=strrep(m,'yy','y0');
eval(['z0_2=' m ';']);

J2=sum((z0-z0_2).^2);


J=J2+gamma*J1+(rand)*gen_param.artificialnoise;


if nargin==4
    surf(xx,yy,zz);hold on
    plot3(x0,y0,z0,'o','color','k','markerfacecolor','k','markersize',30);
    for i=1:3
    plot3([x0(i) x0(i)],[y0(i) y0(i)],[0 z0(i)],'k','linewidth',3);
    end
    hold off
    shading interp
end