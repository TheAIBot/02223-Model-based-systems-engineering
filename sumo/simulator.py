#!/usr/bin/env python3

from __future__ import absolute_import
from __future__ import print_function

import os
import sys
import optparse
import random
import pathlib as Path

import routeGen
from simMeasurements import SimMeasurements

# we need to import python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

from sumolib import checkBinary  # noqa
import traci  # noqa






class SumoSim():

    def __init__(self, mapFilepath, trafficLightController, trafficThroughputMultiplier = 0.25):
        self.tlCtrl = trafficLightController

        tripFiles = []
        for i in range(10):
            tripFiles.append(routeGen.genRandomTrips(mapFilepath, i, 50, trafficThroughputMultiplier))
        routeFile = os.path.basename(routeGen.genRoutesFromTrips(mapFilepath, tripFiles))

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

        traci.start([checkBinary("sumo"), "-c", mapConfigFilepath, "--device.emissions.probability", "1", "--waiting-time-memory", "100000"], label= str(self.tlCtrl))
        self.sumoCon = traci.getConnection(str(self.tlCtrl))

        trafficLightController.init(self.sumoCon)

    def run(self):
        measurements = SimMeasurements(1)

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