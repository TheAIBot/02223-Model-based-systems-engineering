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
        self.percent = percent

    def setTLGroup(self, group):
        self.tlGroup = group

    def getTLGroup(self):
        return self.tlGroup

def bfs(sim, startLaneID, goalLaneIDs) -> list[WeightedConnection]:
    nodesToCheck = deque()
    laneIDsFound = set()
    foundGoals = []
    foundGoalLaneIDs = set()

    nodesToCheck.append(Node(0, startLaneID, 0, 1.0))
    laneIDsFound.add(startLaneID)

    while len(nodesToCheck) > 0:
        node: Node = nodesToCheck.popleft()

        if node.laneID in goalLaneIDs:
            goalLaneID = goalLaneIDs[node.laneID]
            if goalLaneID not in foundGoalLaneIDs:
                foundGoalLaneIDs.add(goalLaneID)
                foundGoals.append(WeightedConnection(goalLaneID, node.laneID, node.timeToReach, node.percent))
            continue
        
        #list[(string approachedLane, bool hasPrio, bool isOpen, bool hasFoe, string approachedInternal, string state, string direction, float length)]
        children = sim.lane.getLinks(node.laneID, True)
        for child in children:
            childLaneID = child[0]
            if childLaneID not in laneIDsFound:
                laneIDsFound.add(childLaneID)
                
                childLaneLength = child[7]
                childLaneSpeedlimit = sim.lane.getMaxSpeed(childLaneID)
                childLaneDriveTime = childLaneLength / childLaneSpeedlimit
                nodesToCheck.append(Node(node.searchDepth + 1, childLaneID, node.timeToReach + childLaneDriveTime, node.percent / len(children)))

    return foundGoals


            

class ctrl(TrafficLightController):

    def __init__(self):
        super().__init__("magic stuff")

    def init(self, sim):
        super().init(sim)

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
                            conGroup = None
                            for endTLGroup in self.tlIDToTLInter[connection.reachedTLID].getTrafficLightGroups():
                                if connection.laneID in endTLGroup.getincommingLaneIDs():
                                    conGroup = endTLGroup
                                    break
                            if conGroup is None:
                                raise Exception("Oh no!")
                            self.tlweightConnections[tlInter.tlID].append(connection)
                            connection.setTLGroup(conGroup)
                            



    def updateLights(self, sim, ticks):
        for tlIntersection in self.tlIntersections:
            longestQueue = 0
            longestQueueGroup = None
            for group in tlIntersection.getTrafficLightGroups():
                queueLength = 0
                for laneDetectorValue in group.getLaneDetectorValues():
                    queueLength = max(queueLength, laneDetectorValue)
                
                if queueLength > longestQueue or longestQueueGroup is None:
                    longestQueue = queueLength
                    longestQueueGroup = group

            tlIntersection.setGroupAsGreen(longestQueueGroup, sim)