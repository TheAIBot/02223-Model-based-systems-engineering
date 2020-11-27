#!/usr/bin/env python3

from __future__ import absolute_import
from __future__ import print_function

import os
import sys
import optparse
import random
import pathlib as Path
import string

import sumoTools
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

def createSimSumoConfigWithRandomTraffic(mapFilepath, trafficThroughputMultiplier = 0.5, additionalTrafficlighPhases = False):
    routeFile = sumoTools.generateRoutes(mapFilepath, 50, 100, trafficThroughputMultiplier)
    return createSimSumoConfig(mapFilepath, routeFile, additionalTrafficlighPhases = additionalTrafficlighPhases)

def createSimSumoConfig(mapFilepath, routeFile, additionalTrafficlighPhases = False):
    additionalFiles = ["lanedetector.xml"]
    if additionalTrafficlighPhases:
        sumoTools.modifyTrafficLightPhases(mapFilepath)
        additionalFiles.append("trafficlightPhases.xml")

    mapFolder = os.path.dirname(mapFilepath)
    mapName = Path.Path(mapFilepath).stem
    mapConfigFilepath = os.path.join(mapFolder, mapName + ".sumocfg")
    with open(mapConfigFilepath, "w") as mapConfig:
        print("<configuration>", file=mapConfig)
        print("    <input>", file=mapConfig)
        print("        <net-file value=\"{}\"/>".format(os.path.basename(mapFilepath)), file=mapConfig)
        print("        <route-files value=\"{}\"/>".format(routeFile), file=mapConfig)
        print("        <additional-files value=\"{}\"/>".format(str.join(", ", additionalFiles)), file=mapConfig)
        print("    </input>", file=mapConfig)
        print("</configuration>", file=mapConfig)

    return mapConfigFilepath

class SumoSim():

    def __init__(self, mapConfigFilepath, trafficLightController, scale = 1):
        self.tlCtrl = trafficLightController
        self.label = str(self.tlCtrl) + ''.join(random.choice(string.ascii_lowercase) for i in range(20))

        traci.start([checkBinary("sumo"), "-c", mapConfigFilepath, "--device.emissions.probability", "1", "--waiting-time-memory", "100000", "--no-warnings", "true", "--scale", str(scale)], label = self.label)
        self.sumoCon = traci.getConnection(self.label)

        trafficLightController.init(self.sumoCon)

    def run(self, takeMeasurements = True, maxTicks = 100000, ticksStartBreaking = 100000, maxAverage = 1000000):
        measurements = SimMeasurements(1, self.tlCtrl)

        ticks = 0
        while self.sumoCon.simulation.getMinExpectedNumber() > 0:
            self.tlCtrl.update(self.sumoCon, ticks)

            if takeMeasurements:
                measurements.update(self.sumoCon)

            self.sumoCon.simulationStep()
            if ticks>ticksStartBreaking and measurements.getAverageTravelTime()>maxAverage:
                break
            ticks += 1
            if ticks > maxTicks:
                break

        measurements.collectAfterSimEnd(self.sumoCon)

        self.sumoCon.close()
        sys.stdout.flush()

        return measurements