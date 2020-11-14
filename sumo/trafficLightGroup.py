#!/usr/bin/env python3

import os
import sys

# we need to import python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

import traci.constants as tc

class TrafficLightGroup():
    def __init__(self, linkIdxs, laneDetectorIDs, greenPhaseIdx):
        self.linkIDxs = linkIdxs
        self.laneDetectorIDs = laneDetectorIDs
        self.greenPhaseIdx = greenPhaseIdx
        self.laneDetectorValues = dict()
        for detectorID in range(len(self.laneDetectorIDs)):
            self.laneDetectorValues[detectorID] = 0

    def getLaneDetectorIDs(self):
        return self.laneDetectorIDs

    def subscribeLaneDetectors(self, sim):
        for detectorID in self.laneDetectorIDs:
            sim.multientryexit.subscribe(detectorID, (tc.LAST_STEP_VEHICLE_NUMBER,))

    def updateLaneDetectorValues(self, subscribedData):
        for detectorID in self.laneDetectorIDs:
            self.laneDetectorValues[detectorID] = subscribedData[detectorID][tc.LAST_STEP_VEHICLE_NUMBER]

    def getLaneDetectorValues(self):
        return self.laneDetectorValues.values()

    #def subscribeLaneDetectors