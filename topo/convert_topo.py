#!/usr/bin/env python

import clawpack.geoclaw.topotools as topotools

topo_path = './MERGE-IMJA-LAKE-BATHY-ASTDEM2-29m-16bit.tif'
out_path = "./imja.tt3"
topo = topotools.Topography(path=topo_path, topo_type=5)
topo.read()
# Remove 0 values around perimiter
topo.Z = topo.Z[:-1, :-1]
topo.write(out_path, topo_type=3)
print("Extent = (%s, %s) x (%s, %s)" % (topo.x[0], topo.y[0], topo.x[-1], topo.y[-1]))

# Plot topography with lake topo region