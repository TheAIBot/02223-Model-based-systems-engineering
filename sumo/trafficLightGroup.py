#!/usr/bin/env python3

class TrafficLightGroup():
    def __init__(self, linkIdxs, laneDetectorIDs, greenPhaseIdx):
        self.linkIDxs = linkIdxs
        self.laneDetectorIDs = laneDetectorIDs
        self.greenPhaseIdx = greenPhaseIdx

    def getLaneDetectorIDs(self):
        return self.laneDetectorIDs