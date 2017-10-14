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
