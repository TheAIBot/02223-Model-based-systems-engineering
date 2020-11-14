from trafficLightController import TrafficLightController

class ctrl(TrafficLightController):

    def __init__(self):
        super().__init__("Shortest queue first")

    def updateLights(self, sim, ticks):
        for tlIntersection in self.tlIntersections:
            longestQueue = 0
            longestQueueGroup = None
            for group in tlIntersection.getTrafficLightGroups():
                queueLength = 1000000
                for laneDetectorValue in group.getLaneDetectorValues():
                    queueLength = min(queueLength, laneDetectorValue)
                
                if queueLength > longestQueue or longestQueueGroup is None:
                    longestQueue = queueLength
                    longestQueueGroup = group

            tlIntersection.setGroupAsGreen(longestQueueGroup, sim)