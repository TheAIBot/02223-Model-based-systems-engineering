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

    # Id of the traffic light
    tlId = 'n0'
    
    # Phase information:
    # 0: Vertical green light
    # 1: Horizontal green light
    # 2: Vertical yellow light
    # 3: Horizontal yellow light
    # 4: All red

    # define the phases as variables just for ease of use
    vGreen = 0
    hGreen = 1
    vYellow = 2
    hYellow = 3
    red = 4

    # define the different lane detector id's as variable, for ease of use
    laneLeft = "lad_n1"
    laneTop = "lad_n2"
    laneRight = "lad_n3"
    laneBottom = "lad_n4"

    # make an array of the lane detector ids so we can easily use it with loops
    laneDetectors = [laneLeft, laneTop, laneRight, laneBottom]

    # Set start phase to 4 (red) to start with
    traci.trafficlight.setPhase(tlId, red)

    # begin simulation loop
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        print(f"step: {step}")
    
        # print out useful information about current phase
        if traci.trafficlight.getPhase(tlId) == vGreen:
            print("Phase 0: Vertical green light")
        elif traci.trafficlight.getPhase(tlId) == hGreen:
            print("Phase 1: Horizontal green light")
        elif traci.trafficlight.getPhase(tlId) == vYellow:
            print("Phase 2: Vertical yellow light")
        elif traci.trafficlight.getPhase(tlId) == hYellow:
            print("Phase 3: Horizontal yellow light")
        elif traci.trafficlight.getPhase(tlId) == red:
            print("Phase 4: Red")
        
        # loop through all of the lane detectors,
        # find out which lane that has the greatest amount of cars
        mostTrafficDetector = "";
        mostTrafficNum = 0;
        for detectorId in laneDetectors:
            lsNum = traci.lanearea.getLastStepVehicleNumber(detectorId)
            if lsNum > 0 and lsNum > mostTrafficNum:
                mostTrafficNum = lsNum
                mostTrafficDetector = detectorId

        if mostTrafficDetector != "":
            print(f"Most traffic: {mostTrafficDetector}, Number: {mostTrafficNum}")
            if mostTrafficDetector == laneLeft or mostTrafficDetector == laneRight:
                traci.trafficlight.setPhase(tlId, hGreen)
            elif mostTrafficDetector == laneTop or mostTrafficDetector == laneBottom:
                traci.trafficlight.setPhase(tlId, vGreen)

    """
    print("Loop done.")

    arrivedNum = traci.simulation.getArrivedNumber()
    arrivedIds = traci.simulation.getArrivedIDList()

    durSum = 0
    for id in arrivedIds:
        duration = traci.simulation.getParameter(id, "duration")
        durSum = durSum + duration
    
    avgDuration = durSum / arrivedNum

    print("Arrived vehicles: {arrivedNum}, Vehicle simulation duration sum: {durSum}, Vehicle average simulation duration: {avgDuration}")
    """


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
        print("        <additional-files value=\"{}\"/>".format(os.path.basename(laneDecPath)), file=mapConfig)
        print("    </input>", file=mapConfig)
        print("</configuration>", file=mapConfig)

    # this is the normal way of using traci. sumo is started as a
    # subprocess and then the python script connects and runs
    print("--------------- TraCI is ready. Waiting for simulation... ---------------")
    traci.start([sumoBinary, "-c", mapConfigFilepath, "--device.emissions.probability", "1", "--tripinfo-output", "tripinfo.xml"])
    run()
