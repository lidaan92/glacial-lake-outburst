#!/usr/bin/env python

import numpy
import matplotlib.pyplot as plt

import clawpack.geoclaw.topotools as tt
import clawpack.geoclaw.dtopotools as dt

def transform(x, y, theta=0.0):

    A = numpy.eye(2)
    return numpy.dot(A, numpy.array([x, y]))


def slide_topo(x, y, t):

    x_c = 492500
    slide_speed = 50
    y_start = 3085500
    y_c = y_start + slide_speed * t
    xi_c, zeta_c = transform(x_c, y_c)
    x_start, zeta_start = transform(0.0, y_start)
    sigma = 100.0
    A = 10.0

    # Transform coordinates
    xi, zeta = transform(x, y)

    slide = numpy.zeros(x.shape)

    # front
    slide += A * numpy.exp(-((xi - xi_c)**2 + (zeta - zeta_c)**2) / sigma**2) * (zeta - zeta_c > 0.0)

    # center
    slide += A * numpy.exp(-((xi - xi_c)**2) / sigma**2) * (zeta - zeta_c <= 0.0) * (zeta - zeta_start >= 0.0)

    # back
    slide += A * numpy.exp(-((xi - xi_c)**2 + (zeta - zeta_start)**2) / sigma**2) * (zeta - zeta_start < 0.0)

    return slide

if __name__ == "__main__":

    # Create dtopo
    dtopo_path = "./topo/imja_slide.tt3"
    dtopo = dt.DTopography()
    dtopo.x = numpy.linspace(491000, 494500, 100)
    dtopo.y = numpy.linspace(3085200, 3086800, 100)
    X, Y = numpy.meshgrid(dtopo.x, dtopo.y)
    T = numpy.linspace(0, 25, 6)
    dtopo.Z = numpy.empty((dtopo.x.shape[0], dtopo.y.shape[0], T.shape[0]))
    for (i, t) in enumerate(T):
        dtopo.Z[:, :, i] = slide_topo(X, Y, t)

    for t in T:
        fig = plt.figure()
        axes = fig.add_subplot(1, 1, 1)
        axes.pcolor(dtopo.X, dtopo.Y, dtopo.dZ_at_t(t))
        axes.set_title("t = %s" % str(t))

    # topo.plot(contour_levels=[5000], limits=[4750, 5500])
    plt.show()
