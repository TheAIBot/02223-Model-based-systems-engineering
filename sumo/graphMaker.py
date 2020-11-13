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


def getCtrlsResults(mapPath, ctrls):
    mapConfigFile = simu.createSimSumoConfigWithRandomTraffic(mapPath)

    results = []
    for ctrl in ctrls:
        sSim = simu.SumoSim(mapConfigFile, ctrl)
        results.append(sSim.run())

    return results


def getCtrlsDensityResults(mapPath, ctrls, trafficThroughputMultipliers):
    results = []
    mapConfigs = {}

    for mult in trafficThroughputMultipliers:
        print(f"Generating map with trafficThroughputMultiplier: {mult}")
        mapConfigs[mult] = simu.createSimSumoConfigWithRandomTraffic(mapPath, mult)

    for ctrl in ctrls:
        multResults = {}
        for mult in trafficThroughputMultipliers:
            print(f"Testing controller: {ctrl.getName()}, with trafficThroughputMultiplier: {mult}")
            mapConfigFile = mapConfigs[mult]
            sSim = simu.SumoSim(mapConfigFile, ctrl)
            multResults[mult] = sSim.run()
        results.append(multResults)

    return results


def getGraphSavePath(mapPath):
    mapName = os.path.basename(os.path.dirname(mapPath))
    mapGraphPath = os.path.join("graphs", mapName)

    if not os.path.isdir("graphs"):
        os.mkdir("graphs")

    if not os.path.isdir(mapGraphPath):
        os.mkdir(mapGraphPath)

    return mapGraphPath


def createHistogram(mapPath, data, dens, name, title, xlabel, ylabel, fileName):
    plt.hist(data, density = dens, bins = 30, label = name)

    plt.legend(loc="upper left")
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    mapGraphPath = getGraphSavePath(mapPath)
    plt.savefig(os.path.join(mapGraphPath, fileName))


def makeComparisons(mapPath, ctrls):
    results = getCtrlsResults(mapPath, ctrls)

    for result in results:
        travelTimes = []
        for veh in result.vehiclesData.values():
            travelTimes.append(veh.getTravelTime())

        createHistogram(mapPath, travelTimes, True, 
        result.getControllerName(), 
        "Vehicle travel time", 
        "Time (steps)", "Density (vehicle)",
         "vehicle-travel-time.pdf")

    plt.clf()

    for result in results:
        CO = []
        for veh in result.vehiclesData.values():
            CO.append(veh.getEmissions().getCOEmissions())

        # NOT A DENSITY DIAGRAM (yes or no?)
        createHistogram(mapPath, CO, False, 
        result.getControllerName(), 
        "Vehicle Carbon Monoxide (CO) emissions", 
        "Time (steps)", "CO (mg)",
         "vehicle-CO-emissions.pdf")

    plt.clf()

    for result in results:
        CO2 = []
        for veh in result.vehiclesData.values():
            CO2.append(veh.getEmissions().getCO2Emissions())

        # NOT A DENSITY DIAGRAM (yes or no?)
        createHistogram(mapPath, CO2, False, 
        result.getControllerName(), 
        "Vehicle Carbon Dioxide (CO2) emissions", 
        "Time (steps)", "CO2 (mg)",
         "vehicle-CO2-emissions.pdf")

    plt.clf()

    for result in results:
        HC = []
        for veh in result.vehiclesData.values():
            HC.append(veh.getEmissions().getHCEmissions())

        # NOT A DENSITY DIAGRAM (yes or no?)
        createHistogram(mapPath, HC, False, 
        result.getControllerName(), 
        "Vehicle Hydrocarbon (HC) emissions", 
        "Time (steps)", "HC (mg)",
         "vehicle-HC-emissions.pdf")

    plt.clf()

    for result in results:
        PMx = []
        for veh in result.vehiclesData.values():
            PMx.append(veh.getEmissions().getPMXEmissions())

        # NOT A DENSITY DIAGRAM (yes or no?)
        createHistogram(mapPath, PMx, False, 
        result.getControllerName(), 
        "Vehicle Particulate Matter (PM) emissions", 
        "Time (steps)", "PM (mg)",
         "vehicle-PMx-emissions.pdf")

    plt.clf()

    for result in results:
        NOx = []
        for veh in result.vehiclesData.values():
            NOx.append(veh.getEmissions().getNOXEmissions())

        # NOT A DENSITY DIAGRAM (yes or no?)
        createHistogram(mapPath, NOx, False, 
        result.getControllerName(), 
        "Vehicle Nitrogen Oxides (NOx) emissions", 
        "Time (steps)", "NOx (mg)",
         "vehicle-NOx-emissions.pdf")

    plt.clf()

    for result in results:
        fuel = []
        for veh in result.vehiclesData.values():
            fuel.append(veh.getEmissions().getFuelConsumption())

        # NOT A DENSITY DIAGRAM (yes or no?)
        createHistogram(mapPath, fuel, False, 
        result.getControllerName(), 
        "Vehicle Fuel consumption", 
        "Time (steps)", "Fuel (ml)",
         "vehicle-fuel-emissions.pdf")


def makeDensityComparisons(mapPath, ctrls, trafficThroughputMultipliers):
    results = getCtrlsDensityResults(mapPath, ctrls, trafficThroughputMultipliers)
    xData = tuple(trafficThroughputMultipliers)
    yData = {}
    
    for result in results:
        for mult in result:
            data = result[mult]
            ctrlName = data.getControllerName()
            if ctrlName not in yData.keys():
                yData[ctrlName] = []
            print(f"Controller: {ctrlName}, Density: {mult}, Data: {data}")
            meanTravelTime = data.getAverageTravelTime()
            yData[ctrlName].append(meanTravelTime)
            
    createBarChart(mapPath, xData, yData, 
    data.getControllerName(),
    "Mean travel time, traffic density", 
    "Traffic density", "Mean travel time (steps)",
    "vehicle-density-mean-travel-time.pdf")

 
def createBarChart(mapPath, xData, yData, name, title, xlabel, ylabel, fileName):
    for x in xData:
        print(f"x data value: {x}")

    for ctrlName in yData:
        mults = yData[ctrlName]
        for i in range(len(mults)):
            mult = xData[i]
            meanTravel = mults[i]
            print(f"Controller: {ctrlName}, mult: {mult}, mean travel: {meanTravel}")

    colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']

    n_groups = len(xData)

    # create plot
    fig, ax = plt.subplots()
    index = np.arange(n_groups)
    bar_width = 0.35
    opacity = 0.8

    ctrlIndex = 0
    for ctrlName in yData:
        plt.bar(index + ctrlIndex * bar_width, tuple(yData[ctrlName]), bar_width,
        alpha=opacity,
        color=colors[ctrlIndex],
        label=ctrlName)
        ctrlIndex += 1
        
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.xticks(index + bar_width, xData)
    plt.legend()

    plt.tight_layout()

    mapGraphPath = getGraphSavePath(mapPath)
    plt.savefig(os.path.join(mapGraphPath, fileName))


def makeRandomMap(mapSavePath, mapName):
    if not os.path.isdir(mapSavePath):
        os.mkdir(mapSavePath)
    mapFilepath = os.path.join(mapSavePath, mapName)
    #netgenerate.py
    #generateTLSE2Detectors.py
    #tlsCycleAdaptation.py
    #tlsCoordinator.py maybe?


makeComparisons("testMaps/1-3TL3W-Intersection/network.net.xml", [staticLightCtrl.ctrl(), largestQueueFirstLightCtrl.ctrl()])
makeDensityComparisons("testMaps/1-3TL3W-Intersection/network.net.xml", [staticLightCtrl.ctrl(), largestQueueFirstLightCtrl.ctrl()], [0.05, 0.10, 0.20, 0.25])