
""" 
Set up the plot figures, axes, and items to be done for each frame.

This module is imported by the plotting routines and then the
function setplot is called to set the plot parameters.
    
""" 

from __future__ import absolute_import
from __future__ import print_function
from six.moves import range

import os

import numpy
import matplotlib.pyplot as plt
import matplotlib.colors as colors


import clawpack.visclaw.colormaps as colormaps
import clawpack.clawutil.data as data
from clawpack.geoclaw import topotools
import clawpack.geoclaw.geoplot as geoplot


surface_cmap = colormaps.make_colormap({1.0: 'r', 0.5: 'w', 0.0: 'b'})
speed_cmap = plt.get_cmap('PuBu')
friction_cmap = plt.get_cmap('YlOrRd')
wind_cmap = plt.get_cmap('PuBu')
pressure_cmap = plt.get_cmap('PuBu')
land_cmap = geoplot.land_colors

# Contruct lake mask for plotting
init_region = [86.910814, 86.951576, 27.883193, 27.912485]
cutouts = []

def lake_mask(x, y):
    region = numpy.where((init_region[0] <= x) * 
                         (x <= init_region[1]) *
                         (init_region[2] <= y) * 
                         (y <= init_region[3]), True, False)
    for cutout in cutouts:
        region = numpy.where((cutout[0] < x) * (x < cutout[2]) *
                             (cutout[1] < y) * (y < cutout[3]), 
                             False, region)

    return region


def surface_or_depth(cd, DRY_TOL=1e-3):
    h = cd.q[0, :, :]
    eta = cd.q[3, :, :]
    b = cd.q[3, :, :] - cd.q[0, :, :] 

    surface = numpy.ma.masked_where(h <= DRY_TOL, eta - 5000.0)
    depth = numpy.ma.masked_where(h <= DRY_TOL, h)
    return numpy.where(lake_mask(cd.x, cd.y) * (b < 5000), surface, depth)


#--------------------------
def setplot(plotdata=None):
#--------------------------
    
    """ 
    Specify what is to be plotted at each frame.
    Input:  plotdata, an instance of pyclaw.plotters.data.ClawPlotData.
    Output: a modified version of plotdata.
    
    """ 


    from clawpack.visclaw import colormaps, geoplot
    from numpy import linspace

    if plotdata is None:
        from clawpack.visclaw.data import ClawPlotData
        plotdata = ClawPlotData()

    plotdata.clearfigures()  # clear any old figures,axes,items data

    # Import data objects
    clawdata = data.ClawInputData(2)
    clawdata.read(os.path.join(plotdata.outdir, 'claw.data'))


    # To plot gauge locations on pcolor or contour plot, use this as
    # an afteraxis function:

    def addgauges(current_data):
        from clawpack.visclaw import gaugetools
        gaugetools.plot_gauge_locations(current_data.plotdata, \
             gaugenos='all', format_string='ko', add_labels=True)
    

    #-----------------------------------------
    # Figure for surface
    #-----------------------------------------
    extents = {"Full Domain": {'extent': [clawdata.lower[0], clawdata.upper[0], 
                                          clawdata.lower[1], clawdata.upper[1]],
                               'show_contours': False,
                               'show_patches': [1, 1, 1, 1],
                               'figsize': (6.4, 4.8)},
               "Zoom 1": {'extent': init_region,
                          'show_contours': True,
                          'show_patches': 0,
                          'figsize': (6.4 * 2.0, 4.8)}}

    for (name, param_dict) in extents.items():
        plotfigure = plotdata.new_plotfigure(name='Surface %s' % name)
        plotfigure.kwargs['figsize'] = param_dict['figsize']

        # Set up for axes in this figure:
        plotaxes = plotfigure.new_plotaxes('pcolor')
        plotaxes.title = 'Surface'
        plotaxes.scaled = True

        # Water
        plotitem = plotaxes.new_plotitem(plot_type='2d_pcolor')
        # plotitem.plot_var = geoplot.surface
        plotitem.plot_var = surface_or_depth
        # plotitem.plot_var = 0
        plotitem.pcolor_cmap = surface_cmap
        plotitem.pcolor_cmin = -10.0
        plotitem.pcolor_cmax = 10.0
        plotitem.add_colorbar = True
        plotitem.amr_celledges_show = [0, 0, 0, 0]
        plotitem.patchedges_show = param_dict['show_patches']

        # Bathy contour
        plotitem = plotaxes.new_plotitem(plot_type='2d_contour')
        plotitem.show = param_dict['show_contours']
        plotitem.plot_var = geoplot.topo
        plotitem.contour_levels = numpy.arange(5000, 6000, 25)
        plotitem.amr_contour_colors = ['k']  # color on each level
        plotitem.kwargs = {'linestyles':'solid','linewidths':1}
        plotitem.amr_contour_show = [0, 0, 0, 1]  
        plotitem.celledges_show = 0
        plotitem.patchedges_show = 0

        plotitem = plotaxes.new_plotitem(plot_type='2d_contour')
        plotitem.show = param_dict['show_contours']
        plotitem.plot_var = geoplot.topo
        plotitem.contour_levels = numpy.arange(4000, 5000, 25)
        plotitem.amr_contour_colors = ['k']  # color on each level
        plotitem.kwargs = {'linestyles':'dashed','linewidths':1}
        plotitem.amr_contour_show = [0, 0, 0, 1]  
        plotitem.celledges_show = 0
        plotitem.patchedges_show = 0

        # Land
        plotitem = plotaxes.new_plotitem(plot_type='2d_pcolor')
        plotitem.plot_var = geoplot.land
        plotitem.pcolor_cmap = geoplot.land_colors
        plotitem.pcolor_cmin = 4800
        plotitem.pcolor_cmax = 5005
        plotitem.add_colorbar = False
        plotitem.amr_celledges_show = [0,0,0]
        plotitem.patchedges_show = param_dict['show_patches']
        plotaxes.xlimits = param_dict['extent'][:2]
        plotaxes.ylimits = param_dict['extent'][2:]

        def draw_rect(rect, axes, style="r--"):
            """rect = [xlower, ylower, xupper, yupper"""
            xlower = rect[0]
            xupper = rect[1]
            ylower = rect[2]
            yupper = rect[3]
            axes.plot([xlower, xupper], [ylower, ylower], style)
            axes.plot([xupper, xupper], [ylower, yupper], style)
            axes.plot([xupper, xlower], [yupper, yupper], style)
            axes.plot([xlower, xlower], [yupper, ylower], style)

        def afteraxes(cd):
            addgauges(cd)
            draw_rect([491000, 493700, 3085250, 3086250], plt.gca())

        plotaxes.afteraxes = afteraxes

    # -----------------------------------------
    # Figures for gauges
    # -----------------------------------------
    plotfigure = plotdata.new_plotfigure(name='Surface at gauges', figno=300, \
                    type='each_gauge')
    plotfigure.clf_each_gauge = True

    # Set up for axes in this figure:
    plotaxes = plotfigure.new_plotaxes()
    plotaxes.xlimits = 'auto'
    plotaxes.ylimits = 'auto'
    plotaxes.title = 'Surface'

    # Plot surface as blue curve:
    plotitem = plotaxes.new_plotitem(plot_type='1d_plot')
    plotitem.plot_var = 3
    plotitem.plotstyle = 'b-'

    # Plot topo as green curve:
    plotitem = plotaxes.new_plotitem(plot_type='1d_plot')
    plotitem.show = False

    # def gaugetopo(current_data):
    #     q = current_data.q
    #     h = q[0,:]
    #     eta = q[3,:]
    #     topo = eta - h
    #     return topo
        
    # plotitem.plot_var = gaugetopo
    # plotitem.plotstyle = 'g-'

    # def add_zeroline(current_data):
    #     from pylab import plot, legend, xticks, floor, axis, xlabel
    #     t = current_data.t 
    #     gaugeno = current_data.gaugeno

        # if gaugeno == 32412:
        #     try:
        #         plot(TG32412[:,0], TG32412[:,1], 'r')
        #         legend(['GeoClaw','Obs'],loc='lower right')
        #     except: pass
        #     axis((0,t.max(),-0.3,0.3))

        # plot(t, 0*t, 'k')
        # n = int(floor(t.max()/3600.) + 2)
        # xticks([3600*i for i in range(n)], ['%i' % i for i in range(n)])
        # xlabel('time (hours)')

    # plotaxes.afteraxes = add_zeroline



    #-----------------------------------------
    
    # Parameters used only when creating html and/or latex hardcopy
    # e.g., via pyclaw.plotters.frametools.printframes:

    plotdata.printfigs = True                # print figures
    plotdata.print_format = 'png'            # file format
    plotdata.print_framenos = 'all'          # list of frames to print
    plotdata.print_gaugenos = 'all'          # list of gauges to print
    plotdata.print_fignos = 'all'            # list of figures to print
    plotdata.html = True                     # create html files of plots?
    plotdata.html_homelink = '../README.html'   # pointer for top of index
    plotdata.latex = True                    # create latex file of plots?
    plotdata.latex_figsperline = 2           # layout of plots
    plotdata.latex_framesperline = 1         # layout of plots
    plotdata.latex_makepdf = False           # also run pdflatex?
    plotdata.parallel = True                 # make multiple frame png's at once

    return plotdata
