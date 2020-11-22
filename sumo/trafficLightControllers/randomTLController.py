import random
from trafficLightController import TrafficLightController

class ctrl(TrafficLightController):

    def __init__(self):
        super().__init__("Random", 'm')

    def updateLights(self, sim, ticks):
        if ticks % 50 == 0:
            for tlIntersection in self.tlIntersections:
                rngGroup = random.randint(0, len(tlIntersection.getTrafficLightGroups()) - 1)
                tlIntersection.setGroupAsGreen(tlIntersection.getTrafficLightGroups()[rngGroup], sim)