from trafficLightController import TrafficLightController
from collections import deque

import os
import sys

# we need to import python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

import traci

class Node():
    def __init__(self, searchDepth, laneID, timeToReach, percent):
        self.searchDepth = searchDepth
        self.laneID = laneID
        self.timeToReach = timeToReach
        self.percent = percent

class WeightedConnection():
    def __init__(self, endDetectorID, reachedTLID, laneID, timeToReach, percent):
        self.endDetectorID = endDetectorID
        self.reachedTLID = reachedTLID
        self.laneID = laneID
        self.timeToReach = timeToReach
        self.reliabilities = deque()
        self.reliabilitySum = 0
        self.maxReliabilities = 10000

    def setTLGroupIdx(self, groupIdx):
        self.tlGroupIdx = groupIdx

    def getTLGroupIdx(self):
        return self.tlGroupIdx

    def updateReliability(self, newReliability):
        if len(self.reliabilities) == self.maxReliabilities:
            self.reliabilitySum -= self.reliabilities.popleft()
        self.reliabilities.append(newReliability)

        self.reliabilitySum += newReliability

    def getReliability(self):
        if len(self.reliabilities) == 0:
            return 0
        else:
            return self.reliabilitySum / len(self.reliabilities)

    def setStartDetectorID(self, detectorID):
        self.startDetectorID = detectorID

    def getStartDetectorID(self):
        return self.startDetectorID

    def getEndDetectorID(self):
        return self.endDetectorID



class TimedWeight():
    def __init__(self, weightCon: WeightedConnection, timeBeforeArrival, vehicleCount, weight):
        self.weightCon = weightCon
        self.expectedArrivalStart = timeBeforeArrival * 0.8
        self.expectedArrivalEnd = timeBeforeArrival * 1.6
        self.expectedArrivalTimer = 0

        self.expectedVehicles = vehicleCount
        self.newArrivedVehicles = 0

        self.timeBeforeAddWeight = max(0, int(timeBeforeArrival) - 15)
        self.weightDuration = 0
        self.weight = weight

    def update(self):
        if self.timeBeforeAddWeight > 0:
            self.timeBeforeAddWeight -= 1
        else:
            self.weightDuration -= 1

        self.expectedArrivalTimer += 1

    def updateReliability(self):
        arrivedRatio = min(1, self.newArrivedVehicles / self.expectedVehicles)
        self.weightCon.updateReliability(arrivedRatio)

    def getWeight(self):
        if self.timeBeforeAddWeight > 0:
            return 0
        else:
            return self.weight

    def isValid(self):
        return self.weightDuration > 0 or self.expectedArrivalEnd > self.expectedArrivalTimer

    def isInArrivalWindow(self):
        return self.expectedArrivalTimer > self.expectedArrivalStart and self.expectedArrivalTimer < self.expectedArrivalEnd

    def addVehiclesArrived(self, newVehiclesCount):
        self.newArrivedVehicles += newVehiclesCount

def bfs(sim, startLaneID, startTLID, incommingTLLaneIDs, detectorRoadIDToDetectorID, detectorIDToTLID):
    nodesToCheck = deque()
    laneIDsFound = set()
    foundGoals = []
    foundGoalTLIDs = set()

    nodesToCheck.append(Node(0, startLaneID, 0, 1.0))
    laneIDsFound.add(startLaneID)

    while len(nodesToCheck) > 0:
        node: Node = nodesToCheck.popleft()

        roadID = node.laneID.split("_")[0]
        if roadID in detectorRoadIDToDetectorID:
            reachedDetectorID = detectorRoadIDToDetectorID[roadID]
            reachedTLID = detectorIDToTLID[reachedDetectorID]
            if reachedTLID != startTLID:
                if reachedTLID not in foundGoalTLIDs:
                    foundGoalTLIDs.add(reachedTLID)
                    foundGoals.append(WeightedConnection(reachedDetectorID, reachedTLID, node.laneID, node.timeToReach, node.percent))
                continue

        if node.laneID in incommingTLLaneIDs:
            if incommingTLLaneIDs[node.laneID] != startTLID:
                continue
        
        #list[(string approachedLane, bool hasPrio, bool isOpen, bool hasFoe, string approachedInternal, string state, string direction, float length)]
        children = sim.lane.getLinks(node.laneID)
        for child in children:
            childLaneID = child[0]
            if childLaneID not in laneIDsFound:
                laneIDsFound.add(childLaneID)
                
                childLaneDriveTime = sim.lane.getTraveltime(node.laneID)
                nodesToCheck.append(Node(node.searchDepth + 1, childLaneID, node.timeToReach + childLaneDriveTime, node.percent / len(children)))

    return foundGoals

class ctrl(TrafficLightController):

    def __init__(self):
        super().__init__("Weight-LQF", 'r', trainFirst=True)

    def init(self, sim):
        super().init(sim)

        if not self.isTrainningRound():
            return

        self.detectorWeights = dict()
        for tlInter in self.tlIntersections:
            for group in tlInter.getTrafficLightGroups():
                for detectorID in group.getLaneDetectorIDs():
                    self.detectorWeights[detectorID] = []

        self.tlIDToTLInter = dict()
        for tlInter in self.tlIntersections:
            self.tlIDToTLInter[tlInter.tlID] = tlInter

        detectorIDToTLID = dict()
        detectorRoadIDToDetectorID = dict()
        for tlInter in self.tlIntersections:
            for group in tlInter.getTrafficLightGroups():
                for detectorID in group.getLaneDetectorIDs():
                    detectorIDToTLID[detectorID] = tlInter.tlID
                    detectorRoadID = detectorID.split("_")[2]
                    detectorRoadIDToDetectorID[detectorRoadID] = detectorID


        self.tlweightConnections = dict()
        #each itersection have some number of connections to
        #other intersections. The connections are determined
        #by using a bfs algorithm which will find nearby
        #traffic light intersections
        for tlInter in self.tlIntersections:
            self.tlweightConnections[tlInter.tlID] = dict()
            for group in tlInter.getTrafficLightGroups():
                for detectorID in group.getLaneDetectorIDs():
                    self.tlweightConnections[tlInter.tlID][detectorID] = []


        #find all the lanes that end at a traffic light
        incommingTLLaneIDs = dict()
        for tlInter in self.tlIntersections:
            for group in tlInter.getTrafficLightGroups():
                for incommingTLLaneID in group.getincommingLaneIDs():
                    incommingTLLaneIDs[incommingTLLaneID] = tlInter.tlID

        #for eahc outgoing traffic light lane, do bfs
        #to find what traffic lights it's connected to
        #and add them to the traffic lights weight
        #connections
        for tlInter in self.tlIntersections:
            for group in tlInter.getTrafficLightGroups():
                for incommingTLLaneID in group.getincommingLaneIDs():
                    connections = bfs(sim, incommingTLLaneID, tlInter.tlID, incommingTLLaneIDs, detectorRoadIDToDetectorID, detectorIDToTLID)
                    for connection in connections:
                        roadID = incommingTLLaneID.split("_")[0]
                        startDetectorID = detectorRoadIDToDetectorID[roadID]
                        connection.setStartDetectorID(startDetectorID)

                        hasConnection = False
                        for wCon in self.tlweightConnections[tlInter.tlID][startDetectorID]:
                            if wCon.getEndDetectorID() == connection.getEndDetectorID():
                                hasConnection = True
                                break
                        if not hasConnection:
                            self.tlweightConnections[tlInter.tlID][startDetectorID].append(connection)                            
                            
    def updateLights(self, sim, ticks):
        for tlInter in self.tlIntersections:
            if tlInter.hasTarget():
                continue

            longestQueue = 0
            longestQueueGroup = None
            for group in tlInter.getTrafficLightGroups():
                if tlInter.inGroupsGreenPhase(group) and tlInter.getTimeInCurrentPhase() > 50:
                    continue
                queueLength = group.getSumLaneDetectorValues()

                for detectorID in group.getLaneDetectorIDs():
                    for weight in self.detectorWeights[detectorID]:
                        queueLength += weight.getWeight()
                
                if queueLength > longestQueue or longestQueueGroup is None:
                    longestQueue = queueLength
                    longestQueueGroup = group

            if longestQueueGroup is not None:
                #allow the previous targetted group to have a green
                #phase that lasts for atleast 10 steps
                if tlInter.isInPrevTargetPhase() and tlInter.getTimeInCurrentPhase() < 10 and not tlInter.inGroupsGreenPhase(longestQueueGroup):
                    continue

                tlInter.setGroupAsGreen(longestQueueGroup, sim)

        self.updateWeights(sim)
    
    def updateWeights(self, sim):
        for tlInter in self.tlIntersections:
            for group in tlInter.getTrafficLightGroups():
                for detectorID in group.getLaneDetectorIDs():
                    for weightIdx in reversed(range(len(self.detectorWeights[detectorID]))):
                        weight = self.detectorWeights[detectorID][weightIdx]
                        if weight.isValid():
                            if weight.isInArrivalWindow():
                                weight.addVehiclesArrived(group.getDetectorLastStepNewVehiclesCount(weight.weightCon.getEndDetectorID()))
                            weight.update()
                        else:
                            if self.isTrainningRound():
                                weight.updateReliability()
                            del self.detectorWeights[detectorID][weightIdx]


        #for each traffic light, if it just switched phase
        #and if the phase is the green phase for a traffic
        #light group, then that group will send weights
        #to the traffic lights it's connected to.
        for tlInter in self.tlIntersections:
            for group in tlInter.getTrafficLightGroups():
                #only send updates from this group if this group has
                #green light
                if not tlInter.inGroupsGreenPhase(group):
                    continue

                for detectorID in group.getLaneDetectorIDs():
                    for connection in self.tlweightConnections[tlInter.tlID][detectorID]:
                        weight = group.getDetectorLastStepLeftVehiclesCount(detectorID)

                        #no need to send update if weight is 0
                        #because it won't influence the other
                        #traffic lights
                        if weight == 0:
                            continue

                        self.detectorWeights[connection.getEndDetectorID()].append(TimedWeight(connection, connection.timeToReach, weight, weight * connection.getReliability()))
