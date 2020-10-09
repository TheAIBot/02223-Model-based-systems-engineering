from __future__ import absolute_import
from __future__ import print_function

import os
import sys
import optparse
import random
import pathlib as Path

import routeGen

# we need to import python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

from sumolib import checkBinary  # noqa
import traci  # noqa

class SumoSim():

    def __init__(self, mapFilepath, trafficLightController):
        self.tlCtrl = trafficLightController

        routesFilepath = routeGen.gen_random_routes(mapFilepath)

        mapFolder = os.path.dirname(mapFilepath)
        mapName = Path.Path(mapFilepath).stem
        mapConfigFilepath = os.path.join(mapFolder, mapName + ".sumocfg")
        with open(mapConfigFilepath, "w") as mapConfig:
            print("<configuration>", file=mapConfig)
            print("    <input>", file=mapConfig)
            print("        <net-file value=\"{}\"/>".format(mapFilepath), file=mapConfig)
            print("        <route-files value=\"{}\"/>".format(routesFilepath), file=mapConfig)
            print("    </input>", file=mapConfig)
            print("</configuration>", file=mapConfig)

        traci.start([checkBinary('sumo'), "-c", mapConfigFilepath])

    def run(self):
        ticks = 0
        while traci.simulation.getMinExpectedNumber() > 0:
            self.tlCtrl.updateLights(traci.simulation)

            traci.simulationStep()
            ticks += 1

        traci.close()
        sys.stdout.flush()

        return ticks