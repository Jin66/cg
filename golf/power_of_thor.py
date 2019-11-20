# Best so far
j,k,x,y=map(int,input().split())
while 1:b,c=k>y,(x>j)-(x<j);y+=b;x+=c;print("S"[0:b]+" WE"[c].strip())
