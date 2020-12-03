#!/usr/bin/env python3

from __future__ import absolute_import
from __future__ import print_function

import os
import sys
import optparse
import random
import pathlib as Path
import string
import datetime
now = datetime.datetime.now

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

SUMO = None
SUMO_IMPL = None

def _import_libsumo():
    global SUMO, SUMO_IMPL
    import libsumo as libsumo_hidden
    SUMO = libsumo_hidden
    SUMO_IMPL = "libsumo"

def _import_traci():
    global SUMO, SUMO_IMPL
    import traci as traci_hidden
    SUMO = traci_hidden
    SUMO_IMPL = "traci"

try:
    _import_libsumo()
except:
    print("Libsumo unavailable, falling back to TraCI.")
    _import_traci()

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

    def __init__(self, mapConfigFilepath, trafficLightController, scale = 1, gui = False):
        if gui and SUMO_IMPL == "libsumo":
            print("Libsumo doesn't support launching the GUI, falling back to TraCI.")
            _import_traci()

        self.tlCtrl = trafficLightController
        self.label = str(self.tlCtrl) + ''.join(random.choice(string.ascii_lowercase) for i in range(20))

        SUMO.start([checkBinary("sumo-gui" if gui else "sumo"), "-c", mapConfigFilepath, "--device.emissions.probability", "1", "--waiting-time-memory", "100000", "--no-warnings", "true", "--scale", str(scale)])

        trafficLightController.init(SUMO)

    def run(self, takeMeasurements = True, maxTicks = 100000, ticksStartBreaking = 100000, maxAverage = 1000000):
        measurements = SimMeasurements(1, self.tlCtrl)

        start_time = now()

        ticks = 0
        while SUMO.simulation.getMinExpectedNumber() > 0:
            self.tlCtrl.update(SUMO, ticks)

            if takeMeasurements:
                measurements.update(SUMO)

            SUMO.simulationStep()
            if ticks>ticksStartBreaking and measurements.getAverageTravelTime()>maxAverage:
                break
            ticks += 1
            if ticks > maxTicks:
                break

        measurements.collectAfterSimEnd(SUMO)

        SUMO.close()
        sys.stdout.flush()

        print("=== Controller '{}' took {} to finish. ===".format(
            self.tlCtrl.getName(),
            now() - start_time,
        ))

        return measurements