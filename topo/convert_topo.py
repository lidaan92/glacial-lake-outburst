#!/usr/bin/env python

import sys
import os

import numpy
import matplotlib.pyplot as plt

import clawpack.geoclaw.topotools as topotools
import clawpack.visclaw.colormaps as colormaps

land_cmap = colormaps.make_colormap({ 0.0:[0.1,0.4,0.0],
                                         0.25:[0.0,1.0,0.0],
                                          0.5:[0.8,1.0,0.5],
                                          1.0:[0.8,0.5,0.2]})


locations = {'imja': [{'path': 'ASTGTM2_everest_mosaic.tif',
                       'out_path': 'everest.tt3',
                       'strip_zeros': True,
                       'contours': (4730, 4740, 5000),
                       'limits': (4700, 4800)}],
             'barun': [{'path': 'ASTGTM2_everest_mosaic.tif',
                        'out_path': 'everest.tt3',
                        'strip_zeros': False,
                        'contours': (4730, 4740, 5000),
                        'limits': (4700, 4800)}
                      ],
             'thulagi': [{'path': "ASTGTM2_Thulagi_mosaic.tif",
                          'out_path': 'thulagi.tt3',
                          'strip_zeros': False,
                          'contours': (4730, 4740, 5000),
                          'limits': (4700, 4800)}]

             }

def convert_topo(location, plot=False):
    """Convert geotiff to topotype 3"""
    
    for loc_dict in locations[location]:
        topo = None
        if not os.path.exists(loc_dict['out_path']):

            topo = topotools.Topography(path=loc_dict['path'], topo_type=5)
            topo.read()

            if loc_dict['strip_zeros']:
                # Remove 0 values around perimiter
                topo.Z = numpy.flipud(topo.Z[:-1, :-1])
            
            topo.write(loc_dict['out_path'], topo_type=3)


        if plot:
            if topo is None:
                topo = topotools.Topography(path=loc_dict['out_path'])
            
            fig = plt.figure()
            axes = fig.add_subplot(1, 1, 1)

            topo.plot(axes=axes, contour_levels=loc_dict['contours'], 
                                 limits=loc_dict['limits'],
                                  cmap=land_cmap)
    if plot:
        plt.show()


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


if __name__ == '__main__':
    
    # Command line parsing
    if len(sys.argv) == 1:
        print("Available locations:")
        for location in locations.keys():
            print("  %s" % location)
        sys.exit(0)
    
    elif len(sys.argv) == 2:
        location = sys.argv[1].lower()

    else:
        raise InputError("Expected a location.")

    convert_topo(location, plot=True)
