import numpy as np
import pandas as pd
import copy

from scipy.spatial.transform import Rotation


from argparse import ArgumentParser
parser = ArgumentParser()
parser.add_argument("-m","--matplotlib",action='store_true',default=True, help="Use Matplotlib")
#parser.add_argument("-g","--opengl",action='store_false',dest='matplotlib',help="Use Opengl")
args = parser.parse_args()


## Note: Global units are in mm
##

## All classess must have:
## draw, setup, init,

from geometry import *

import time
if __name__ == "__main__": ## TEST

    ### SETUP GEOMETRY
    from tower import *

    ####iread link hyb hex(whole) nstubs bx chip_id strip bend Z
    #168 0 0 0x4b5e5e37 1 727 4 188 3 7
    #168 1 0 0x4b6239cb 1 728 4 115 4 11
    # hyb, z, chip ,strip

    m0.get(0).active=True
    m1.get(0).active=True
    

    if args.matplotlib:    
        from mpl_toolkits import mplot3d
        import matplotlib.pyplot as plt

        fig = plt.figure()
        ax = fig.add_subplot(1,1,1, projection='3d')
        #ax.view_init(-20, -20, 60)
        #ax.view_init(elev=30, azim=45, roll=15)
        ax.view_init(elev=100, azim=180, roll=0)

        #dz = 240
        #dx = 10 # TBC
        #dy = 187.5 ## TBC

        ax.set_xlim(0, Hybrid.dx + 10 + 60); 
        ax.set_ylim(0, Hybrid.dy + 10); 
        ax.set_zlim(0, Hybrid.dz*2 + 10);

        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_zlabel("z")
        
        d = {'ax':ax,'plt':plt,'fig':fig}
        #m0.draw(d)
        #m1.draw(d)
        if False:  #only one
            m0.get(0,7,4,188).active = True
            m1.get(0,11,4,115).active = True
            trk = Track()
            trk.setup(m0.get(0,7,4,188),m1.get(0,11,4,115))
            trk.draw(d)
        #draw_track(m0.get(0,7,4,188),m1.get(0,11,4,115),ax)
        tower.draw(d)

        if True:
            run2 = pd.read_csv("processed/run2.csv") ## 340 min
            tracks = [] 
            for i in range(0, len(run2)):
                t = Track()
                if run2.iloc[i]["hyb2"] != 1: continue
                    ## hyb, z, chip ,strip
                t.setup(m0.get(
                    run2.iloc[i]["hyb1"],run2.iloc[i]["z1"], run2.iloc[i]['chip1'],run2.iloc[i]['strip1']
                ),m1.get(
                    run2.iloc[i]["hyb2"],run2.iloc[i]["z2"], run2.iloc[i]['chip2'],run2.iloc[i]['strip2']
                ))

                m0.get(
                    run2.iloc[i]["hyb1"],run2.iloc[i]["z1"], run2.iloc[i]['chip1'],run2.iloc[i]['strip1']
                ).active = True
                m1.get(
                    run2.iloc[i]["hyb2"],run2.iloc[i]["z2"], run2.iloc[i]['chip2'],run2.iloc[i]['strip2']
                ).active = True

                tracks.append(t)

            tower.draw(d)
            [    t.draw(d) for t in tracks]

        plt.show()

