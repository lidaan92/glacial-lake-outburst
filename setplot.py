
""" 
Set up the plot figures, axes, and items to be done for each frame.

This module is imported by the plotting routines and then the
function setplot is called to set the plot parameters.
    
""" 

from __future__ import absolute_import
from __future__ import print_function
from six.moves import range

import numpy
import matplotlib.pyplot as plt
import matplotlib.colors as colors


import clawpack.visclaw.colormaps as colormaps
from clawpack.geoclaw import topotools
import clawpack.geoclaw.geoplot as geoplot


surface_cmap = colormaps.make_colormap({1.0: 'r', 0.5: 'w', 0.0: 'b'})
speed_cmap = plt.get_cmap('PuBu')
friction_cmap = plt.get_cmap('YlOrRd')
wind_cmap = plt.get_cmap('PuBu')
pressure_cmap = plt.get_cmap('PuBu')
land_cmap = geoplot.land_colors

def eta(q, DRY_TOL=1e-3):
    h = q[0, :, :]
    eta = q[3, :, :] - 5000.0
    index = numpy.nonzero((numpy.abs(h) < DRY_TOL) + (h == numpy.nan))
    eta[index[0], index[1]] = numpy.nan
    return eta

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


    # To plot gauge locations on pcolor or contour plot, use this as
    # an afteraxis function:

    def addgauges(current_data):
        from clawpack.visclaw import gaugetools
        gaugetools.plot_gauge_locations(current_data.plotdata, \
             gaugenos='all', format_string='ko', add_labels=True)
    

    #-----------------------------------------
    # Figure for surface
    #-----------------------------------------
    
    extents = {"Full Domain": [486800, 498600, 3082100, 3090500],
               "Zoom": (491010, 493710, 3086250, 3087250)}

    for (name, extent) in extents.items():
        plotfigure = plotdata.new_plotfigure(name='Surface %s' % name)

        # Set up for axes in this figure:
        plotaxes = plotfigure.new_plotaxes('pcolor')
        plotaxes.title = 'Surface'
        plotaxes.scaled = True

        # Water
        plotitem = plotaxes.new_plotitem(plot_type='2d_pcolor')
        #plotitem.plot_var = geoplot.surface
        plotitem.plot_var = lambda cd: eta(cd.q)
        plotitem.pcolor_cmap = surface_cmap
        plotitem.pcolor_cmin = -1.0
        plotitem.pcolor_cmax = 1.0
        plotitem.add_colorbar = True
        plotitem.amr_celledges_show = [0,0,0]
        plotitem.patchedges_show = 1

        # Bathy contour
        plotitem = plotaxes.new_plotitem(plot_type='2d_contour')
        plotitem.show = False
        plotitem.plot_var = geoplot.topo
        plotitem.contour_levels = [5000]
        plotitem.amr_contour_colors = ['r']  # color on each level
        plotitem.kwargs = {'linestyles':'solid','linewidths':2}
        plotitem.amr_contour_show = [1,1,1]  
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
        plotitem.patchedges_show = 1
        plotaxes.xlimits = extent[:2]
        plotaxes.ylimits = extent[2:]

    #-----------------------------------------
    # Figures for gauges
    #-----------------------------------------
    # plotfigure = plotdata.new_plotfigure(name='Surface at gauges', figno=300, \
    #                 type='each_gauge')
    # plotfigure.clf_each_gauge = True

    # # Set up for axes in this figure:
    # plotaxes = plotfigure.new_plotaxes()
    # plotaxes.xlimits = 'auto'
    # plotaxes.ylimits = 'auto'
    # plotaxes.title = 'Surface'

    # # Plot surface as blue curve:
    # plotitem = plotaxes.new_plotitem(plot_type='1d_plot')
    # plotitem.plot_var = 3
    # plotitem.plotstyle = 'b-'

    # # Plot topo as green curve:
    # plotitem = plotaxes.new_plotitem(plot_type='1d_plot')
    # plotitem.show = False

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

    #     if gaugeno == 32412:
    #         try:
    #             plot(TG32412[:,0], TG32412[:,1], 'r')
    #             legend(['GeoClaw','Obs'],loc='lower right')
    #         except: pass
    #         axis((0,t.max(),-0.3,0.3))

    #     plot(t, 0*t, 'k')
    #     n = int(floor(t.max()/3600.) + 2)
    #     xticks([3600*i for i in range(n)], ['%i' % i for i in range(n)])
    #     xlabel('time (hours)')

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
