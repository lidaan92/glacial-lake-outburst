#!/usr/bin/env python

import sys
import os
import subprocess
import shutil

import numpy
import matplotlib.pyplot as plt

import clawpack.geoclaw.topotools as tt
import clawpack.geoclaw.dtopotools as dt


locations = {"imja": {"scenarios": {"island_peak": {"start": (86.930245, 27.905104),
                                                    "slide_speed": 25,
                                                    "max_length": 1e3,
                                                    "theta": 4.0 * numpy.pi / 3.0,
                                                    "sigma": 2.5e2,
                                                    "A": 100.0,
                                                    "t_end": 35.0},
                                     "amphulapche": {"start": (86.911737, 27.885901),
                                                     "slide_speed": 50,
                                                     "max_length": 5e3,
                                                     "theta": numpy.pi / 3.0,
                                                     "sigma": 500.0,
                                                     "A": 100.0,
                                                     "t_end": 35.0},
                                     "snow_line": {"start": (86.942428, 27.897892),
                                                   "slide_speed": 50,
                                                   "max_length": 1e3,
                                                   "theta": numpy.pi,
                                                   "sigma": 500,
                                                   "A": 200.0,
                                                   "t_end": 35.0}
                                   },
                     "extent": [86.910814, 86.951576, 27.883193, 27.912485],
                     "topo_path": "./everest.tt3"
                    },
            }


def transform(x, y, theta=0.0):
    return (x * numpy.cos(theta) + y * numpy.sin(theta), 
            x * numpy.sin(theta) - y * numpy.cos(theta))


def slide_topo(x, y, t, start, slide_speed, max_length, theta, sigma_slide, 
               amplitude, estimate_mass=False):

    # Convert input to lat-long coordinates
    deg2meters = 111.32e3
    speed = slide_speed / deg2meters
    L = max_length / deg2meters
    sigma = sigma_slide / deg2meters
    A = amplitude / deg2meters

    # Transform coordinates
    eta, zeta = transform(x, y, theta)
    eta_start, zeta_start = transform(start[0], start[1], theta)

    # Derive lengths in eta-zeta coordinate system
    eta_c = eta_start + speed * t
    zeta_c = zeta_start
    if eta_c - eta_start > L:
        eta_start = eta_c - L
    else:
        eta_end = eta_start

    # Compute dtopo
    slide = numpy.zeros(x.shape)
    estimated_mass = 0.0

    # front
    slide += A * numpy.exp(-((eta - eta_c)**2 + (zeta - zeta_c)**2) / sigma**2) * (eta > eta_c)
    estimated_mass += (A * numpy.pi * numpy.sqrt(sigma) / 4.0) ** 2

    # center
    slide += A * numpy.exp(-((zeta - zeta_c)**2) / sigma**2) * (eta  <= eta_c) * (eta >= eta_start)
    estimated_mass += A * numpy.sqrt(sigma) / 2.0 * numpy.sqrt(2.0 * numpy.pi) * (eta_c - eta_start)

    # back
    slide += A * numpy.exp(-((eta - eta_start)**2 + (zeta - zeta_start)**2) / sigma**2) * (eta < eta_start)
    estimated_mass += (A * numpy.pi * numpy.sqrt(sigma) / 4.0) ** 2

    if estimate_mass:
        estimated_mass *= 2000.0 / (1e3 * 1e6) * deg2meters**3
        print("Estimated Mass = %s Million Tons" % (estimated_mass))

    return slide

1 gm     (0.01 m)^3
  --   * ---------
  cm^3   (0.001 kg)


def create_dtopo(location, scenario_name, N=100, estimate_mass=True, 
                 force=False, plot=False, topo_path=None):

    scenario = locations[location]["scenarios"][scenario_name]
    extent = locations[location]['extent']
    path = os.path.join("..", location, "%s.tt3" % scenario_name)

    if os.path.exists(path):
        if force:
            os.remove(path)
        else:
            print("Slide file already exists.")
            sys.exit(0)

    # Create dtopo
    dtopo = dt.DTopography()
    dtopo.x = numpy.linspace(extent[0], extent[1], N)
    dtopo.y = numpy.linspace(extent[2], extent[3], N)
    dtopo.X, dtopo.Y = numpy.meshgrid(dtopo.x, dtopo.y)
    dtopo.times = numpy.linspace(0, scenario['t_end'], 8)
    dtopo.dZ = numpy.empty((dtopo.times.shape[0], dtopo.x.shape[0], 
                                                  dtopo.y.shape[0]))

    for (i, t) in enumerate(dtopo.times):
        dtopo.dZ[i, :, :] = slide_topo(dtopo.X, dtopo.Y, t, 
                                       scenario["start"],
                                       scenario["slide_speed"],
                                       scenario["max_length"],
                                       scenario["theta"],
                                       scenario["sigma"],
                                       scenario["A"],
                                       estimate_mass=estimate_mass)

    dtopo.write(path=path)

    if plot:
      # Load topo for comparison
      topo = tt.Topography(path=locations[location]["topo_path"], topo_type=3)

      if not os.path.exists("./%s" % scenario_name):
          os.mkdir(scenario_name)

      for i in range(dtopo.times.shape[0] - 1, -1, -1):
          fig = plt.figure()
          axes = fig.add_subplot(1, 1, 1)
          extent = [numpy.min(dtopo.x), numpy.max(dtopo.x),
                    numpy.min(dtopo.y), numpy.max(dtopo.y)]
          axes.pcolor(dtopo.x, dtopo.y, dtopo.dZ_at_t(dtopo.times[i]))
          axes.contour(topo.x, topo.y, topo.Z, levels=[5000], colors='w')
          axes.set_xlim(extent[:2])
          axes.set_ylim(extent[2:])

          axes.set_title("t = %s" % str(dtopo.times[i]))
          fig.savefig('./%s/slide_%s.png' % (scenario_name, i))

      # make a movie
      cmd = r"ffmpeg -r 2 -i %s" % scenario_name + r"/slide_%1d.png " + \
            r"-q:a 0 -q:v 0 -vcodec mpeg4 -vb 20M -r 24 %s/%s.mp4" % (scenario_name, 
                                                                      scenario_name)
      subprocess.call(cmd, shell=True)


if __name__ == "__main__":

    location = sys.argv[1]
    force = False
    plot = False

    if len(sys.argv) == 2:
        scenarios = locations[location]['scenarios'].keys()
    elif len(sys.argv) >= 3:
        scenario = sys.argv[2]
        scenarios = [scenario]

        if len(sys.argv) >= 4:
            force = bool(sys.argv[3])
            if len(sys.argv) >= 5:
                plot = bool(sys.argv[4])

    else:
        raise InputError("Need the location and scenario to proceed.")

    for scenario in scenarios:
        create_dtopo(location, scenario, force=force, plot=plot)