#!/usr/bin/env python3

from __future__ import absolute_import
from __future__ import print_function

import os
import sys
import optparse
import random
import pathlib as Path

import string

import routeGen
from simMeasurements import SimMeasurements

random.seed(864)

# we need to import python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

from sumolib import checkBinary  # noqa
import traci  # noqa

def createSimSumoConfigWithRandomTraffic(mapFilepath, trafficThroughputMultiplier = 0.25):
    routeFile = routeGen.generateRoutes(mapFilepath, 50, 10, trafficThroughputMultiplier)
    return createSimSumoConfig(mapFilepath, routeFile)

def createSimSumoConfig(mapFilepath, routeFile):
    mapFolder = os.path.dirname(mapFilepath)
    mapName = Path.Path(mapFilepath).stem
    mapConfigFilepath = os.path.join(mapFolder, mapName + ".sumocfg")
    with open(mapConfigFilepath, "w") as mapConfig:
        print("<configuration>", file=mapConfig)
        print("    <input>", file=mapConfig)
        print("        <net-file value=\"{}\"/>".format(os.path.basename(mapFilepath)), file=mapConfig)
        print("        <route-files value=\"{}\"/>".format(routeFile), file=mapConfig)
        print("        <additional-files value=\"{}\"/>".format("lanedetector.xml"), file=mapConfig)
        print("    </input>", file=mapConfig)
        print("</configuration>", file=mapConfig)

    return mapConfigFilepath

class SumoSim():

    def __init__(self, mapConfigFilepath, trafficLightController):
        self.tlCtrl = trafficLightController
        self.label = str(self.tlCtrl) + ''.join(random.choice(string.ascii_lowercase) for i in range(20))

        traci.start([checkBinary("sumo"), "-c", mapConfigFilepath, "--device.emissions.probability", "1", "--waiting-time-memory", "100000"], label = self.label)
        self.sumoCon = traci.getConnection(self.label)

        trafficLightController.init(self.sumoCon)

    def run(self):
        measurements = SimMeasurements(1, self.tlCtrl)

        ticks = 0
        while self.sumoCon.simulation.getMinExpectedNumber() > 0:
            self.tlCtrl.updateLights(self.sumoCon, ticks)

            measurements.update(self.sumoCon)

            self.sumoCon.simulationStep()
            ticks += 1

        measurements.collectAfterSimEnd(self.sumoCon)

        self.sumoCon.close()
        sys.stdout.flush()

        return measurements