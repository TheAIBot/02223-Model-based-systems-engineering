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
# Total phase time: 140s
#
# Phase 0: vertical green,  horizontal red    (40s) (defualt, i.e. resting in vertical lane)
# Phase 1: vertical yellow, horizontal red    (10s)
# Phase 2: vertical red,    horizontal red    (10s) (all red period to clear intersection)
# Phase 3: vertical red,    horizontal orange (10s)
# Phase 4: vertical red,    horizontal green  (40s)
# Phase 5: vertical red,    horizontal yellow (10s)
# Phase 6: vertical red,    horizontal red    (10s) (all red period to clear intersection)
# Phase 7: vertical orange, horizontal red    (10s)
#

class shortestQueueFirstLightController():

    def init(self, sim):
        self.phase_vGreen_hRed  = 0 # default, i.e. resting in vertical lane green
        self.phase_vYellow_hRed = 1
        self.phase_vRed_hRed_1  = 2
        self.phase_vRed_hOrange = 3
        self.phase_vRed_hGreen  = 4
        self.phase_vRed_hYellow = 5
        self.phase_vRed_hRed_2  = 6
        self.phase_vOrange_hRed = 7

        # get traffic light ids for this simulation
        self.tLightIds = sim.trafficlight.getIDList()

        # set the default phase, just to be sure
        for tLightId in self.tLightIds:
            sim.trafficlight.setPhase(tLightId, self.phase_vGreen_hRed)

    def updateLights(self, sim):
        for tLightId in self.tLightIds:

            # get current traffic light phase
            curPhase = sim.trafficlight.getPhase(tLightId)
            curPhaseStr = ""

            if curPhase == 0:
                curPhaseStr = "phase_vGreen_hRed"
            elif curPhase == 1:
                curPhaseStr = "phase_vYellow_hRed"
            elif curPhase == 2:
                curPhaseStr = "phase_vRed_hRed_1"
            elif curPhase == 3:
                curPhaseStr = "phase_vRed_hOrange"
            elif curPhase == 4:
                curPhaseStr = "phase_vRed_hGreen"
            elif curPhase == 5:
                curPhaseStr = "phase_vRed_hYellow"
            elif curPhase == 6:
                curPhaseStr = "phase_vRed_hRed_2"
            elif curPhase == 7:
                curPhaseStr = "phase_vOrange_hRed"

            # generate lane area dectector id's for this specific traffic light
            dectLeftId = tLightId + "_left"
            dectRightId = tLightId + "_right"
            dectTopId = tLightId + "_top"
            dectBottomId = tLightId + "_bottom"

            # get all detector id's in the simulation
            detectors = sim.lanearea.getIDList()

            # loop through all of the registered lane detectors,
            # find out which lane that has the least amount of traffic on it.
            # If none we just take the left as a defualt.
            leastTrafficDetector = dectLeftId
            leastTrafficNum = 100

            for detectorId in detectors:
                vechNum = sim.lanearea.getLastStepVehicleNumber(detectorId)
                if vechNum > 0 and vechNum < leastTrafficNum:
                    leastTrafficDetector = detectorId
                    leastTrafficNum = vechNum
                
            #print(f"Least trafficated detector: {leastTrafficDetector}, Vehicles on detector: {leastTrafficNum}, Current phase: " + curPhaseStr)

            if leastTrafficDetector == dectTopId or leastTrafficDetector == dectBottomId:
                # prioritize vertical traffic
                if curPhase == self.phase_vGreen_hRed:    # if we are already green, make sure we stay green
                    sim.trafficlight.setPhase(tLightId, self.phase_vGreen_hRed) 
                elif curPhase == self.phase_vYellow_hRed: # if we are yellow, change to all red
                    sim.trafficlight.setPhase(tLightId, self.phase_vRed_hRed_1)
                elif curPhase == self.phase_vRed_hRed_1 or curPhase == self.phase_vRed_hRed_2: # if we are all red, change to orange vertical phase
                    sim.trafficlight.setPhase(tLightId, self.phase_vOrange_hRed)
                elif curPhase == self.phase_vRed_hOrange: # if horizontal traffic is orange, make it go green quick
                    sim.trafficlight.setPhase(tLightId, self.phase_vRed_hGreen)
                elif curPhase == self.phase_vRed_hGreen:  # if horizontal traffic is green, make it go yellow quick
                    sim.trafficlight.setPhase(tLightId, self.phase_vRed_hYellow)
                elif curPhase == self.phase_vRed_hYellow: # if horizontal traffic is yellow, make it go red quick
                    sim.trafficlight.setPhase(tLightId, self.phase_vRed_hRed_2)
                elif curPhase == self.phase_vOrange_hRed: # if vertical is orange, go to green quick
                    sim.trafficlight.setPhase(tLightId, self.phase_vGreen_hRed)
            elif leastTrafficDetector == dectLeftId or leastTrafficDetector == dectRightId:
                # prioritize horizontal traffic
                if curPhase == self.phase_vGreen_hRed:    # If vertical is green, make it go yellow quick
                    sim.trafficlight.setPhase(tLightId, self.phase_vYellow_hRed)
                elif curPhase == self.phase_vYellow_hRed: # If vertical is yellow, make it go red quick
                    sim.trafficlight.setPhase(tLightId, self.phase_vRed_hRed_1)
                elif curPhase == self.phase_vRed_hRed_1 or curPhase == self.phase_vRed_hRed_2: # if we are all red, change to orange horizontal phase
                    sim.trafficlight.setPhase(tLightId, self.phase_vRed_hOrange)
                elif curPhase == self.phase_vRed_hOrange: # if horizontal orange phase, go green quick
                    sim.trafficlight.setPhase(tLightId, self.phase_vRed_hGreen)
                elif curPhase == self.phase_vRed_hGreen:  # if horizontal green phase, stay green
                    sim.trafficlight.setPhase(tLightId, self.phase_vRed_hGreen)
                elif curPhase == self.phase_vRed_hYellow: # if horizontal yellow phase, change to all red
                    sim.trafficlight.setPhase(tLightId, self.phase_vRed_hRed_2)
                elif curPhase == self.phase_vOrange_hRed: # if vertical orange phase, make it go green quick
                    sim.trafficlight.setPhase(tLightId, self.phase_vGreen_hRed)