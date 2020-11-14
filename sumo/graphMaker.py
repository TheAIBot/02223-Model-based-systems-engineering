#!/usr/bin/env python3

import os
import matplotlib.pyplot as plt
import numpy as np
import subprocess

import sumoTools
import simulator as simu
import trafficLightControllers.staticLights as staticLightCtrl
import trafficLightControllers.largestQueueFirstTLController as largestQueueFirstLightCtrl
import trafficLightControllers.shortestQueueFirstTLController as shortestQueueFirstLightCtrl
from simMeasurements import SimMeasurements


def getCtrlsResults(mapPath, ctrls):
    mapConfigFile = simu.createSimSumoConfigWithRandomTraffic(mapPath, additionalTrafficlighPhases=True)

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
    "Mean travel time, traffic density", 
    "Traffic density", "Mean travel time (steps)",
    "vehicle-density-mean-travel-time.pdf")

 
def createBarChart(mapPath, xData, yData, title, xlabel, ylabel, fileName):

    colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']

    n_groups = len(xData)

    # create plot
    plt.subplots()
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


def makeComparisonsDetectorLengths(mapPath, ctrls, detectorLengths):
    # for every detector length, run the simulation and make some graphs
    xData = tuple(detectorLengths)
    yData = {}

    results = {}
    for length in detectorLengths:
        print(f"Testing map: {mapPath} with lane detector length: {length}")
        sumoTools.createLaneDetectors(mapFilepath, length)
        results[length] = getCtrlsResults(mapPath, ctrls)

    for length in results:
        result = results[length]
        for ctrlResult in result:
            ctrlName = ctrlResult.getControllerName()
            print(f"ctrl: {ctrlName}, length: {length}")
            if ctrlName not in yData.keys():
                yData[ctrlName] = []
            meanTravelTime = ctrlResult.getAverageTravelTime()
            yData[ctrlName].append(meanTravelTime)

    createBarChart(mapPath, xData, yData,
    "Mean travel time, lane detector length", 
    "Lane detector length (m)", "Mean travel time (steps)",
    "vehicle-lane-detector-length-mean-travel-time.pdf")


mapSavePath = "random_map"
if not os.path.isdir(mapSavePath):
    os.mkdir(mapSavePath)
mapFilepath = os.path.join(mapSavePath, "rng1" + ".net.xml")
sumoTools.createRandomMap(mapFilepath)
sumoTools.createLaneDetectors(mapFilepath)
sumoTools.modifyTrafficLightPhases(mapFilepath)


makeComparisonsDetectorLengths(mapFilepath, [staticLightCtrl.ctrl(), largestQueueFirstLightCtrl.ctrl()], [5, 10, 20, 50, 100, 150, 200])


#makeComparisons("random_map/rng1.net.xml", [staticLightCtrl.ctrl(), largestQueueFirstLightCtrl.ctrl()])
#makeComparisons("testMaps/1-3TL3W-Intersection/network.net.xml", [staticLightCtrl.ctrl(), largestQueueFirstLightCtrl.ctrl()])
#makeDensityComparisons("testMaps/1-3TL3W-Intersection/network.net.xml", [staticLightCtrl.ctrl(), largestQueueFirstLightCtrl.ctrl()], [0.05, 0.10, 0.15, 0.20, 0.25])
