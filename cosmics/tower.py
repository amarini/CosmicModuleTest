import sys,os

sys.path.insert(0,os.getcwd()+"/cosmics")
sys.path.insert(0,os.getcwd())

from geometry import *

m0 = Module()
m0.setup()

m1 = Module()
m1.x = np.array([65.,0.,0.])
#m1.x += np.array([0,0,0.851351])
#m1.x += np.array([0.,5.03,-5.1]) ## alignment
#m1.x += np.array([0.,2.365885,-2.926829])


m1.setup()

tower = Tower()
tower.add("m0",m0)
tower.add("m1",m1)
