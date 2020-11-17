from trafficLightController import TrafficLightController

class ctrl(TrafficLightController):

    def __init__(self):
        super().__init__("Largest queue first")

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
                
                if queueLength > longestQueue or longestQueueGroup is None:
                    longestQueue = queueLength
                    longestQueueGroup = group

            if longestQueueGroup is not None:
                #allow the previous targetted group to have a green
                #phase that lasts for atleast 10 steps
                if tlInter.isInPrevTargetPhase() and tlInter.getTimeInCurrentPhase() < 10 and not tlInter.inGroupsGreenPhase(longestQueueGroup):
                    continue

                tlInter.setGroupAsGreen(longestQueueGroup, sim)