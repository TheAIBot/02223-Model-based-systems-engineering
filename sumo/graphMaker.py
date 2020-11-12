#!/usr/bin/env python3

import os
import matplotlib.pyplot as plt
import numpy as np
import subprocess

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

def getCtrlsResults(mapPath, ctrls):
    mapConfigFile = simu.createSimSumoConfigWithRandomTraffic(mapPath)

    results = []
    for ctrl in ctrls:
        sSim = simu.SumoSim(mapConfigFile, ctrl)
        results.append(sSim.run())

    return results

def getGraphSavePath(mapPath):
    mapName = os.path.basename(os.path.dirname(mapPath))
    mapGraphPath = os.path.join("graphs", mapName)

    if not os.path.isdir("graphs"):
        os.mkdir("graphs")

    if not os.path.isdir(mapGraphPath):
        os.mkdir(mapGraphPath)

    return mapGraphPath

def makeComparisonVehicleTimeHist(mapPath, ctrls):
    for result in getCtrlsResults(mapPath, ctrls):
        times = []
        for veh in result.vehiclesData.values():
            times.append(veh.getTravelTime())

        plt.hist(times, density = True, bins = 30, label = result.getControllerName())

    plt.legend(loc="upper left")
    plt.title("Mean vehicle travel time histogram")
    plt.xlabel("Time in steps")

    mapGraphPath = getGraphSavePath(mapPath)
    plt.savefig(os.path.join(mapGraphPath, "cmp-vehicle-time-hist.pdf"))

def makeRandomMap(mapSavePath, mapName):
    if not os.path.isdir(mapSavePath):
        os.mkdir(mapSavePath)
    mapFilepath = os.path.join(mapSavePath, mapName)
    #netgenerate.py
    #generateTLSE2Detectors.py
    #tlsCycleAdaptation.py
    #tlsCoordinator.py maybe?


makeComparisonVehicleTimeHist("testMaps/1-3TL3W-Intersection/network.net.xml", [staticLightCtrl.ctrl(), largestQueueFirstLightCtrl.ctrl()])





