#!/usr/bin/env python

import numpy
import matplotlib.pyplot as plt

import clawpack.geoclaw.topotools as tt
import clawpack.geoclaw.dtopotools as dt

def transform(x, y, theta=0.0):
    return (x * numpy.cos(theta) + y * numpy.sin(theta), 
            x * numpy.sin(theta) - y * numpy.cos(theta))

def slide_topo(x, y, t):

    x_start, y_start = 492500, 3085500
    slide_speed = 50
    slide_max_length = 1000.0
    theta = numpy.pi / 3.0
    sigma = 100.0
    A = 10.0

    # Transform coordinates
    eta, zeta = transform(x, y, theta)
    eta_start, zeta_start = transform(x_start, y_start, theta)

    # Derive lengths in eta-zeta coordinate system
    eta_c = eta_start + slide_speed * t
    zeta_c = zeta_start
    if eta_c - eta_start > slide_max_length:
        eta_start = eta_c - slide_max_length
    else:
        eta_end = eta_start

    # Compute dtopo
    slide = numpy.zeros(x.shape)

    # front
    slide += A * numpy.exp(-((eta - eta_c)**2 + (zeta - zeta_c)**2) / sigma**2) * (eta > eta_c)

    # center
    slide += A * numpy.exp(-((zeta - zeta_c)**2) / sigma**2) * (eta  <= eta_c) * (eta >= eta_start)

    # back
    slide += A * numpy.exp(-((eta - eta_start)**2 + (zeta - zeta_start)**2) / sigma**2) * (eta < eta_start)

    return slide

if __name__ == "__main__":
    # Create dtopo
    dtopo_path = "./topo/imja_slide.tt3"
    dtopo = dt.DTopography()
    dtopo.x = numpy.linspace(491000, 494500, 100)
    dtopo.y = numpy.linspace(3085200, 3086800, 100)
    dtopo.X, dtopo.Y = numpy.meshgrid(dtopo.x, dtopo.y)
    dtopo.times = numpy.linspace(0, 35, 8)
    dtopo.dZ = numpy.empty((dtopo.times.shape[0], dtopo.x.shape[0], 
                                                  dtopo.y.shape[0]))
    for (i, t) in enumerate(dtopo.times):
        dtopo.dZ[i, :, :] = slide_topo(dtopo.X, dtopo.Y, t)

    for i in range(dtopo.times.shape[0] - 1, -1, -1):
        fig = plt.figure()
        axes = fig.add_subplot(1, 1, 1)
        axes.pcolor(dtopo.x, dtopo.y, dtopo.dZ_at_t(dtopo.times[i]))
        # axes.pcolor(X, Y, slide_topo(X, Y, T[i]))
        axes.set_title("t = %s" % str(dtopo.times[i]))

    # topo.plot(contour_levels=[5000], limits=[4750, 5500])
    plt.show()
