import random
from trafficLightIntersection import TrafficLightIntersection

class ctrl():

    def init(self, sim):
        # get traffic light ids for this simulation
        self.tLightIds = sim.trafficlight.getIDList()

        self.tlIntersections = []
        for tlID in self.tLightIds:
            self.tlIntersections.append(TrafficLightIntersection(tlID, sim))

    def updateLights(self, sim, ticks):
        if ticks % 50 == 0:
            for tlIntersection in self.tlIntersections:
                rngGroup = random.randint(0, len(tlIntersection.getTrafficLightGroups()) - 1)
                tlIntersection.setGroupAsGreen(tlIntersection.getTrafficLightGroups()[rngGroup], sim)

        for tlIntersection in self.tlIntersections:
            tlIntersection.update(sim)

    def getName(self):
        return "Random"