#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import print_function

import os
import sys
import optparse
import random
import pathlib as Path
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
parentdirdir = os.path.dirname(parentdir)
sys.path.append(parentdirdir)
import routeGen
import trip_stats as Stats

# we need to import python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

from sumolib import checkBinary  # noqa
import traci  # noqa


def get_options():
    optParser = optparse.OptionParser()
    optParser.add_option("--nogui", action="store_true",
                         default=False, help="run the commandline version of sumo")
    options, args = optParser.parse_args()
    return options


def run():
    """execute the TraCI control loop"""
    print("--------------- Simulation started! ---------------")
    step = 0

    # begin simulation loop
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        print(f"step: {step}")
    traci.close()
    Stats.gen_trip_stats()
    sys.stdout.flush()


# this is the main entry point of this script
if __name__ == "__main__":
    options = get_options()

    # this script has been called from the command line. It will start sumo as a
    # server, then connect and run
    if options.nogui:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')

    # first, generate the route file for this simulation
    mapFilePath = "network.net.xml"
    routesFilepath = routeGen.gen_random_routes(mapFilePath, 50)
    laneDecPath = "lanedetector.xml"

    # generate config.sumocfg
    mapFolder = os.path.dirname(mapFilePath)
    mapName = Path.Path(mapFilePath).stem
    mapConfigFilepath = os.path.join(mapFolder, "config.sumocfg")
    with open(mapConfigFilepath, "w") as mapConfig:
        print("<configuration>", file=mapConfig)
        print("    <input>", file=mapConfig)
        print("        <net-file value=\"{}\"/>".format(os.path.basename(mapFilePath)), file=mapConfig)
        print("        <route-files value=\"{}\"/>".format(os.path.basename(routesFilepath)), file=mapConfig)
        print("    </input>", file=mapConfig)
        print("</configuration>", file=mapConfig)

    # this is the normal way of using traci. sumo is started as a
    # subprocess and then the python script connects and runs
    print("--------------- TraCI is ready. Waiting for simulation... ---------------")
    traci.start([sumoBinary, "-c", mapConfigFilepath, "--device.emissions.probability", "1", "--tripinfo-output", "tripinfo.xml"])
    run()
