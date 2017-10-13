#!/usr/bin/env python

import numpy
import matplotlib.pyplot as plt

import clawpack.geoclaw.topotools as topotools


def convert_topo(path, out_path):
    topo = topotools.Topography(path=topo_path, topo_type=5)
    topo.read()
    # Remove 0 values around perimiter
    topo.Z = numpy.flipud(topo.Z[:-1, :-1])
    topo.write(out_path, topo_type=3)


def draw_rect(rect, axes, style="k--"):
    """rect = [xlower, ylower, xupper, yupper"""
    xlower = rect[0]
    xupper = rect[2]
    ylower = rect[1]
    yupper = rect[3]
    axes.plot([xlower, xupper], [ylower, ylower], style)
    axes.plot([xupper, xupper], [ylower, yupper], style)
    axes.plot([xupper, xlower], [yupper, yupper], style)
    axes.plot([xlower, xlower], [yupper, ylower], style)


def plot_topo(path, axes=None):

    topo = topotools.Topography(path=path, topo_type=3)

    if axes is None:
        fig = plt.figure()
        axes = fig.add_subplot(1, 1, 1)
    topo.plot(axes=axes, contour_levels=[5000], limits=(4853, 5000))

    include_boxes = [[491100.0, 3085150.0, 493800.0, 3086400.0]]

    offset_x = [0.0, 0.0]
    offset_y = [0.0, 0.0]

    exclude_boxes = [[491000.0 - offset_x[0], 3086950.0 - offset_y[0], 
                      491900.0 - offset_x[0], 3087250.0 - offset_y[1]],
                     [490750.0 - offset_x[1], 3086800.0 - offset_y[1], 
                      491400.0 - offset_x[1], 3087250.0 - offset_y[1]]]

    for rect in include_boxes:
        draw_rect(rect, axes, style='b--')
    for rect in exclude_boxes:
        draw_rect(rect, axes, style='r--')


if __name__ == '__main__':
    topo_path = './MERGE-IMJA-LAKE-BATHY-ASTDEM2-29m-16bit.tif'
    out_path = "./imja.tt3"

    convert_topo(topo_path, out_path)
    plot_topo(out_path)

    plt.show()

# print("Extent = (%s, %s) x (%s, %s)" % (topo.x[0], topo.y[0], topo.x[-1], topo.y[-1]))

# Plot topography with lake topo region
# fig = plt.figure()

# lake_topo = topotools.Topography(path="./IMJA-LAKE-BATHY-MASL-29m-16bit.tif", 
#                             topo_type=5)
# lake_topo.no_data_value = 65535
# lake_topo.read(mask=True)

# print("Extent = (%s, %s) x (%s, %s)" % (lake_topo.x[0], lake_topo.y[0], lake_topo.x[-1], lake_topo.y[-1]))
# print("Limits = (%s, %s)" % (numpy.min(lake_topo.Z), numpy.max(lake_topo.Z)))

# axes = fig.add_subplot(1, 2, 1)
# lake_topo.plot(axes=axes, limits=(4853, 5000))

# topo = topotools.Topography(path=topo_path, topo_type=5)

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
# plt.show()
