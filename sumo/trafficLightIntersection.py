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

#Traffic light foes are traffic lights that should change to red.
#This is a list over the allowed changes that leads to red.
allowedFoeTLChange = dict()
allowedFoeTLChange["G"] = ["g", "y"] 
allowedFoeTLChange["g"] = ["y"] 
allowedFoeTLChange["y"] = ["r"]

def isFoeTLStateChangeAllowed(prevState, newState):
    if prevState == newState:
        return True

    if prevState in allowedFoeTLChange:
        return newState in allowedFoeTLChange[prevState]
    else:
        return False

#Traffic light friends are traffic lights that should change to green.
#This is a list over the allowed changes that leads to green.
allowedFriendTLChange = dict()
allowedFriendTLChange["u"] = ["g", "G"]
allowedFriendTLChange["r"] = ["y", "g", "G"]
allowedFriendTLChange["y"] = ["g", "G"]

def isFriendTLStateChangeAllowed(prevState, newState):
    if prevState == newState:
        return True

    if prevState in allowedFriendTLChange:
        return newState in allowedFriendTLChange[prevState]
    else:
        return False

def getLinkGroups(tlID, program, sim):
    linkCount = len(program.phases[0].state)
    groups = []
    groupsPreferedPhase = []


    for _ in range(len(program.phases)):
        groups.append([])

    #each link should be part of a group.
    #go through all phases and find a phase
    #where the link is green. Links that are
    #green in the same phase will be added to
    #the same group.
    for linkIdx in range(linkCount):
        foundGreenPhase = False
        #G has higher priority than g so
        #a link should prefer being part of
        #the group where it's in state G.
        #Not all links have a G state and in
        #those cases they will be part of the
        #group where they are in their g state.
        for phaseIdx in range(len(program.phases)):
            if program.phases[phaseIdx].state[linkIdx].upper() == "G":
                foundGreenPhase = True
                groups[phaseIdx].append(linkIdx)
                break
        if not foundGreenPhase:
            for phaseIdx in range(len(program.phases)):
                if program.phases[phaseIdx].state[linkIdx] == "g":
                    foundGreenPhase = True
                    groups[phaseIdx].append(linkIdx)
                    break
            if not foundGreenPhase:
                raise Exception("All links must have a green phase")

    linkGroups = []
    for phaseIdx, group in enumerate(groups):
        if len(group) > 0:
            linkGroups.append(group)
            groupsPreferedPhase.append(phaseIdx)

    return linkGroups, groupsPreferedPhase

def getLinkGroupLaneDetectors(tlID, linkGroups, links, sim):
    groupsLaneDetectors = []
    laneDetectorNames = sim.multientryexit.getIDList()
    trafficLightDetectors = dict()

    for _ in range(len(linkGroups)):
        groupsLaneDetectors.append([])

    #get the lanes that the detectors are placed on
    for detectorName in laneDetectorNames:
        dwa = detectorName.split("_")
        detectortlID = dwa[1]
        if detectortlID == tlID:
            roadID = dwa[2]
            if roadID in trafficLightDetectors:
                raise Exception("Honestly now sure if two detectors can be on the same road.")
            trafficLightDetectors[roadID] = detectorName

    for roadID, detectorName in trafficLightDetectors.items():
        #a detector can be used by multiple traffic light groups.
        #This causes problem so a detector must only be part of
        #one traffic light group. Each group is scored on how
        #many of its links are part of the detector. The group
        #with the highest score is awarded the detector.
        groupScores = []
        for linkGroup in linkGroups:
            score = 0
            for linkIdx in linkGroup:
                if len(links[linkIdx]) > 0:
                    incommingLaneID = links[linkIdx][0][0]
                    incommingRoadID = incommingLaneID.split("_")[0]
                    if incommingRoadID == roadID:
                        score += 1
            groupScores.append(score)

        bestGroupIdx = -1
        bestGroupScore = 0
        for groupIdx, score in enumerate(groupScores):
            if bestGroupIdx == -1 or score > bestGroupScore:
                bestGroupIdx = groupIdx
                bestGroupScore = score

        groupsLaneDetectors[bestGroupIdx].append(detectorName)

    return groupsLaneDetectors


class TrafficLightIntersection():
    def __init__(self, tlID, sim):
        self.tlID = tlID
        self.program = sim.trafficlight.getAllProgramLogics(self.tlID)[0]
        self.tlControlledLinks = sim.trafficlight.getControlledLinks(self.tlID)
        self.tlGroups = []
        self.targetGroup = None
        self.currPhaseIdx = 0
        self.prevPhaseIdx = 0
        self.justSwitchedPhase = False
        self.timeInPhase = 0
        self.isInPrevTargetGreenPhase = False

        linkGroups, groupsPreferedPhase = getLinkGroups(self.tlID, self.program, sim)
        linkGroupsLaneDetectors = getLinkGroupLaneDetectors(self.tlID, linkGroups, self.tlControlledLinks, sim)

        for i in range(len(linkGroups)):
            self.tlGroups.append(TrafficLightGroup(self, linkGroups[i], linkGroupsLaneDetectors[i], groupsPreferedPhase[i]))

        for group in self.tlGroups:
            group.subscribeLaneDetectors(sim)

        sim.trafficlight.subscribe(self.tlID, (tc.TL_CURRENT_PHASE,))

    def findNextPhaseToTargetGroup(self, targetGroup: TrafficLightGroup, prevStateIdx: int, currPhaseIdx: int):
        """
        The trafficlight must go through its yellow -> red -> yellow
        phases before it can go to its green phase. It does this by
        sequentially going through the trafficlights phases. But
        doing just that would mean that it may have to go through
        other groups green phases which is not desirable. This method
        returns the index of the next phase it should switch to while
        skipping over other groups green phases.
        """

        #Instead of sumo switching phases, this will pretend that it switch
        #one step too early. By doing this, the traffic light won't spend 1 step
        #in a phase it shouldn't be, before it's changed to the next good phase.
        if self.program.phases[currPhaseIdx].duration - 1 == self.timeInPhase and self.getNextPhaseIdx(currPhaseIdx) != targetGroup.getGreenPhaseIndex():
            currPhaseIdx = self.getNextPhaseIdx(currPhaseIdx)

        targetGroupLinks = targetGroup.getTLLinkIndexes()
        prevPhaseStates = self.program.phases[prevStateIdx].state
        nextPhaseIdx = currPhaseIdx
        while True:
            goodPhase = True

            #If the traffic light is currently in another groups green phase
            #then this will detect it and switch to the next phase.
            for group in self.tlGroups:
                if nextPhaseIdx == group.getGreenPhaseIndex() and group != targetGroup:
                    goodPhase = False
                    break

            if goodPhase:
                #All phases that leads up to green phases for other groups are ignored.
                for linkIdx, tlState in enumerate(self.program.phases[nextPhaseIdx].state):
                    if linkIdx in targetGroupLinks:
                        if not isFriendTLStateChangeAllowed(prevPhaseStates[linkIdx], tlState):
                            goodPhase = False
                            break
                    else:
                        if not isFoeTLStateChangeAllowed(prevPhaseStates[linkIdx], tlState):
                            goodPhase = False
                            break

            if goodPhase:
                break

            nextPhaseIdx = self.getNextPhaseIdx(nextPhaseIdx)
            if nextPhaseIdx == targetGroup.getGreenPhaseIndex():
                break

        return nextPhaseIdx

    def getNextPhaseIdx(self, phaseIdx):
        return (phaseIdx + 1) % len(self.program.phases)

    def resetPhaseRemainingTime(self, phaseIdx, sim):
        phaseDuration = self.program.phases[phaseIdx].duration
        sim.trafficlight.setPhaseDuration(self.tlID, phaseDuration)     

    def update(self, sim):
        if self.targetGroup is not None:
            if self.currPhaseIdx == self.targetGroup.greenPhaseIdx:
                self.targetGroup = None
                self.isInPrevTargetGreenPhase = True
                return

            nextPhaseIdx = self.findNextPhaseToTargetGroup(self.targetGroup, self.prevPhaseIdx, self.currPhaseIdx)
            if self.currPhaseIdx != nextPhaseIdx:
                sim.trafficlight.setPhase(self.tlID, nextPhaseIdx)

    def updateWithDataFromSumo(self, detectorData, trafficlightData):
        for group in self.tlGroups:
            group.updateLaneDetectorValues(detectorData)

        self.prevPhaseIdx = self.currPhaseIdx
        self.currPhaseIdx = trafficlightData[self.tlID][tc.TL_CURRENT_PHASE]
        self.justSwitchedPhase = self.prevPhaseIdx != self.currPhaseIdx   

        if self.justSwitchedPhase:
            self.timeInPhase = 0
        else:
            self.timeInPhase += 1  

        if self.justSwitchedPhase:
            self.isInPrevTargetGreenPhase = False

    def setGroupAsGreen(self, group: TrafficLightGroup, sim):
        if self.inGroupsGreenPhase(group):
            self.resetPhaseRemainingTime(group.greenPhaseIdx, sim)
        else:
            self.targetGroup = group

    def setGroupsGreenPhaseLength(self, group: TrafficLightGroup, phaseLength, sim):
        self.program.phases[group.greenPhaseIdx].duration = phaseLength
        sim.trafficlight.setProgramLogic(self.tlID, self.program)

    def getTrafficLightGroups(self):
        return self.tlGroups

    def getCurretPhaseIndex(self):
        return self.currPhaseIdx

    def getControlledLinks(self):
        return self.tlControlledLinks

    def phaseJustSwitched(self):
        return self.justSwitchedPhase
    
    def getTimeInCurrentPhase(self):
        return self.timeInPhase

    def inGroupsGreenPhase(self, group: TrafficLightGroup):
        return self.currPhaseIdx == group.getGreenPhaseIndex()

    def hasTarget(self):
        return self.targetGroup is not None

    def isInPrevTargetPhase(self):
        return self.isInPrevTargetGreenPhase