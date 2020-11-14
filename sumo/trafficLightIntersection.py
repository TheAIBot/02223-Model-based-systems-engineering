#!/usr/bin/env python3

from trafficLightGroup import TrafficLightGroup


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
            if tlState == "g" and not linkUsed[i]:
                group.append(i)
                linkUsed[i] = True
        if len(group) > 0:
            groups.append(group)
            groupsPreferedPhase.append(phaseIdx)

    return groups, groupsPreferedPhase

def getLinkGroupLaneDetectors(tlID, linkGroups, sim):
    groupsLaneDetectors = []
    links = sim.trafficlight.getControlledLinks(tlID)
    laneDetectorNames = sim.lanearea.getIDList()

    laneDetectorNameIDs = []
    for laneDName in laneDetectorNames:
        laneDetectorNameIDs.append(sim.lanearea.getLaneID(laneDName))

    for group in linkGroups:
        groupLaneDetectors = []
        for gIdx in group:
            if len(links[gIdx]) > 0:
                incommingLane = links[gIdx][0][0]
                if incommingLane in laneDetectorNameIDs:
                    laneDetectorName = laneDetectorNames[laneDetectorNameIDs.index(incommingLane)]
                    if laneDetectorName not in groupLaneDetectors:
                        groupLaneDetectors.append(laneDetectorName)
        groupsLaneDetectors.append(groupLaneDetectors)

    return groupsLaneDetectors


class TrafficLightIntersection():
    def __init__(self, tlID, sim):
        self.tlID = tlID
        self.program = sim.trafficlight.getAllProgramLogics(self.tlID)[0]
        self.tlGroups = []
        self.targetGroup = None

        linkGroups, groupsPreferedPhase = getLinkGroups(self.tlID, self.program, sim)
        linkGroupsLaneDetectors = getLinkGroupLaneDetectors(self.tlID, linkGroups, sim)

        for i in range(len(linkGroups)):
            self.tlGroups.append(TrafficLightGroup(linkGroups[i], linkGroupsLaneDetectors[i], groupsPreferedPhase[i]))

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
        while "g" in self.program.phases[nextPhaseIdx].state:
            nextPhaseIdx = (nextPhaseIdx + 1) % len(self.program.phases)
            if nextPhaseIdx == self.targetGroup.greenPhaseIdx:
                break

        return nextPhaseIdx

    def resetPhaseRemainingTime(self, phaseIdx, sim):
        phaseDuration = self.program.phases[phaseIdx].duration
        sim.trafficlight.setPhaseDuration(self.tlID, phaseDuration)

    def update(self, sim):
        if self.targetGroup is not None:
            currPhaseIdx = sim.trafficlight.getPhase(self.tlID)

            #if has reached the correct phase
            if currPhaseIdx == self.targetGroup.greenPhaseIdx:
                self.targetGroup = None
                return

            nextPhaseIdx = self.findNextPhaseToTargetGroup(currPhaseIdx)
            if currPhaseIdx != nextPhaseIdx:
                sim.trafficlight.setPhase(self.tlID, nextPhaseIdx)

    def setGroupAsGreen(self, group, sim):
        if sim.trafficlight.getPhase(self.tlID) == group.greenPhaseIdx:
            self.resetPhaseRemainingTime(group.greenPhaseIdx, sim)
        else:
            self.targetGroup = group

    def setGroupsGreenPhaseLength(self, group, phaseLength, sim):
        self.program.phases[group.greenPhaseIdx].duration = phaseLength
        sim.trafficlight.setProgramLogic(self.tlID, self.program)

    def getTrafficLightGroups(self):
        return self.tlGroups