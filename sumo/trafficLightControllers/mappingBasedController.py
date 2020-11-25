from trafficLightController import TrafficLightController


class ctrl(TrafficLightController):
    intervals = [0, 5, 10, 15, 20]
    intervalsTime = [0, 40, 80, 120, 160]

    def __init__(self, config):
        super().__init__(f"Mapping", 'orange')
        self.lastChanges = {}
        self.moves = {}
        lenInter = len(ctrl.intervals)
        for i in range(lenInter):
            for j in range(lenInter):
                for k in range(len(ctrl.intervalsTime)):
                    bitIdx = k * lenInter * lenInter + j * lenInter + i
                    flag = (config >> bitIdx) & 1
                    self.moves[(i, j, k)] = flag

    def updateLights(self, sim, ticks):
        if(ticks <= 1):
            for tlIntersection in self.tlIntersections:
                self.lastChanges[tlIntersection] = ticks

        for tlIntersection in self.tlIntersections:
            groups = tlIntersection.getTrafficLightGroups()
            if len(groups) != 2:
                continue

            group1 = groups[0]
            group2 = groups[1]
            isPhase1 = tlIntersection.getCurretPhaseIndex() == group1.greenPhaseIdx
            groupA = group1 if isPhase1 else group2
            groupB = group2 if isPhase1 else group1

            waitingAM = ctrl.getMappedWaiting(groupA)
            waitingBM = ctrl.getMappedWaiting(groupB)
            timeSinceLastChangedM = self.getTimeSinceLastChangedM(
                tlIntersection, ticks)

            shouldChangePhase = self.moves[(
                waitingAM, waitingBM, timeSinceLastChangedM)]

            if shouldChangePhase == 0:
                continue

            tlIntersection.setGroupAsGreen(groupB, sim)
            self.lastChanges[tlIntersection] = ticks

    def getTimeSinceLastChangedM(self, tlIntersection, ticks):
        timeSinceLastChange = ticks - self.lastChanges[tlIntersection]
        timeSinceLastChangeMapped = 0
        for i, val in enumerate(ctrl.intervalsTime):
            if timeSinceLastChange > val:
                timeSinceLastChangeMapped = i

        return timeSinceLastChangeMapped

    def getMappedWaiting(group):
        waiting = group.getSumLaneDetectorValues()
        waitingMapped = 0
        for i, val in enumerate(ctrl.intervals):
            if waiting > val:
                waitingMapped = i

        return waitingMapped
