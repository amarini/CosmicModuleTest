import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math

import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d.axes3d as axes3d

simulation = pd.read_csv("cosmics_simulation.csv")

nw = 0.5
cut = math.cos(math.atan( nw*0.1/2.6 )) ## +/-3 strip
print("Cut", (simulation['cost'] > cut).sum() / len(simulation) )
cut2 = math.sin(math.atan( nw*0.1/2.6 ))
simulation['bend-proj'] = simulation['phi'].apply(math.cos).apply(abs) * simulation['cost'].apply(math.acos).apply(math.sin)


simulation['bend-proj2'] =  (simulation['phi'].apply(math.cos) * simulation['cost'].apply(math.acos).apply(math.sin) / simulation['cost'] ) .apply(math.atan)

simulation['isin-l0h0'] = True ## by generation
sel = simulation['isin-l0h0'] & (simulation["bend-proj"] <cut2)
#sel = simulation['isin-l0h0'] & (simulation['cost'] > cut)
#sel = simulation['isin-l0h0']
sel = simulation['isin-l0h0'] & (simulation["bend-proj2"].apply(abs) <cut2)

theta = simulation[sel]['cost'].apply(math.acos).to_numpy()
phi = simulation [sel]['phi'].to_numpy()

############
R=1
X = R * np.sin(theta) * np.cos(phi)
Y = R * np.sin(theta) * np.sin(phi)
Z = R * np.cos(theta)
##############

fig = plt.figure()
ax = fig.add_subplot(1,1,1, projection='3d')
for i in range(0,len(theta)):
    XX = [0.,X[i]]
    YY = [0.,Y[i]]
    ZZ = [0, Z[i]]
    ax.plot3D(
        XX, YY, ZZ,linewidth=0.2, color='blue')

plt.show()
