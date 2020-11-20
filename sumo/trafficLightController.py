#!/usr/bin/env python3
from abc import ABC, abstractmethod
from trafficLightIntersection import TrafficLightIntersection

class TrafficLightController(ABC):
    def __init__(self, name, graphColor, trainFirst = False):
        self.name = name
        self.trainFirst = trainFirst
        self.graphColor = graphColor
        self.trainningRound = False

    def init(self, sim):  
        # get traffic light ids for this simulation
        self.tLightIds = sim.trafficlight.getIDList()

        self.tlIntersections = []
        for tlID in self.tLightIds:
            tl = TrafficLightIntersection(tlID, sim)
            if len(tl.getTrafficLightGroups()) > 0:
                self.tlIntersections.append(tl)

    def update(self, sim, ticks):
        #update trafficlights with sumo data
        laneDetectorData = sim.multientryexit.getAllSubscriptionResults()
        trafficlightData = sim.trafficlight.getAllSubscriptionResults()
        for tlIntersection in self.tlIntersections:
            tlIntersection.updateWithDataFromSumo(laneDetectorData, trafficlightData)

        #now controller algorithm can run with updated information
        self.updateLights(sim, ticks)

        #update the intersections so they can do what the
        #controller algorithm asked them to do
        for tlIntersection in self.tlIntersections:
            tlIntersection.update(sim)

    @abstractmethod
    def updateLights(self, sim, ticks):
        pass

    def getName(self):
        return self.name

    def needsTrainning(self):
        return self.trainFirst

    def setTrainningRound(self, train):
        self.trainningRound = train 

    def isTrainningRound(self):
        return self.trainningRound

    def getGraphColor(self):
        return self.graphColor
