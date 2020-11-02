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

            detectors = sim.lanearea.getIDList()

            # loop through all of the registered lane detectors,
            # find out which lane that has the greatest amount of cars
            mostTrafficDetector = ""
            mostTrafficNum = 0
            trafficCount = 0
            for detectorId in detectors:
                vechNum = sim.lanearea.getLastStepVehicleNumber(detectorId)
                if vechNum > 0:
                    trafficCount += 1
                    if vechNum > mostTrafficNum:
                        mostTrafficNum = vechNum
                        mostTrafficDetector = detectorId

            if trafficCount == 0:
                if curPhase == hGreen:
                    sim.trafficlight.setPhase(tLightId, hYellow)
                elif curPhase == vGreen: 
                    sim.trafficlight.setPhase(tLightId, vYellow)
                else:
                    sim.trafficlight.setPhase(tLightId, allRed)
                return

            if mostTrafficDetector != "":
                print(f"Most traffic: {mostTrafficDetector}, Number: {mostTrafficNum}")
                if mostTrafficDetector == dectLeftId or mostTrafficDetector == dectRightId:
                    if curPhase == allRed:
                        sim.trafficlight.setPhase(tLightId, hYellow)
                    else:
                        sim.trafficlight.setPhase(tLightId, hGreen)
                elif mostTrafficDetector == dectTopId or mostTrafficDetector == dectBottomId:
                    if curPhase == allRed:
                        sim.trafficlight.setPhase(tLightId, vYellow)
                    else:
                        sim.trafficlight.setPhase(tLightId, vGreen)
                mostTrafficDetector = ""