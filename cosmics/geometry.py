import numpy as np
import pandas as pd
import copy

from scipy.spatial.transform import Rotation

### these are for drawing. Should be load only if necessary
#from mpl_toolkits import mplot3d
#import matplotlib.pyplot as plt

class Base:
    use = 'mpl' # mpl (matplotlib) ogl (opengl)
    def __init__(self):
        pass
    def draw(self):
        raise RuntimeError("Unimplemented")
    def setup(self):
        raise RuntimeError("Unimplmented")

class Strip(Base):
    todraw = True
    only_active = True
    def __init__(self):
        super().__init__()
        self . start = np.zeros(shape=3)
        self . stop = np.zeros(shape=3)

        self . active=False ## keep track to plot

    def draw(self, d):
        if not Strip.todraw: return self
        if Strip.only_active and not self.active: return self

        if Base.use == 'mpl': return self._draw_mpl(d)
        return self

    def _draw_mpl(self,d):
        ''' d must contain: ax'''
        ax = d['ax']
        x = np.array( [self.start,self.stop] )
        lc = 'b' if not self.active else 'r'
        ax.plot3D( x[:,0], x[:,1], x[:,2] ,color=lc)
        return self

    #def _draw_ogl(self,d):
    #    ''' to investigate '''
    #    glBegin(GL_LINES)
    #    glVertex3fv(self.start)
    #    glVertex3fv(self.stop)
    #    glEnd()

    def setup(self):
        pass

class Hybrid (Base):
    todraw = True
    ## derived as max on run
    nz = 16
    nchip = 8
    nstrip =240 

    dz = 24
    dx = 1.6 # TBC, 1.6 2.4 or 4.0 mm
    #dy = 187.5 ## TBC
    dy = 192 ## TBC


    def __init__(self):
        super().__init__()
        self . x = np.zeros(shape=3) ## X,Y,Z posizione of a corner
        self . theta = np.zeros(shape=3) ## solid position. Euler angles
        self . hyb = 0
        self.type = 'PS'  ## maybe we make a base class and two derived classes?
        self.active = False
        self.components={} ## z, chip, strip

    def EndZ(self): ## compute the final point in Z
        R = Rotation.from_euler('xyz',self.theta)
        ## prepare list of vertices
        vtx = np.array([0.,0.,1.])  ## unitary length in Z
        l = np.array([Hybrid.dx,Hybrid.dy,Hybrid.dz])
        vtx = vtx * l 
        vtx = self.x + R.apply(vtx)
        return vtx

    def EndY(self): ## compute the final point in Z
        R = Rotation.from_euler('xyz',self.theta)
        ## prepare list of vertices
        vtx = np.array([0.,1.,0.])  ## unitary length in Z
        l = np.array([Hybrid.dx,Hybrid.dy,Hybrid.dz])
        vtx = vtx * l 
        vtx = self.x + R.apply(vtx)
        return vtx

    def EndX(self): ## compute the final point in Z
        R = Rotation.from_euler('xyz',self.theta)
        ## prepare list of vertices
        vtx = np.array([1.,0.,0.])  ## unitary length in Z
        l = np.array([Hybrid.dx,Hybrid.dy,Hybrid.dz])
        vtx = vtx * l 
        vtx = self.x + R.apply(vtx)
        return vtx

    def IsIn(self, point):
        dpoint = point -self.x ## compute delta wrt start
        R = Rotation.from_euler('xyz',self.theta)
        Q = R.inv()
        l = np.array([Hybrid.dx,Hybrid.dy,Hybrid.dz])
        u = Q.apply(dpoint)/l ## in the unitary frame
        
        if  u[0]<0  or u[0] > 1:  return False
        if  u[1]<0  or u[1] > 1:  return False
        if  u[2]<0  or u[2] > 1:  return False
        return True

    def setup(self):
        self.components = {} ## reset
        R = Rotation.from_euler('xyz',self.theta)
        for z in range(0,Hybrid.nz):
            for chip in range(0,Hybrid.nchip):
                for strip in range(0,Hybrid.nstrip): 
                    a = Strip()
                    xpos = 0
                    iy =  ( chip*Hybrid.nstrip + strip ) ## standard 
                
                    ChipBest = [5, 4, 3, 2, 6, 7, 0, 1]
                    # [5, 4, 3, 2, 1, 0, 7, 6]
                    iy = ChipBest[chip] *Hybrid.nstrip + strip

                    iz = z

                    if self.hyb: 
                        #iz = z
                        #iy = (Hybrid.nstrip*Hybrid.nchip)  - iy ## go back
                        iz = Hybrid.nz -z -1
                        istr = Hybrid.nstrip -strip -1
                        ichi = (chip + Hybrid.nchip/2) % Hybrid.nchip
                        iy=  (ichi*Hybrid.nstrip + istr) ## count back strip, chip rotade
                        #iy=  (chip*Hybrid.nstrip + istr) ## count back strip but not chip
                        #iy = (Hybrid.nstrip*Hybrid.nchip)  - iy ## go back

                        ChipBest = [6,7,0,1,5,4,3,2] ## cycling ChipBest
                        iy = ChipBest[chip] *Hybrid.nstrip + istr


                        ## Revert iy
                        #iy =  ( chip*Hybrid.nstrip + strip )
                    ypos = Hybrid.dy / (Hybrid.nstrip*Hybrid.nchip) * iy

                    zpos_0 = Hybrid.dz / Hybrid.nz *iz
                    zpos_1 = Hybrid.dz / Hybrid.nz *(iz+1)

                    a.start = np.array([xpos,ypos,zpos_0])
                    a.stop  = np.array([xpos,ypos,zpos_1])

                    ## implement rotations. 
                    a.start = R.apply(a.start)
                    a.stop = R.apply(a.stop)

                    ## translate
                    a.start += self.x
                    a.stop += self.x

                    self.components[(z,chip,strip)] = copy.deepcopy(a)
        [c.setup() for c in self.components.values()]
        return self

    def print(self):
        print ("-- HYBRID",self.hyb,"---")
        print ("* x=",self.x)
        print ("* theta=",self.theta)

    def get(self,z,chip,strip):

        ## DEBUG
        #print("DEBUG","Components strip are:",self.components.keys())
        return self.components[(z,chip,strip)]

    def getN(self):
        return len(self.components) ## fast

    def draw(self, d):
        [ c.draw(d) for c in self.components.values()]
        if not Hybrid.todraw: return self
        if Base.use == 'mpl': return self._draw_mpl(d)
        return self
    
    def _draw_mpl(self,d):

        from mpl_toolkits import mplot3d

        R = Rotation.from_euler('xyz',self.theta)
        ## prepare list of vertices
        vtx0 = [ np.array([ix,iy,iz]) for ix in range(0,2) for iy in range(0,2) for iz in range(0,2)] ## unitary cube
        l = np.array([Hybrid.dx,Hybrid.dy,Hybrid.dz])
        vtx = [ a * l  for a in vtx0] ## stretch
        vtx = np.array([ self.x + R.apply(a) for a in vtx ])
    
        faces = []
        for i in range(0,6):
            if i ==0:  sel = [ vtx[i] for i in range(0,len(vtx)) if vtx0[i][0] ==0 ]
            elif i ==1:  sel = [ vtx[i] for i in range(0,len(vtx)) if vtx0[i][0] ==1 ]

            elif i ==2:  sel = [ vtx[i] for i in range(0,len(vtx)) if vtx0[i][1] ==0 ]
            elif i ==3:  sel = [ vtx[i] for i in range(0,len(vtx)) if vtx0[i][1] ==1 ]

            elif i ==4:  sel = [ vtx[i] for i in range(0,len(vtx)) if vtx0[i][2] ==0 ]
            elif i ==5:  sel = [ vtx[i] for i in range(0,len(vtx)) if vtx0[i][2] ==1 ]
            
            assert(len(sel) == 4)

            sel2 = [sel[0], sel[1] , sel[3] , sel[2]] ## this was sorted going to row, I need them in a "circular" fashio

            faces.append(sel2)
        
        # prepare list of faces
        fc = 'lightskyblue' if not self.active else 'lightcoral'
        collection = mplot3d.art3d.Poly3DCollection(faces, linewidths=0.2, alpha=0.2,edgecolors='k', facecolors=fc)

        ax = d['ax']
        ax.add_collection3d(collection)
        return self

    def _draw_ogl(self,d):
        pass

    def _draw_chip(self,chip,d): ## debug
        ''' Only for Hyb 0. Draw a square, not a cube'''
        from mpl_toolkits import mplot3d
        

        iy0 =  chip*Hybrid.nstrip 
        iy1 =  (chip +1)*(Hybrid.nstrip) 

        ypos0 = Hybrid.dy / (Hybrid.nstrip*Hybrid.nchip) * iy0
        ypos1 = Hybrid.dy / (Hybrid.nstrip*Hybrid.nchip) * iy1

        zpos0 = 0.
        zpos1 = Hybrid.dz 

        xpos = Hybrid.dx ## anypoint
    
        ## Rotate and translate
        R = Rotation.from_euler('xyz',self.theta)

        face = [ [xpos,ypos0,zpos0], 
                 [65,ypos0,zpos1],
                 [65,ypos1,zpos1],
                 [xpos,ypos1,zpos0],
                ]

        faces = [[ self.x + R.apply(f) for f in face]]
        print ("Drawing faces",faces)

        fc = 'gold'  if 'fc' not in d else d['fc']
        collection = mplot3d.art3d.Poly3DCollection(faces, linewidths=0.2, alpha=0.2,edgecolors='k', facecolors=fc)
        ax = d['ax']
        ax.add_collection3d(collection)
        return self

class Module (Base):
    todraw=False ## Not impl
    nhybrid= 2
    def __init__(self):
        super().__init__()
        self.x = np.zeros(shape=3)
        self . theta = np.zeros(shape=3) ## solid position. Euler angles
        self.type = 'PS' 
        self.components={} #"hyb->X" 

    def setup(self):
        self.components={}

        for ihyb in range(0,2):
            hyb = Hybrid()
            hyb . hyb = ihyb 
            hyb . theta = self.theta
            hyb . x = self.x 

            if ihyb ==1: 
                #hyb.x += np.array([0.,0.,Hybrid.dz])
                hyb.x = self.components[0].EndZ()


            #hyb.print()

            self.components[ihyb] = copy.deepcopy(hyb)
        
        [c.setup() for c in self.components.values()]

        ## maybe add strips
    def getN():
        return np.sum([c.getN() for c in self.components.values()])

    def draw(self, d):
        [ c.draw(d) for c in self.components.values()]
        if not Module.todraw: return self
        #return self._draw_mpl(d) if Base.use =='mpl' else self._draw_ogl(d)
        print("I shouldn't be here:",Module.draw)
        raise RuntimeError("Not Implemented")
        #self._draw_mpl(d)

    def get(self, hyb, z = None,chip = None, strip=None ):
        if z==None and chip == None and strip == None: return self.components[hyb]

        ## DEBUG
        #print("DEBUG","Hybrids are:",self.components.keys())
        return self.components[hyb] .get(z,chip,strip,)

class Tower(Base):
    def __init__(self,name=''):
        super().__init__()
        self.components={}
        self.name=name

    def setup(self):
        pass

    def draw(self,d):
        [ c.draw(d) for c in self.components.values() ]
    
    def add(self, name,m):
        self.components[name] = m
    def get(self, name):
        return self.components[name]

    def get_name(self):
        return self.name

#### Make a class. 
class Track(Base):
    def __init__(self):
        self.p1 = np.zeros(shape=3)
        self.p2 = np.zeros(shape=3)
    
    def setup(self):
        pass
    def setup(self, s1, s2,e = 0.1):  
        p1 = (s1.start + s1.stop)/2.  ## mid points of a strip
        p2 = (s2.start + s2.stop)/2.

        ## enlarge the track
        self.p1 = p1 + (p1-p2)*e 
        self.p2 = p2 + (p2-p1)*e

    def draw(self,d):
        if Base.use == 'mpl': return self._draw_mpl(d)
        return self

    def _draw_mpl(self,d):
        x = np.array( [self.p1, self.p2] ) ## make a np array
        d['ax'].plot3D( x[:,0], x[:,1], x[:,2] ,color='green')



