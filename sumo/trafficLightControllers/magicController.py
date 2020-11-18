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
    def __init__(self, reachedTLID, laneID, timeToReach, percent):
        self.reachedTLID = reachedTLID
        self.laneID = laneID
        self.timeToReach = timeToReach
        self.reliability = 0
        self.reliabilities = deque()
        self.reliabilitySum = 0
        self.maxReliabilities = 20
        for _ in range(self.maxReliabilities):
            self.reliabilities.append(0)

    def setTLGroupIdx(self, groupIdx):
        self.tlGroupIdx = groupIdx

    def getTLGroupIdx(self):
        return self.tlGroupIdx

    def updateReliability(self, newReliability):
        if len(self.reliabilities) == self.maxReliabilities:
            self.reliabilitySum -= self.reliabilities.popleft()
        self.reliabilities.append(newReliability)

        self.reliabilitySum += newReliability
        self.reliability = self.reliabilitySum / self.maxReliabilities
        #print(int(100 * self.reliability))

    def getReliability(self):
        return self.reliability



class TimedWeight():
    def __init__(self, weightCon: WeightedConnection, timeBeforeArrival, vehicleCount, weight):
        self.weightCon = weightCon
        self.expectedArrivalStart = timeBeforeArrival * 0.4
        self.expectedArrivalEnd = timeBeforeArrival * 1.6
        self.expectedArrivalTimer = 0

        self.expectedVehicles = vehicleCount
        self.newArrivedVehicles = 0

        self.timeBeforeAddWeight = max(0, int(timeBeforeArrival) - 10)
        self.weightDuration = 0
        self.weight = weight

    def update(self):
        if self.timeBeforeAddWeight > 0:
            self.timeBeforeAddWeight -= 1
        else:
            self.weightDuration -= 1

        self.expectedArrivalTimer += 1
        if self.expectedArrivalEnd <= self.expectedArrivalTimer:
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

def bfs(sim, startLaneID, goalLaneIDs) -> list[WeightedConnection]:
    nodesToCheck = deque()
    laneIDsFound = set()
    foundGoals = []
    foundGoalTLIDs = set()

    nodesToCheck.append(Node(0, startLaneID, 0, 1.0))
    laneIDsFound.add(startLaneID)

    while len(nodesToCheck) > 0:
        node: Node = nodesToCheck.popleft()

        if node.laneID in goalLaneIDs:
            goalTLID = goalLaneIDs[node.laneID]
            if goalTLID not in foundGoalTLIDs:
                foundGoalTLIDs.add(goalTLID)
                foundGoals.append(WeightedConnection(goalTLID, node.laneID, node.timeToReach, node.percent))
            continue
        
        #list[(string approachedLane, bool hasPrio, bool isOpen, bool hasFoe, string approachedInternal, string state, string direction, float length)]
        children = sim.lane.getLinks(node.laneID, True)
        for child in children:
            childLaneID = child[0]
            if childLaneID not in laneIDsFound:
                laneIDsFound.add(childLaneID)
                
                childLaneDriveTime = sim.lane.getTraveltime(node.laneID)
                nodesToCheck.append(Node(node.searchDepth + 1, childLaneID, node.timeToReach + childLaneDriveTime, node.percent / len(children)))

    return foundGoals

class ctrl(TrafficLightController):

    def __init__(self):
        super().__init__("magic stuff")

    def init(self, sim):
        super().init(sim)

        self.tlWeights = dict()
        for tlInter in self.tlIntersections:
            groupWeights = []
            for _ in tlInter.getTrafficLightGroups():
                groupWeights.append([])
            self.tlWeights[tlInter.tlID] = groupWeights

        self.tlIDToTLInter = dict()
        for tlInter in self.tlIntersections:
            self.tlIDToTLInter[tlInter.tlID] = tlInter

        self.tlweightConnections = dict()
        #each itersection have some number of connections to
        #other intersections. The connections are determined
        #by using a bfs algorithm which will find nearby
        #traffic light intersections
        for tlIntersection in self.tlIntersections:
            self.tlweightConnections[tlIntersection.tlID] = []

        #find all the lanes that end at a traffic light
        goalLaneIDs = dict()
        for tlInter in self.tlIntersections:
            for group in tlInter.getTrafficLightGroups():
                for incommingTLLaneID in group.getincommingLaneIDs():
                    goalLaneIDs[incommingTLLaneID] = tlInter.tlID

        #for eahc outgoing traffic light lane, do bfs
        #to find what traffic lights it's connected to
        #and add them to the traffic lights weight
        #connections
        for tlInter in self.tlIntersections:
            for group in tlInter.getTrafficLightGroups():
                for outgoingTLLaneID in group.getoutgoingLaneIDs():
                    connections = bfs(sim, outgoingTLLaneID, goalLaneIDs)
                    for connection in connections:
                        hasConnection = False
                        for wCon in self.tlweightConnections[tlInter.tlID]:
                            if wCon.reachedTLID == connection.reachedTLID:
                                hasConnection = True
                                break
                        if not hasConnection:
                            conGroupIdx = None
                            for groupIdx, endTLGroup in enumerate(self.tlIDToTLInter[connection.reachedTLID].getTrafficLightGroups()):
                                if connection.laneID in endTLGroup.getincommingLaneIDs():
                                    conGroupIdx = groupIdx
                                    break
                            if conGroupIdx is None:
                                raise Exception("Oh no!")
                            self.tlweightConnections[tlInter.tlID].append(connection)
                            connection.setTLGroupIdx(conGroupIdx)
                            
    def updateLights(self, sim, ticks):
        for tlInter in self.tlIntersections:
            if tlInter.hasTarget():
                continue

            longestQueue = 0
            longestQueueGroup = None
            for groupIdx, group in enumerate(tlInter.getTrafficLightGroups()):
                if tlInter.inGroupsGreenPhase(group) and tlInter.getTimeInCurrentPhase() > 50:
                    continue
                queueLength = group.getSumLaneDetectorValues()

                for weight in self.tlWeights[tlInter.tlID][groupIdx]:
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
            for groupIdx, group in enumerate(tlInter.getTrafficLightGroups()):
                for weightIdx in reversed(range(len(self.tlWeights[tlInter.tlID][groupIdx]))):
                    weight = self.tlWeights[tlInter.tlID][groupIdx][weightIdx]
                    if weight.isValid():
                        if weight.isInArrivalWindow():
                            weight.addVehiclesArrived(group.getLastStepNewVehiclesCount())
                        weight.update()
                    else:
                        del self.tlWeights[tlInter.tlID][groupIdx][weightIdx]


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

                #every 5 steps in green phase will send updates
                #to other traffic lights
                if tlInter.getTimeInCurrentPhase() % 5 != 0:
                    continue

                weight = group.getSumLaneDetectorValues()
                #no need to send update if weight is 0
                #because it won't influence the other
                #traffic lights
                if weight == 0:
                    continue

                for connection in self.tlweightConnections[tlInter.tlID]:
                    self.tlWeights[connection.reachedTLID][connection.getTLGroupIdx()].append(TimedWeight(connection, connection.timeToReach + 3, weight, weight * connection.getReliability()))
