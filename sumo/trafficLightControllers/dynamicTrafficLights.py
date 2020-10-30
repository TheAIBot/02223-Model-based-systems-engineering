class dynamicTrafficLightController():
    def init(self, sim):
        self.tLightIds = sim.trafficlight.getIDList()

    def updateLights(self, sim):
        for tLightId in self.tLightIds:
            phase = sim.trafficlight.getPhase(tLightId)
            if sim.lanearea.getLastStepVehicleNumber(tLightId) > 0:
                # there is a vehicle incoming from the left lane, switch to
                # yellow for a few seconds before changing to green
                if phase == 0:
                    sim.trafficlight.setPhase(tLightId, 1)
                    sim.trafficlight.setPhaseDuration(tLightId, 5.0)
                elif phase == 1:
                    sim.trafficlight.setPhase(tLightId, 2)
            else:
                # if there is no vehicles coming from the left lane,
                # switch to yellow for a few seconds, then switch to red.
                if phase == 2:
                    sim.trafficlight.setPhase(tLightId, 1)
                    sim.trafficlight.setPhaseDuration(tLightId, 5.0)
                elif phase == 1:
                    sim.trafficlight.setPhase(tLightId, 0)