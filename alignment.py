import os,sys
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

### Calcola la permutazione di chip che mi riduce l'angolo medio, in delta strip

from itertools import permutations
import math

def  CheckPermutations(df, doChip=True, doStrip=False):

    if doChip and doStrip:
        print("Too many permutations?")
        return

    ChipShuffle = [ chip for chip in range(0,Hybrid.nchip)]
    StripShuffle = [ Hybrid.nstrip -strip-1 for strip in range(0,Hybrid.nstrip) ]
    #StripShuffle = [ strip for strip in range(0,Hybrid.nstrip) ] 

    ChipPermutations = permutations(range(0,Hybrid.nchip)) if doChip else [ChipShuffle]
    StripPermutations = permutations(range(0,Hybrid.nstrip)) if doStrip else [StripShuffle]

    npermutions = math.factorial(Hybrid.nchip) if doChip else math.factorial(Hybrid.nstrip)
    count = 0
    
    ## Check 4 x 4
    #ChipPermutations = [ range(0,Hybrid.nchip)  , [ Hybrid.nchip -chip -1 for chip in range(0,Hybrid.nchip) ] ]
    StripPermutations = [ range(0,Hybrid.nstrip), [ Hybrid.nstrip -strip -1 for strip in range(0,Hybrid.nstrip)] ]

    Smin= 1e9
    ChipBest = None
    StripBest = None

    for ChipShuffle in ChipPermutations:
        for StripShuffle in StripPermutations:
            count +=1

            if count%1000 ==0: 
                print(".",end='')
            if count%100000 ==0: 
                print(count,"/",npermutations," Best S",Smin)
            sys.stdout.flush()

            S =0.

            iy1 = df["chip1"].map( { i:ChipShuffle[i] for i in range(0,Hybrid.nchip)} ) * Hybrid.nstrip + df["strip1"].map({ i:StripShuffle[i] for i in range(0,Hybrid.nstrip)})
            iy2 = df["chip2"].map( { i:ChipShuffle[i] for i in range(0,Hybrid.nchip)} ) * Hybrid.nstrip + df["strip2"].map({ i:StripShuffle[i] for i in range(0,Hybrid.nstrip)})

            deltaChip = (iy1-iy2).apply(abs).to_numpy()
            deltaChip = np.maximum( deltaChip - 240,0.) ### close by
            S = np.sum(  (deltaChip)**2 )

            #print("Current permutation is (",S,")",ChipShuffle if doChip else "--",StripShuffle if doStrip else '--')
            if S < Smin:
                print("Better permutation is (",S,")",ChipShuffle,"    ",StripShuffle if (count ==0 or doStrip) else '--' ) # if doStrip else '--')
                #print(" ---- > OLD", Smin,ChipBest,StripBest)
                Smin = S
                ChipBest = ChipShuffle
                StripBest = StripShuffle
    print("----------------")
    print("Best permutation is",ChipBest,StripBest)

## too sensible, I need to try multiple possibilities
## CheckPermutations( df[ df['hyb1'] == df ['hyb2']] ,doChip=True, doStrip=False)
#CheckPermutations(doChip=False, doStrip=True)


def CheckCloseByChip(df):
    ChipPermutations = permutations(range(0,Hybrid.nchip)) 
    Smin=1.e9
    for ChipShuffle in ChipPermutations:
        deltaChip = (df['chip1'].map({ i:ChipShuffle[i] for i in range(0,Hybrid.nchip)} ) - df['chip2'].map({ i:ChipShuffle[i] for i in range(0,Hybrid.nchip)} )).to_numpy()
        deltaChip = np.maximum( np.abs(deltaChip)-1,0.)
        #print ("Delta Chip2",deltaChip)
        S = np.sum(deltaChip**2)
        if S <= Smin:
            Smin=S
            print("Better permutation (",S,")",ChipShuffle)

CheckCloseByChip(  df[ df['hyb1'] == df ['hyb2']]   )


def CheckCloseByChipDifferentHyb(df,Shuffle0= [5, 4, 3, 2, 6, 7, 0, 1]):
    print("closeby")
    ChipPermutations = permutations(range(0,Hybrid.nchip)) 
    Smin=1.e9
    for ChipShuffle in ChipPermutations:
        deltaChip = (df['chip1'].map({ i:Shuffle0[i] for i in range(0,Hybrid.nchip)} ) - df['chip2'].map({ i:ChipShuffle[i] for i in range(0,Hybrid.nchip)} )).to_numpy()
        deltaChip = np.maximum( np.abs(deltaChip)-1,0.)
        #print ("Delta Chip2",deltaChip)
        S = np.sum(deltaChip**2)
        if S <= Smin:
            Smin=S
            print("Better permutation (",S,")",ChipShuffle)

CheckCloseByChipDifferentHyb(  df[ df['hyb1'] != df ['hyb2']]   )
