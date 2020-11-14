from trafficLightController import TrafficLightController

class ctrl(TrafficLightController):

    def __init__(self):
        super().__init__("Largest queue first")

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