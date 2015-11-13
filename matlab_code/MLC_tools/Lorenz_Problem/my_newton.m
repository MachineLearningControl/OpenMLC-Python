function s = my_newton(equa,cont,f, x, tol)
   % f is a multivariable function handle, x is a starting point, both given as row vectors
   % s is solution of f(s)=0 found by Newton's method
	tic
   if nargin == 4
       tol = 10^(-12);
   end
   while 1
       % if x and f(x) are row vectors, we need transpose operations here
	x=x(:);
       y = x - my_jacob2(equa,cont, x)\f(x);             % get the next point
       if norm(f(y))<tol | toc>10                      % check error tolerate
           s = y(:);
           return;
       end
       x = y(:);
   end
