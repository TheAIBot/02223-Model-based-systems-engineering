#!/usr/bin/env python3

import os
import matplotlib.pyplot as plt
import numpy as np
import subprocess
from multiprocessing import Pool, cpu_count

import sumoTools
import simulator as simu
import trafficLightControllers.staticLights as staticCtrl
import trafficLightControllers.randomTLController as randCtrl
import trafficLightControllers.largestQueueFirstTLController as lqfCtrl
import trafficLightControllers.magicController as weightlqfCtrl
import trafficLightControllers.fairPrediction as fairCtrl
from simMeasurements import SimMeasurements




def getCtrlResult(mapConfigFile, ctrl, density):
    #Train once of the controller needs it
    if ctrl.needsTrainning():
        ctrl.setTrainningRound(True)
        simu.SumoSim(mapConfigFile, ctrl, scale=density).run(takeMeasurements=False)
        ctrl.setTrainningRound(False)

    return simu.SumoSim(mapConfigFile, ctrl, scale=density).run()


def getCtrlsResults(mapPath, ctrls, densities = None):
    mapConfigFile = simu.createSimSumoConfigWithRandomTraffic(mapPath, additionalTrafficlighPhases=True)

    simsData = []
    for density in densities or [1]:
        for ctrl in ctrls:
            simsData.append((mapConfigFile, ctrl, density))

    with Pool(cpu_count()) as mpPool:
        return mpPool.starmap(getCtrlResult, simsData)
    #results = []
    #for data in simsData:
    #    results.append(getCtrlResult(data[0], data[1]))
    
    #return results


def getCtrlsDensityResults(mapPath, ctrls, trafficThroughputMultipliers):
    results = getCtrlsResults(mapPath, ctrls, densities = trafficThroughputMultipliers)
    multResults = []
    for ctrlIdx, _ in enumerate(ctrls):
        res = dict()
        for denIdx, density in enumerate(trafficThroughputMultipliers):
            res[density] = results[ctrlIdx + denIdx * len(ctrls)]
        multResults.append(res)

    return multResults


def getGraphSavePath(mapPath):
    mapName = os.path.basename(os.path.dirname(mapPath))
    mapGraphPath = os.path.join("graphs", mapName)

    if not os.path.isdir("graphs"):
        os.mkdir("graphs")

    if not os.path.isdir(mapGraphPath):
        os.mkdir(mapGraphPath)

    return mapGraphPath


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


def createLineChart(mapPath, xData, yData, colors, title, xlabel, ylabel, fileName):
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


def createHistogram(mapPath, data, dens, name, colors, title, xlabel, ylabel, fileName, corner="left"):
    plt.hist(data, density = dens, bins = 30, color = colors, label = name)

    plt.legend(loc="upper " + corner)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    mapGraphPath = getGraphSavePath(mapPath)
    plt.savefig(os.path.join(mapGraphPath, fileName))
    plt.clf()


def getVehicleHistogramData(results, dataSelector):
    histData = []
    histNames = []
    histColors = []
    for result in results:
        resultData = []
        for veh in result.vehiclesData.values():
            resultData.append(dataSelector(veh))
        histData.append(resultData)
        histNames.append(result.getControllerName())
        histColors.append(result.getGraphColor())

    return histData, histNames, histColors


def makeOverallComparisons(mapPath, results):
    histData, histNames, histColors = getVehicleHistogramData(results, lambda x: x.getTravelTime())
    createHistogram(mapPath, histData, True, 
        histNames, histColors,
        "Vehicle travel time", 
        "Time (steps)", "Density (vehicle)",
            "vehicle-travel-time.pdf", "right")

    histData, histNames, histColors = getVehicleHistogramData(results, lambda x: x.getTimeWaiting())
    createHistogram(mapPath, histData, True, 
        histNames, histColors,
        "Vehicle waiting time", 
        "Time (steps)", "Density (vehicle)",
            "vehicle-waiting-time.pdf", "right")

    histData, histNames, histColors = getVehicleHistogramData(results, lambda x: x.getEmissions().getCOEmissions())
    # NOT A DENSITY DIAGRAM (yes or no?)
    # x axis is wrong?
    createHistogram(mapPath, histData, False, 
        histNames, histColors,
        "Vehicle Carbon Monoxide (CO) emissions", 
        "CO (mg)", "Number of vehicles",
            "vehicle-CO-emissions.pdf", "right")

    histData, histNames, histColors = getVehicleHistogramData(results, lambda x: x.getEmissions().getCO2Emissions())
    # NOT A DENSITY DIAGRAM (yes or no?)
    createHistogram(mapPath, histData, False, 
        histNames, histColors,
        "Vehicle Carbon Dioxide (CO2) emissions", 
        "CO2 (mg)", "Number of vehicles",
            "vehicle-CO2-emissions.pdf", "right")

    histData, histNames, histColors = getVehicleHistogramData(results, lambda x: x.getEmissions().getHCEmissions())
    # NOT A DENSITY DIAGRAM (yes or no?)
    createHistogram(mapPath, histData, False, 
        histNames, histColors,
        "Vehicle Hydrocarbon (HC) emissions", 
        "HC (mg)", "Number of vehicles",
            "vehicle-HC-emissions.pdf", "right")

    histData, histNames, histColors = getVehicleHistogramData(results, lambda x: x.getEmissions().getPMXEmissions())
    # NOT A DENSITY DIAGRAM (yes or no?)
    createHistogram(mapPath, histData, False, 
        histNames, histColors,
        "Vehicle Particulate Matter (PM) emissions", 
        "PM (mg)", "Number of vehicles",
            "vehicle-PMx-emissions.pdf", "right")

    histData, histNames, histColors = getVehicleHistogramData(results, lambda x: x.getEmissions().getNOXEmissions())
    # NOT A DENSITY DIAGRAM (yes or no?)
    createHistogram(mapPath, histData, False, 
        histNames, histColors,
        "Vehicle Nitrogen Oxides (NOx) emissions", 
        "NOx (mg)", "Number of vehicles",
            "vehicle-NOx-emissions.pdf", "right")

    histData, histNames, histColors = getVehicleHistogramData(results, lambda x: x.getEmissions().getFuelConsumption())
    # NOT A DENSITY DIAGRAM (yes or no?)
    createHistogram(mapPath, histData, False, 
        histNames, histColors,
        "Vehicle Fuel consumption", 
        "Fuel (ml)", "Number of vehicles",
            "vehicle-fuel-emissions.pdf", "right")

    
def makeDensityComparisons(mapPath, ctrls, trafficThroughputMultipliers):
    results = getCtrlsDensityResults(mapPath, ctrls, trafficThroughputMultipliers)
    xData = tuple(trafficThroughputMultipliers)
    yData = {}
    colors = []
    
    for result in results:
        for mult in result:
            data = result[mult]
            ctrlName = data.getControllerName()
            if data.getGraphColor() not in colors:
                colors.append(data.getGraphColor())
            if ctrlName not in yData.keys():
                yData[ctrlName] = []
            print(f"Controller: {ctrlName}, Density: {mult}, Data: {data}")
            meanTravelTime = data.getAverageTravelTime()
            yData[ctrlName].append(meanTravelTime)
            
    createLineChart(mapPath, xData, yData, colors,
    "Mean travel time, traffic density", 
    "Traffic density", "Mean travel time (steps)",
    "vehicle-density-mean-travel-time.pdf")


def makeComparisonsDetectorLengths(mapPath, ctrls, detectorLengths):
    # for every detector length, run the simulation and make some graphs
    xData = tuple(detectorLengths)
    yData = {}

    results = {}
    for length in detectorLengths:
        print(f"Testing map: {mapPath} with lane detector length: {length}")
        sumoTools.createLaneDetectors(mapPath, length)
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
    
    
def makeComparisonsSmoothTravelTime(mapPath, results, vehicleInterval):
    sortedData = {}
    colors = []

    for result in results:
        name = result.getControllerName()
        colors.append(result.getGraphColor())
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

    # print(f"xData start time length: {len(xData)}")

    # for ctrl in yData:
    #     data = yData[ctrl]
    #     print(f"ctrl: {ctrl} has {len(data)} elements")
    
    createLineChart(mapPath, tuple(xData), yData, colors,
    "Mean travel time (over time)",
    "Time (steps)", "Mean travel time (steps)",
    "vehicle-smoothed-travel-time.pdf")


def makeAllComparisons(mapPath, ctrls, smoothTravelTimeVecInterval, trafficThroughputMultipliers, detectorLengths):
    results = getCtrlsResults(mapPath, ctrls)

    makeOverallComparisons(mapPath, results)
    makeComparisonsSmoothTravelTime(mapPath, results, smoothTravelTimeVecInterval)
    makeDensityComparisons(mapPath, ctrls, trafficThroughputMultipliers)
    makeComparisonsDetectorLengths(mapPath, ctrls, detectorLengths)


if __name__ == '__main__':
    mapSavePath = "random_map"
    if not os.path.isdir(mapSavePath):
        os.mkdir(mapSavePath)
    mapFilepath = os.path.join(mapSavePath, "rng1" + ".net.xml")
    sumoTools.createRandomMap(mapFilepath)
    sumoTools.createLaneDetectors(mapFilepath)

    ctrls = [staticCtrl.ctrl(), randCtrl.ctrl(), lqfCtrl.ctrl(), weightlqfCtrl.ctrl(), fairCtrl.ctrl()]
    densities = [1, 2, 3, 4, 5]
    detectorLengths = [5, 20, 50, 100, 200]

    makeAllComparisons(mapFilepath, ctrls, 25, densities, detectorLengths)


    # densities = []
    # for density in range(20, 101):
    #     densities.append(density / 20)
    # makeDensityComparisons(mapFilepath, [staticLightCtrl.ctrl(), fairPrediction.ctrl(), largestQueueFirstLightCtrl.ctrl(), magicCtrl.ctrl()], densities)