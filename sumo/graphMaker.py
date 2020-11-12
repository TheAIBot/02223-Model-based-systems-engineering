#!/usr/bin/env python3

import os
import matplotlib.pyplot as plt
import numpy as np

import simulator as simu
import trafficLightControllers.staticLights as staticLightCtrl
import trafficLightControllers.largestQueueFirstTLController as largestQueueFirstLightCtrl
import trafficLightControllers.shortestQueueFirstTLController as shortestQueueFirstLightCtrl
from simMeasurements import SimMeasurements

def makeVehicleTimeHist(mapGraphPath: str, mapName: str, data: SimMeasurements):
    times = []
    for veh in data.vehiclesData.values():
        times.append(veh.getTravelTime())
        
    plt.hist(times, density=True, bins=30)
        
    plt.savefig(os.path.join(mapGraphPath, "vehicle-time-hist.pdf"))


mapPath = "testMaps/1-3TL3W-Intersection/network.net.xml"
tlCtrl = staticLightCtrl.staticTrafficLightController()



mapName = os.path.basename(os.path.dirname(mapPath))
mapGraphPath = os.path.join("graphs", mapName)

if not os.path.isdir("graphs"):
    os.mkdir("graphs")

if not os.path.isdir(mapGraphPath):
    os.mkdir(mapGraphPath)

sim = simu.SumoSim(mapPath, tlCtrl)
simData = sim.run()

makeVehicleTimeHist(mapGraphPath, mapPath, simData)





