#!/usr/bin/env python3

from trafficLightGroup import TrafficLightGroup

import os
import sys

# we need to import python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

import traci.constants as tc


def getLinkGroups(tlID, program, sim):
    linkCount = len(program.phases[0].state)
    groups = []
    groupsPreferedPhase = []

    linkUsed = []
    for i in range(linkCount):
        linkUsed.append(False)

    for phaseIdx, phase in enumerate(program.phases):
        group = []
        for i, tlState in enumerate(phase.state):
            if tlState.lower() == "g" and not linkUsed[i]:
                group.append(i)
                linkUsed[i] = True
        if len(group) > 0:
            groups.append(group)
            groupsPreferedPhase.append(phaseIdx)

    if False in linkUsed:
        raise Exception("All links must be given a group.")

    return groups, groupsPreferedPhase

def getLinkGroupLaneDetectors(tlID, linkGroups, sim):
    groupsLaneDetectors = []
    links = sim.trafficlight.getControlledLinks(tlID)
    laneDetectorNames = sim.multientryexit.getIDList()
    trafficLightDetectors = dict()
    for detectorName in laneDetectorNames:
        dwa = detectorName.split("_")
        detectortlID = dwa[1]
        if detectortlID == tlID:
            roadID = dwa[2]
            if roadID not in trafficLightDetectors:
                trafficLightDetectors[roadID] = []
            trafficLightDetectors[roadID].append(detectorName)

    for group in linkGroups:
        groupLaneDetectors = []
        for gIdx in group:
            if len(links[gIdx]) > 0:
                incommingLane = links[gIdx][0][0]
                incommingRoad = incommingLane.split("_")[0]
                if incommingRoad in trafficLightDetectors:
                    for detector in trafficLightDetectors[incommingRoad]:
                        if detector not in groupLaneDetectors:
                            groupLaneDetectors.append(detector)
        groupsLaneDetectors.append(groupLaneDetectors)

    return groupsLaneDetectors


class TrafficLightIntersection():
    def __init__(self, tlID, sim):
        self.tlID = tlID
        self.program = sim.trafficlight.getAllProgramLogics(self.tlID)[0]
        self.tlGroups = []
        self.targetGroup = None
        self.currPhaseIdx = 0

        linkGroups, groupsPreferedPhase = getLinkGroups(self.tlID, self.program, sim)
        linkGroupsLaneDetectors = getLinkGroupLaneDetectors(self.tlID, linkGroups, sim)

        for i in range(len(linkGroups)):
            self.tlGroups.append(TrafficLightGroup(linkGroups[i], linkGroupsLaneDetectors[i], groupsPreferedPhase[i]))

        for group in self.tlGroups:
            group.subscribeLaneDetectors(sim)

        sim.trafficlight.subscribe(self.tlID, (tc.TL_CURRENT_PHASE,))

    def findNextPhaseToTargetGroup(self, currPhaseIdx):
        """
        The trafficlight must go through its yellow -> red -> yellow
        phases before it can go to its green phase. It does this by
        sequentially going through the trafficlights phases. But
        doing just that would mean that it may have to go through
        other groups green phases which is not desirable. This method
        returns the index of the next phase it should switch to while
        skipping over other groups green phases.
        """
        nextPhaseIdx = currPhaseIdx
        while "g" in self.program.phases[nextPhaseIdx].state.lower():
            nextPhaseIdx = (nextPhaseIdx + 1) % len(self.program.phases)
            if nextPhaseIdx == self.targetGroup.greenPhaseIdx:
                break

        return nextPhaseIdx

    def resetPhaseRemainingTime(self, phaseIdx, sim):
        phaseDuration = self.program.phases[phaseIdx].duration
        sim.trafficlight.setPhaseDuration(self.tlID, phaseDuration)     

    def update(self, sim):
        if self.targetGroup is not None:
            if self.currPhaseIdx == self.targetGroup.greenPhaseIdx:
                self.targetGroup = None
                return

            nextPhaseIdx = self.findNextPhaseToTargetGroup(self.currPhaseIdx)
            if self.currPhaseIdx != nextPhaseIdx:
                sim.trafficlight.setPhase(self.tlID, nextPhaseIdx)           

    def updateWithDataFromSumo(self, detectorData, trafficlightData):
        for group in self.tlGroups:
            group.updateLaneDetectorValues(detectorData)

        self.currPhaseIdx = trafficlightData[self.tlID][tc.TL_CURRENT_PHASE]

    def setGroupAsGreen(self, group, sim):
        if self.currPhaseIdx == group.greenPhaseIdx:
            self.resetPhaseRemainingTime(group.greenPhaseIdx, sim)
        else:
            self.targetGroup = group

    def setGroupsGreenPhaseLength(self, group, phaseLength, sim):
        self.program.phases[group.greenPhaseIdx].duration = phaseLength
        sim.trafficlight.setProgramLogic(self.tlID, self.program)

    def getTrafficLightGroups(self):
        return self.tlGroups

    def getCurretPhaseIndex(self):
        return self.currPhaseIdx