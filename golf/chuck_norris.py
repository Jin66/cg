# Best so far
s=r=""
for i in "".join([bin(ord(x))[2:].zfill(7)for x in input()]):
    if s!=i:r+=[" 00 "," 0 "][int(i)]
    r+="0";s=i
print(r[1:])
