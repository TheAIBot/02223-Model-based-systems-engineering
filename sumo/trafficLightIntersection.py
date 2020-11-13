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

    def update(self, sim):
        if self.targetGroup is not None:
            currPhaseIdx = sim.trafficlight.getPhase(self.tlID)

            if currPhaseIdx == self.targetGroup.greenPhaseIdx:
                self.targetGroup = None
                return

            nextPhaseIdx = currPhaseIdx
            gotoNextPhase = True
            while gotoNextPhase:
                gotoNextPhase = False
                for tlState in self.program.phases[nextPhaseIdx].state:
                    if tlState == "g":
                        nextPhaseIdx = (nextPhaseIdx + 1) % len(self.program.phases)
                        gotoNextPhase = True
                        break

                if nextPhaseIdx == self.targetGroup.greenPhaseIdx:
                    break

            if currPhaseIdx != nextPhaseIdx:
                sim.trafficlight.setPhase(self.tlID, nextPhaseIdx)

    def setGroupAsGreen(self, group, sim):
        if sim.trafficlight.getPhase(self.tlID) == group.greenPhaseIdx:
            phaseDuration = self.program.phases[group.greenPhaseIdx].duration
            sim.trafficlight.setPhaseDuration(self.tlID, phaseDuration)
        else:
            self.targetGroup = group

    def getTrafficLightGroups(self):
        return self.tlGroups