#!/usr/bin/env python3

import os
import matplotlib.pyplot as plt
import numpy as np
import subprocess
from multiprocessing import Pool, cpu_count

import sumoTools
import simulator as simu
import trafficLightControllers.staticLights as staticLightCtrl
import trafficLightControllers.largestQueueFirstTLController as largestQueueFirstLightCtrl
import trafficLightControllers.shortestQueueFirstTLController as shortestQueueFirstLightCtrl
import trafficLightControllers.magicController as magicCtrl
from simMeasurements import SimMeasurements


def getCtrlResult(mapConfigFile, ctrl):
    #Train once of the controller needs it
    if ctrl.needsTrainning():
        ctrl.setTrainningRound(True)
        simu.SumoSim(mapConfigFile, ctrl).run(takeMeasurements=False)
        ctrl.setTrainningRound(False)

    return simu.SumoSim(mapConfigFile, ctrl).run()

def getCtrlsResults(mapPath, ctrls):
    mapConfigFile = simu.createSimSumoConfigWithRandomTraffic(mapPath, additionalTrafficlighPhases=True)

    simsData = []
    for ctrl in ctrls:
        simsData.append((mapConfigFile, ctrl))

    with Pool(cpu_count()) as mpPool:
        return mpPool.starmap(getCtrlResult, simsData)
    #results = []
    #for data in simsData:
    #    results.append(getCtrlResult(data[0], data[1]))
    
    #return results


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
    plt.clf()


def getVehicleHistogramData(results, dataSelector):
    histData = []
    histNames = []
    for result in results:
        resultData = []
        for veh in result.vehiclesData.values():
            resultData.append(dataSelector(veh))
        histData.append(resultData)
        histNames.append(result.getControllerName())

    return histData, histNames


def makeComparisons(mapPath, ctrls):
    results = getCtrlsResults(mapPath, ctrls)

    histData, histNames = getVehicleHistogramData(results, lambda x: x.getTravelTime())
    createHistogram(mapPath, histData, True, 
        histNames, 
        "Vehicle travel time", 
        "Time (steps)", "Density (vehicle)",
            "vehicle-travel-time.pdf")

    histData, histNames = getVehicleHistogramData(results, lambda x: x.getEmissions().getCOEmissions())
    # NOT A DENSITY DIAGRAM (yes or no?)
    # x axis is wrong?
    createHistogram(mapPath, histData, False, 
        histNames, 
        "Vehicle Carbon Monoxide (CO) emissions", 
        "Time (steps)", "CO (mg)",
            "vehicle-CO-emissions.pdf")

    histData, histNames = getVehicleHistogramData(results, lambda x: x.getEmissions().getCO2Emissions())
    # NOT A DENSITY DIAGRAM (yes or no?)
    createHistogram(mapPath, histData, False, 
        histNames, 
        "Vehicle Carbon Dioxide (CO2) emissions", 
        "Time (steps)", "CO2 (mg)",
            "vehicle-CO2-emissions.pdf")

    histData, histNames = getVehicleHistogramData(results, lambda x: x.getEmissions().getHCEmissions())
    # NOT A DENSITY DIAGRAM (yes or no?)
    createHistogram(mapPath, histData, False, 
        histNames, 
        "Vehicle Hydrocarbon (HC) emissions", 
        "Time (steps)", "HC (mg)",
            "vehicle-HC-emissions.pdf")

    histData, histNames = getVehicleHistogramData(results, lambda x: x.getEmissions().getPMXEmissions())
    # NOT A DENSITY DIAGRAM (yes or no?)
    createHistogram(mapPath, histData, False, 
        histNames, 
        "Vehicle Particulate Matter (PM) emissions", 
        "Time (steps)", "PM (mg)",
            "vehicle-PMx-emissions.pdf")

    histData, histNames = getVehicleHistogramData(results, lambda x: x.getEmissions().getNOXEmissions())
    # NOT A DENSITY DIAGRAM (yes or no?)
    createHistogram(mapPath, histData, False, 
        histNames, 
        "Vehicle Nitrogen Oxides (NOx) emissions", 
        "Time (steps)", "NOx (mg)",
            "vehicle-NOx-emissions.pdf")

    histData, histNames = getVehicleHistogramData(results, lambda x: x.getEmissions().getFuelConsumption())
    # NOT A DENSITY DIAGRAM (yes or no?)
    createHistogram(mapPath, histData, False, 
        histNames, 
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
    bar_width = 0.20
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


def createLineChart(mapPath, xData, yData, title, xlabel, ylabel, fileName):

    colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']

    # create plot
    plt.subplots()

    for ctrlIndex, ctrlName in enumerate(yData):
        plt.plot(xData, yData[ctrlName],
        color=colors[ctrlIndex],
        label=ctrlName)
        
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
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


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def makeComparisonsSmoothTravelTime(mapPath, ctrls, vehicleInterval):
    results = getCtrlsResults(mapPath, ctrls)

    sortedData = {}

    for result in results:
        name = result.getControllerName()
        sortedData[name] = []
        for vechData in result.vehiclesData.values():
            sortedData[name].append(vechData)

    for ctrl in sortedData:
        sortedData[ctrl].sort(key=lambda x: x.routeStarted)

    xData = []
    yData = {}

    firstIteration = True

    for ctrl in sortedData:
        data = sortedData[ctrl]
        yData[ctrl] = []
        for i in range(0, len(data)):
            travelTimeSum = 0
            vecAmount = 0
            for j in range(i - vehicleInterval, i + vehicleInterval):
                if (j >= 0 and j < len(data)):
                    travelTimeSum += data[j].getTravelTime()
                    vecAmount += 1
            meanTravelTime = travelTimeSum / vecAmount
            if firstIteration:
                xData.append(data[i].routeStarted)
            yData[ctrl].append(meanTravelTime)
        firstIteration = False

    print(f"xData start time length: {len(xData)}")

    for ctrl in yData:
        data = yData[ctrl]
        print(f"ctrl: {ctrl} has {len(data)} elements")
    
    createLineChart(mapPath, tuple(xData), yData,
    "Mean travel time (over time)",
    "Time (steps)", "Mean travel time (steps)",
    "vehicle-smoothed-travel-time.pdf")

 


if __name__ == '__main__':
    mapSavePath = "random_map"
    if not os.path.isdir(mapSavePath):
        os.mkdir(mapSavePath)
    mapFilepath = os.path.join(mapSavePath, "rng1" + ".net.xml")
    sumoTools.createRandomMap(mapFilepath)
    sumoTools.createLaneDetectors(mapFilepath)

    makeComparisonsSmoothTravelTime(mapFilepath, [staticLightCtrl.ctrl(), largestQueueFirstLightCtrl.ctrl(), magicCtrl.ctrl()], 25)
    
    #makeComparisonsDetectorLengths(mapFilepath, [staticLightCtrl.ctrl(), largestQueueFirstLightCtrl.ctrl()], [5, 10, 20, 50, 100, 150, 200])
    #makeComparisons("random_map/rng1.net.xml", [largestQueueFirstLightCtrl.ctrl(), magicCtrl.ctrl()])
    #makeComparisons("testMaps/1-3TL3W-Intersection/network.net.xml", [staticLightCtrl.ctrl(), largestQueueFirstLightCtrl.ctrl()])
    #makeDensityComparisons("testMaps/1-3TL3W-Intersection/network.net.xml", [staticLightCtrl.ctrl(), largestQueueFirstLightCtrl.ctrl(), magicCtrl.ctrl()], [1, 2, 3, 4, 5])
