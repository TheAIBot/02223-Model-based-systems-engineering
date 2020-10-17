#!/usr/bin/env python
# Eclipse SUMO, Simulation of Urban MObility; see https://eclipse.org/sumo
# Copyright (C) 2009-2020 German Aerospace Center (DLR) and others.
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License 2.0 which is available at
# https://www.eclipse.org/legal/epl-2.0/
# This Source Code may also be made available under the following Secondary
# Licenses when the conditions for such availability set forth in the Eclipse
# Public License 2.0 are satisfied: GNU General Public License, version 2
# or later which is available at
# https://www.gnu.org/licenses/old-licenses/gpl-2.0-standalone.html
# SPDX-License-Identifier: EPL-2.0 OR GPL-2.0-or-later

# @file    runner.py
# @author  Lena Kalleske
# @author  Daniel Krajzewicz
# @author  Michael Behrisch
# @author  Jakob Erdmann
# @date    2009-03-26

from __future__ import absolute_import
from __future__ import print_function

import os
import sys
import optparse
import random

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

def numberv(lane):
    nb = 0
    for k in traci.lane.getLastStepVehicleIDs(lane):
        if traci.vehicle.getLanePosition(k) < X-100:
             nb += 1
    return nb

def run():
    """execute the TraCI control loop"""
    print("--------------- Simulation started! ---------------")
    step = 0
    
    # Id of the traffic light
    tlId = 'gneJ1'
    
    # Set start phase to 0 (starts at red)
    traci.trafficlight.setPhase(tlId, 0)

    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        print(f"step: {step}")
    
        if traci.trafficlight.getPhase(tlId) == 0:
            print("Phase 0: Red")
        elif traci.trafficlight.getPhase(tlId) == 1:
            print("Phase 1: Yellow")
        elif traci.trafficlight.getPhase(tlId) == 2:
            print("Phase 2: Green")
            
        if traci.lanearea.getLastStepVehicleNumber(tlId) > 0:
            # there is a vehicle incoming from the left lane, switch to
            # yellow for a few seconds before changing to green
            if traci.trafficlight.getPhase(tlId) == 0:
                traci.trafficlight.setPhase(tlId, 1)
                traci.trafficlight.setPhaseDuration(tlId, 5.0)
            elif traci.trafficlight.getPhase(tlId) == 1:
                traci.trafficlight.setPhase(tlId, 2)
        else:
            # if there is no vehicles coming from the left lane,
            # switch to yellow for a few seconds, then switch to red.
            if traci.trafficlight.getPhase(tlId) == 2:
                traci.trafficlight.setPhase(tlId, 1)
                traci.trafficlight.setPhaseDuration(tlId, 5.0)
            elif traci.trafficlight.getPhase(tlId) == 1:
                traci.trafficlight.setPhase(tlId, 0)
        step += 1
    traci.close()
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
    #generate_routefile()

    # this is the normal way of using traci. sumo is started as a
    # subprocess and then the python script connects and runs
    print("--------------- TraCI is ready. Waiting for simulation... ---------------")
    traci.start([sumoBinary, "-c", "config.sumocfg",
                             "--tripinfo-output", "tripinfo.xml"])
    run()
