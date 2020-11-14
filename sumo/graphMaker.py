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

def createRandomMap(mapFilepath):
    exePath = os.path.join(os.environ["SUMO_HOME"], "bin", "netgenerate")
    procRes = subprocess.run([exePath, "--rand", "-o", mapFilepath, "--rand.iterations=200", "--turn-lanes", "1", "-L", "2", "-j", "traffic_light"])
    if procRes.returncode != 0:
        raise Exception("Executing netgenerate failed.")

def createLaneDetectors(mapFilepath, mapFolderPath):
    laneDetectorFilePath = os.path.join(mapFolderPath, "lanedetector.xml")
    exePath = os.path.join(os.environ["SUMO_HOME"], "tools/output", "generateTLSE3Detectors.py")
    print(exePath)
    procRes = subprocess.run(["python", exePath, "-n", mapFilepath, "-o", laneDetectorFilePath, "-l", "20"])
    if procRes.returncode != 0:
        raise Exception("Executing generateTLSE3Detectors.py failed.")

def makeRandomMap(mapSavePath, mapName):
    if not os.path.isdir(mapSavePath):
        os.mkdir(mapSavePath)
    mapFilepath = os.path.join(mapSavePath, mapName + ".net.xml")
    createRandomMap(mapFilepath)
    createLaneDetectors(mapFilepath, mapSavePath)

    #netgenerate.py
    #generateTLSE2Detectors.py
    #tlsCycleAdaptation.py
    #tlsCoordinator.py maybe?

makeRandomMap("random_map", "rng1")


makeComparisonVehicleTimeHist("random_map/rng1.net.xml", [largestQueueFirstLightCtrl.ctrl(),])





