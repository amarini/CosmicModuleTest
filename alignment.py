from argparse import ArgumentParser
parser=ArgumentParser()

args=parser.parse_args()

from cosmics.geometry import *
import pandas as pd
import numpy as np

df = pd.read_csv("processed/run4.csv")
#df = pd.read_csv("run2.csv")

### the actual geometry is implemented here
from cosmics.tower import *


from scipy.optimize import minimize

def computeX(m,x,w='1',field=1):
    s = m.get( x['hyb' + w] , x['z'+w] , x['chip'+w],x['strip'+w] )
    mid = (s.start + s.stop)/2.
    return mid[field]


df["dy"] = df.apply( lambda x: computeX(m0,x,'1') - computeX(m1,x,'2'), axis=1)
df["dz"] = df.apply( lambda x: computeX(m0,x,'1',field=2) - computeX(m1,x,'2',field=2), axis=1)

### minimizzare dx
print ("-- Y --")
#print ( df["dy"].describe()) 
print (df[ df["hyb1"] == df["hyb2"] ] ["dy"].describe())

print ("-- Z --")
#print (df["dz"].describe())
print (df[ df["hyb1"] == df["hyb2"] ] ["dz"].describe())

#print (df["dz"].describe())
print ("-- Y2 --")
print (df[ df["hyb1"] != df["hyb2"] ] ["dy"].describe())


