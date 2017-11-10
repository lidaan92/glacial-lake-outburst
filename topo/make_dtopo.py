#!/usr/bin/env python

import sys
import os
import subprocess

import numpy
import matplotlib.pyplot as plt

import clawpack.geoclaw.topotools as tt
import clawpack.geoclaw.dtopotools as dt

# Slide specifications
scenarios = {'imja': {"scenarios":{"island_peak": {
                                   "start": (492050, 3086800),
                                   "slide_speed": 25,
                                   "max_length": 1e3,
                                   "theta": 4.0 * numpy.pi / 3.0,
                                   "sigma": 2.5e2,
                                   "A": 100.0,
                                   "t_end": 35.0},
                               "amphulapche": {
                                   "start": (491300, 3085200),
                                   "slide_speed": 50,
                                   "max_length": 5e3,
                                   "theta": numpy.pi / 3.0,
                                   "sigma": 500.0,
                                   "A": 100.0,
                                   "t_end": 35.0},
                               "snow_line": {
                                  "start": (494000, 3085800),
                                  "slide_speed": 50,
                                  "max_length": 1e3,
                                  "theta": numpy.pi,
                                  "sigma": 500,
                                  "A": 200.0,
                                  "t_end": 35.0}},
                  "extent": (491000, 494500, 3085200, 3086800),
                  "topo_path": "./imja.tt3"
                 },
         'barun': {"scenarios": {},
                   "slide_path": 'barun_slide.tt3'},
         'thulagi': {"scenarios": {},
                     "slide_path": 'thulagi_slide.tt3'}
        }

def transform(x, y, theta=0.0):
    return (x * numpy.cos(theta) + y * numpy.sin(theta), 
            x * numpy.sin(theta) - y * numpy.cos(theta))

def slide_topo(x, y, t, start, slide_speed, max_length, theta, sigma, A, 
               estimate_mass=False):

    # Transform coordinates
    eta, zeta = transform(x, y, theta)
    eta_start, zeta_start = transform(start[0], start[1], theta)

    # Derive lengths in eta-zeta coordinate system
    eta_c = eta_start + slide_speed * t
    zeta_c = zeta_start
    if eta_c - eta_start > max_length:
        eta_start = eta_c - max_length
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
        estimated_mass *= 2000.0 / 1e6
        print("Estimated Mass = %s Million Tons" % (estimated_mass))

    return slide


def create_dtopo(location, scenario_name, N=100, estimate_mass=True, 
                                          force=False, plot=False):

    scenario = location['scenarios'][scenario_name]

    dtopo_path = "%s_dtopo.tt3" % scenario_name
    if not os.path.exists(dtopo_path):
        if force:
            shutil.rmtree(dtopo_path)
        else:
            print("Slide file already exists.")
            sys.exit(0)



    # Create dtopo
    dtopo = dt.DTopography()
    dtopo.x = numpy.linspace(location['extent'][0], location['extent'][1], N)
    dtopo.y = numpy.linspace(location['extent'][2], location['extent'][3], N)
    dtopo.X, dtopo.Y = numpy.meshgrid(dtopo.x, dtopo.y)
    dtopo.times = numpy.linspace(0, scenario['t_end'], 8)
    dtopo.dZ = numpy.empty((dtopo.times.shape[0], dtopo.x.shape[0], 
                                                  dtopo.y.shape[0]))

    for (i, t) in enumerate(dtopo.times):
        dtopo.dZ[i, :, :] = slide_topo(dtopo.X, dtopo.Y, t, 
                                       start=scenario['start'],
                                       slide_speed=scenario['slide_speed'],
                                       max_length=scenario['max_length'],
                                       theta=scenario['theta'],
                                       sigma=scenario['sigma'],
                                       A=scenario['A'],
                                       estimate_mass=estimate_mass)
    dtopo.write(path=dtopo_path)


    if plot:
      # Load topo for comparison
      topo = tt.Topography(path=location['topo_path'], topo_type=3)

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

    # Command line parsing
    if len(sys.argv) <= 2:
        # Print available locationis and scenarios
        print("Available locations and scenarios:")
        for (location, loc_dict) in scenarios.items():
            print("  Location %s:" % location)
            for scenario_name in loc_dict['scenarios'].keys():
                print("    %s" % scenario_name)
        sys.exit(0)

    elif len(sys.argv) == 3:
        location = sys.argv[1]
        scenario = sys.argv[2]

    else:
        raise InputError("Expected a location and scenario.")

    if scenario not in scenarios[location]['scenarios'].keys():
        raise ValueError("Unknown scenario %s for location %s." % (scenario, 
                                                                   location))

    create_dtopo(scenarios[location], scenario)
