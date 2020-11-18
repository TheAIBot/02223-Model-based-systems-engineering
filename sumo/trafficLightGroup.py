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
    def __init__(self, tlInter, linkIdxs, laneDetectorIDs, greenPhaseIdx):
        self.tlInter = tlInter
        self.linkIDxs = linkIdxs
        self.laneDetectorIDs = laneDetectorIDs
        self.greenPhaseIdx = greenPhaseIdx
        self.currentStepVehicles = set()
        self.lastStepNewVehiclesCount = 0
        self.laneDetectorValues = dict()
        for detectorID in range(len(self.laneDetectorIDs)):
            self.laneDetectorValues[detectorID] = 0

    def getLaneDetectorIDs(self):
        return self.laneDetectorIDs

    def subscribeLaneDetectors(self, sim):
        for detectorID in self.laneDetectorIDs:
            sim.multientryexit.subscribe(detectorID, (tc.LAST_STEP_VEHICLE_NUMBER, tc.LAST_STEP_VEHICLE_ID_LIST))

    def updateLaneDetectorValues(self, subscribedData):
        for detectorID in self.laneDetectorIDs:
            self.laneDetectorValues[detectorID] = subscribedData[detectorID][tc.LAST_STEP_VEHICLE_NUMBER]

        self.lastStepNewVehiclesCount = 0
        previousStepVehicles = self.currentStepVehicles
        self.currentStepVehicles = set(subscribedData[detectorID][tc.LAST_STEP_VEHICLE_ID_LIST])
        for detectorID in self.laneDetectorIDs:
            for vehicleID in self.currentStepVehicles:
                if vehicleID not in previousStepVehicles:
                    self.lastStepNewVehiclesCount += 1

    def getLaneDetectorValues(self):
        return self.laneDetectorValues.values()

    def getSumLaneDetectorValues(self):
        detectorSum = 0
        for value in self.laneDetectorValues.values():
            detectorSum += value

        return detectorSum

    def getTLLinkIndexes(self):
        return self.linkIDxs

    def getGreenPhaseIndex(self):
        return self.greenPhaseIdx

    def getincommingLaneIDs(self):
        incommingLanes = []
        links = self.tlInter.getControlledLinks()
        for linkIdx in self.linkIDxs:
            if len(links[linkIdx]) > 0:
                incommingLanes.append(links[linkIdx][0][0])

        return incommingLanes

    def getoutgoingLaneIDs(self):
        outgoingLanes = []
        links = self.tlInter.getControlledLinks()
        for linkIdx in self.linkIDxs:
            if len(links[linkIdx]) > 0:
                outgoingLanes.append(links[linkIdx][0][2])

        return outgoingLanes

    def getLastStepNewVehicles(self):
        return self.lastStepNewVehiclesCount
