function b=my_pow(arg1,arg2)
arg2=abs(arg2);
arg2=(arg2<1) + round((arg2>=1).*arg2);

b=arg1.^arg2;