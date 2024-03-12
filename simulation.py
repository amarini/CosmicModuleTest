import numpy as np
import pandas as pd
import math
import sys,os

## be geometry aware
from cosmics.geometry import *
## pseudo random
np.random.seed(123456)



### La distribuzione dei raggi cosmici e'
## cos^2 theta


#from geometry import *

Costmin=0
Emin=0 ## useless
Emax=10
Nint = 70.E-4 * 2 * np.pi ## /cm^2/s/sr
## cos^2 theta

#def dN(E,cost):
#    return cost**2 / np.sqrt(1. - cost**2)  ## ~ cos^2t dt

def dN(E,theta):
    return math.cos(theta)**2 # * math.sin(theta)
Nmax =1

def sample():
    global calls
    ## Energy is in GeV
    #if calls[0] %10000 == 0: print("Gen efficiency",calls)

    ##
    ok = False
    while not ok:
        E = np.random.uniform (Emin,Emax)
        #cost = np.random.uniform(Costmin,1)
        theta = np.random.uniform(0,np.pi/2.)
        accept = np.random.uniform(0, Nmax)
        #N = dN(E,cost)
        N = dN(E,theta)

        if accept <= N: ok=True
    cost = math.cos(theta)
    return E, cost


def gen_one(S=Hybrid.dz*Hybrid.dy/100.):
    global Nint
    ### phi
    E, cost = sample()
    phi = np.random.uniform()* 2* np.pi
    ### do I want to keep track of the normalization?
    dt =  np.random.exponential( 1./ (Nint*S) )

    return E, cost,phi, dt

if True: ### Generation routine
    df = pd.DataFrame({"E":[],"cost":[],"phi":[],"dt":[]})
    for i in range(0,10000):
        if i%100==0: 
            print(".",end='')
            sys.stdout.flush()
        E, cost, phi, dt = gen_one()
        #df.append( {"E":E,"cost":cost,"phi":phi,"dt":dt} )
        df.loc[len(df)] = [E,cost,phi,dt] 

    #print("Gen eff",calls)

    df["t"] = df['dt'].cumsum()
    df.to_csv("cosmics_simulation.csv")

if True:
    df = pd.read_csv("cosmics_simulation.csv") ## reload it from csv
    from scipy.spatial.transform import Rotation
    
    from cosmics.tower import *

    ## Assume Generation surface is on m0 hyb0
    hyb = m0.get(0) 
    R = Rotation.from_euler('xyz',hyb.theta)
    l = np.array([Hybrid.dx,Hybrid.dy,Hybrid.dz])
    
    impact=[]
    impact2=[]
    isinhyb0 = []
    isinhyb1 = []

    for i in range(0,len(df)):
        ## impact point coorditates
        z = np.random.uniform()
        y = np.random.uniform()
        x = 0.

        ## prepare list of vertices
        point = np.array([x,y,z])  ##
        point = point * l 
        point = hyb.x + R.apply(point)

        impact.append(point)
    

        ## Propagate to the other module
        cost = df["cost"].to_numpy()[i]
        sint = math.sqrt(1.-cost*cost)
        tant = sint/cost
        phi = df['phi'].to_numpy()[i]
    
        ### Assume horizontal modules
        dx = m1.get(0).x[0]-m0.get(0).x[0] ## Assume horizontal modules TODO: generalize
        r = dx * tant  ## dx * tan(theta)
        dy = r * math.cos(phi)
        dz = r * math.sin(phi)
        
        point2 = point + np.array([dx,dy,dz])
        impact2 .append(point2)


        ### check if it is in or out
        hyb0 = m1.get(0)
        hyb1 = m1.get(1)

        isinhyb0.append(hyb0.IsIn(point2))
        isinhyb1.append(hyb1.IsIn(point2))



    df['impact-x'] = np.array([ i[0] for i in impact])
    df['impact-y'] = np.array([ i[1] for i in impact])
    df['impact-z'] = np.array([ i[2] for i in impact])

    df['impact2-x'] = np.array([ i[0] for i in impact2])
    df['impact2-y'] = np.array([ i[1] for i in impact2])
    df['impact2-z'] = np.array([ i[2] for i in impact2])

    df['isin-hyb0'] = isinhyb0
    df['isin-hyb1'] = isinhyb1
    
    ## overwrite with the new informations
    df.to_csv("cosmics_simulation.csv")

print()



