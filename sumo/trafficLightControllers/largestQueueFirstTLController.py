from trafficLightIntersection import TrafficLightIntersection

class ctrl():

    def init(self, sim):
        # get traffic light ids for this simulation
        self.tLightIds = sim.trafficlight.getIDList()

        self.tlIntersections = []
        for tlID in self.tLightIds:
            self.tlIntersections.append(TrafficLightIntersection(tlID, sim))

    def updateLights(self, sim, ticks):
        for tlIntersection in self.tlIntersections:
            longestQueue = 0
            longestQueueGroup = None
            for group in tlIntersection.getTrafficLightGroups():
                queueLength = 0
                for laneDetectorID in group.getLaneDetectorIDs():
                    queueLength = max(queueLength, sim.lanearea.getLastStepVehicleNumber(laneDetectorID))
                
                if queueLength > longestQueue or longestQueueGroup is None:
                    longestQueue = queueLength
                    longestQueueGroup = group

            tlIntersection.setGroupAsGreen(longestQueueGroup)

        for tlIntersection in self.tlIntersections:
            tlIntersection.update(sim)

    def getName(self):
        return "Largest queue first"