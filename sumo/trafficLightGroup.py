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

        self.currentStepDetectorVehicles = dict()
        self.detectorLastStepNewVehiclesCount = dict()
        for detectorID in self.laneDetectorIDs:
            self.currentStepDetectorVehicles[detectorID] = []
            self.detectorLastStepNewVehiclesCount[detectorID] = 0

    def getLaneDetectorIDs(self):
        return self.laneDetectorIDs

    def subscribeLaneDetectors(self, sim):
        for detectorID in self.laneDetectorIDs:
            sim.multientryexit.subscribe(detectorID, (tc.LAST_STEP_VEHICLE_ID_LIST,))

    def updateLaneDetectorValues(self, subscribedData):
        self.lastStepNewVehiclesCount = 0
        for detectorID in self.laneDetectorIDs:
            prevDetectorVehicles = self.currentStepDetectorVehicles[detectorID]
            self.currentStepDetectorVehicles[detectorID] = []
            self.detectorLastStepNewVehiclesCount[detectorID] = 0

            for vehicleID in subscribedData[detectorID][tc.LAST_STEP_VEHICLE_ID_LIST]:
                if vehicleID not in prevDetectorVehicles:
                    self.detectorLastStepNewVehiclesCount[detectorID] += 1
                self.currentStepDetectorVehicles[detectorID].append(vehicleID)

    def getLaneDetectorValues(self):
        detectorValues = dict()
        for detectorID in self.laneDetectorIDs:
            detectorValues[detectorID] = len(self.currentStepDetectorVehicles[detectorID])

        return detectorValues

    def getSumLaneDetectorValues(self):
        detectorSum = 0
        for detectorID in self.laneDetectorIDs:
            detectorSum += len(self.currentStepDetectorVehicles[detectorID])

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

    def getLastStepNewVehiclesCount(self):
        newVehicles = 0
        for detectorID in self.laneDetectorIDs:
            newVehicles += self.detectorLastStepNewVehiclesCount[detectorID]

        return newVehicles

    def getVehicleIDsFromDetectors(self):
        detectorVehicles = []
        for detectorID in self.laneDetectorIDs:
            detectorVehicles.extend(self.currentStepDetectorVehicles[detectorID])

        return detectorVehicles

    def getDetectorVehicleIDs(self, detectorID):
        return self.currentStepDetectorVehicles[detectorID]

    def getDetectorLastStepNewVehiclesCount(self, detectorID):
        return self.detectorLastStepNewVehiclesCount[detectorID]
