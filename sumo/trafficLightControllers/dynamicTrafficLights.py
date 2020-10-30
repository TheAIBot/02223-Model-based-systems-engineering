class dynamicTrafficLightController():
    def init(self, sim):
        self.tLightIds = sim.trafficlight.getIDList()

    def updateLights(self, sim):

        allRed = 0
        vYellow = 1
        hYellow = 2
        vGreen = 3
        hGreen = 4

        for tLightId in self.tLightIds:
            # TRAFFIC LIGHT AND LANE DETECTOR INFORMATION:
            #
            # Every test map should comply after these rules.
            #
            # Every traffic light with id (for example "TL") must name
            # their corresponding lanearea detectors in this way.
            #
            # For the left lane detector: "TL_left", i.e. traffic light id + "_left"
            # For the right lane detector: "TL_right".
            # For the bottom lane detector: "TL_bottom".
            # For the top lane detector: "TL_top".
            #
            #
            # PHASE INFORMATION:
            #
            # Phase 0: All red (30s)
            # Phase 1: Vertical yellow (30s)
            # Phase 2: Horizontal yellow (30s)
            # Phase 3: Vertical green (30s)
            # Phase 4: Horizontal green (30s)
            #
            
            # get current traffic light phase
            curPhase = sim.trafficlight.getPhase(tLightId)

            # generate lane area dectector id's for this specific traffic light
            dectLeftId = tLightId + "_left"
            dectRightId = tLightId + "_right"
            dectTopId = tLightId + "_top"
            dectBottomId = tLightId + "_bottom"

            

        


            """
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
                    """
