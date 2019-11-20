m=int;l=input;*r,e,p,c,a,t=map(m,l().split());x={};exec("i,j=map(m,l().split());x[i]=j;"*t)
while 1:g,h,d=l().split();g=m(g);h=m(h);d=len(d);print(["BLOCK","WAIT"][g<0 or(g==e and((p>h and d>4)or(p<h and d<5)))or(g!=e and((x[g]>h-1 and d>4)or(x[g]<h+1 and d<5)))])
