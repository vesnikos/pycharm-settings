"""
reated by vesnikos at 21/07/2015

Purpose:

Change Log: 
"""

import os
import itertools

file = r"C:\Users\vesnikos\Desktop"

def drange(start,stop,step):
    r = start
    while r <= stop:
        yield str(r)
        r += step


step = 0.5
with open(file+"\lat.csv","w") as f :
    f.writelines("lon,lat,z"+os.linesep)
    for lat in drange(-90,90,step):
        for lon in drange(-180,180,step):
            f.writelines(",".join((lon,lat,lon)))