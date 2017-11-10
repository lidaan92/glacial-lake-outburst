#!/usr/bin/env python

from __future__ import print_function

import sys
import os
import subprocess

import numpy
import matplotlib.pyplot as plt

import batch

locations = {'imja': {"scenarios": ["island_peak", "amphulapche", "snow_line"],
                      "domain": [487000, 498000, 3083000, 3090000],
                      "gauges": [[1, 491350, 3086100, 0.0, 1e10]],
                      "topo": ['topo/imja.tt3', 'topo/everest.tt3'],
                      "lake_region": [4, 4, 0.0, 1e10, 491000, 493700, 3085250, 3086250]
              }, 
              'barun': {"scenarios": {},
                        "domain": [],
                        "gauges": [],
                        "topo": []
              }, 
              'thulagi': {"scenarios": {},
                          "domain": [],
                          "gauges": [],
                          "topo": []
              } 
            }

class GlacialOutburstJob(batch.Job):
    """Jobs describing a glacial outburst flood"""

    def __init__(self, location, scenario):
        r"""
        Initialize a GlacialOutburstJob object.
        
        See :class:`GlacialOutburstJob` for full documentation
        
        """

        super(GlacialOutburstJob, self).__init__()

        # Check to make sure the topography is available

        # Check and make sure slide data is available


        # Set job descriptors
        self.type = "glacial_flood"
        self.name = "%s" % location
        self.prefix = "%s" % scenario
        self.executable = 'xgeoclaw'

        self.location = location
        self.scenario = scenario

        # Data
        import setrun
        self.rundata = setrun.setrun()

        # Set domain
        self.rundata.clawdata.lower = locations[location]["domain"][:2]
        self.rundata.clawdata.upper = locations[location]["domain"][2:]

        # Set topography
        self.rundata.topo_data.topofiles = []
        for path in locations[location]["topo"]:
            topo_path = os.path.abspath(os.path.join(os.getcwd(), path))
            self.rundata.topo_data.topofiles.append([3, 1, 10, 0.0, 1e10, topo_path])

        # Set slide
        self.rundata.dtopo_data.dtopofiles = []
        path = os.path.abspath(os.path.join(os.getcwd(), 'topo', 
                                       "%s_dtopo.tt3" % scenario))
        self.rundata.dtopo_data.dtopofiles.append([3, 0, 10, path])

        # Regions
        self.rundata.regiondata.regions = []
        #  [minlevel,maxlevel,t1,t2,x1,x2,y1,y2]
        rundata.regiondata.regions.append(locations[location]['lake_region'])

        # Set gauges
        self.rundata.gaugedata.gauges = locations[location]['gauges']


    def write_data_objects(self):

        # Create topography if needed
        cmd_path = os.path.join(os.getcwd(), "topo", "convert_topo.py")
        cmd = "python %s %s" % (cmd_path, self.location)
        subprocess.call(cmd, shell=True)

        # Create slide dtopo if needed
        cmd_path = os.path.join(os.getcwd(), "topo", "make_dtopo.py")
        cmd = "python %s %s %s" % (cmd_path, self.location, self.scenario)
        subprocess.call(cmd, shell=True)


    def __str__(self):
        return "%s - %s" % (self.location, self.scenario)


if __name__ == "__main__":

    location_runs = locations.keys()

    if len(sys.argv) > 1:
        location_runs = sys.argv[1:]


    # Create jobs for each location requested
    jobs = []
    job_numbers = 0
    for location in location_runs:
        for scenario in locations[location]['scenarios']:
            jobs.append(GlacialOutburstJob(location, scenario))

    controller = batch.BatchController(jobs)
    controller.wait = False
    controller.plot = False
    print(controller)

    # controller.run()