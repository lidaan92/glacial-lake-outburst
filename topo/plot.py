#!/usr/bin/env python

import numpy
import matplotlib.pyplot as plt

import clawpack.geoclaw.topotools as topotools

fig = plt.figure()

lake_topo = topotools.Topography(path="./IMJA-LAKE-BATHY-MASL-29m-16bit.tif", 
                            topo_type=5)
lake_topo.no_data_value = 65535
lake_topo.read(mask=True)

print("Extent = (%s, %s) x (%s, %s)" % (lake_topo.x[0], lake_topo.y[0], lake_topo.x[-1], lake_topo.y[-1]))
print("Limits = (%s, %s)" % (numpy.min(lake_topo.Z), numpy.max(lake_topo.Z)))

# axes = fig.add_subplot(1, 2, 1)
axes = fig.add_subplot(1, 1, 1)
# lake_topo.plot(axes=axes, limits=(4853, 5000))

import clawpack.visclaw.colormaps as colormaps
land_cmap = colormaps.make_colormap({ 0.0:[0.1,0.4,0.0],
                                     0.25:[0.0,1.0,0.0],
                                      0.5:[0.8,1.0,0.5],
                                      1.0:[0.8,0.5,0.2]})
lake_topo.plot(axes=axes, limits=(4500, 5000), cmap=land_cmap)

# topo = topotools.Topography(path='./MERGE-IMJA-LAKE-BATHY-ASTDEM2-29m-16bit.tif', 
#                             topo_type=5)
# Remove 0 values around perimiter
# topo.Z = topo.Z[:-1, :-1]

# topo.extent = lake_topo.extent
# print("Extent = (%s, %s) x (%s, %s)" % (topo.x[0], topo.y[0], topo.x[-1], topo.y[-1]))
# print("Limits = (%s, %s)" % (numpy.min(topo.Z), numpy.max(topo.Z)))

# # Plot topography with lake topo region
# axes = fig.add_subplot(1, 2, 2)
# topo.plot(axes=axes, contour_levels=[5000], limits=(4853, 5000))

# include_box = (491271, lake_topo.extent[1], lake_topo.extent[2], lake_topo.extent[3])
# cutout_box = (491200, 491800, 3085550, 3085700)

# print(include_box)
# print(cutout_box)
plt.show()
