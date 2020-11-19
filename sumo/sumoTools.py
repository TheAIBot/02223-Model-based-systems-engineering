#!/usr/bin/env python3

import os
import subprocess
import random as rng
import xml.etree.ElementTree as xmlReader
from multiprocessing import Pool, cpu_count

def genRandomTrips(mapFilepath, routeIndex, vehicleCount, throughputMultiplier, seed = 56):
    rng.seed(seed)
    tripsStartTime = round(rng.uniform(0, 1000))
    throughputInc = 1.0 / throughputMultiplier
    tripsReleaseTime = rng.uniform(100 * throughputInc, 400 * throughputInc)
    tripsEndTime = round(tripsStartTime + tripsReleaseTime)

    arrivalRate = max(1, round((tripsEndTime - tripsStartTime) / vehicleCount))

    mapFolderPath = os.path.dirname(mapFilepath)
    tripFilepath = os.path.join(mapFolderPath, "trips" + str(routeIndex) + ".xml")
    randomTripsPath = os.path.join(os.environ["SUMO_HOME"], "tools", "randomTrips.py")
    procRes = subprocess.run(["python", randomTripsPath, "-n", mapFilepath, "--begin=" + str(tripsStartTime), "--end=" + str(tripsEndTime), "--period=" + "{0:.1f}".format(arrivalRate), "--binomial=" + str(int(max(1, throughputMultiplier))), "--seed=" + str(seed), "--fringe-factor=50", "-o",  tripFilepath])
    if procRes.returncode != 0:
        raise Exception("Executing randomTrips.py failed.")
    
    return tripFilepath

def makeTripsCompatible(tripFiles):
    """A trip files designates a trip ID for each trip starting from 0.
    Duplicate trip ID is not allowed to this method will rewrite each
    trip ID so it is unique across all the trip files."""
    tripCounter = 0
    for tripFile in tripFiles:
        tripXml = xmlReader.parse(tripFile)
        for trip in tripXml.getroot().findall("trip"):
            trip.set("id", str(tripCounter))
            tripCounter += 1

        with open(tripFile, "wb") as mapConfig:
            tripXml.write(mapConfig)

def genRoutesFromTrips(mapFilepath, tripFiles):
    makeTripsCompatible(tripFiles)

    mapFolderPath = os.path.dirname(mapFilepath)
    routeFilepath = os.path.join(mapFolderPath, "routes.xml")
    vehicleTypePath = "vehicleTypes/vehicle_type.add.xml"
    routerPath = os.path.join(os.environ["SUMO_HOME"], "bin", "duarouter")
    procRes = subprocess.run([routerPath, "-n", mapFilepath, "--route-files", ",".join(tripFiles), "--no-step-log", "--seed", "56",  "--additional-files", vehicleTypePath, "-o", routeFilepath, "--ignore-errors", "true", "--no-warnings", "true"])
    if procRes.returncode != 0:
        raise Exception("Executing duarouter failed.")
    return routeFilepath

def generateRoutes(mapFilepath, carsPerGen, genCount, throughputMultiplier):
    tripData = []
    for i in range(genCount):
        tripData.append((mapFilepath, i, carsPerGen, throughputMultiplier, rng.randint(0, 100000))) 

    with Pool(cpu_count()) as mpPool:
        tripFiles = mpPool.starmap(genRandomTrips, tripData)
    return os.path.basename(genRoutesFromTrips(mapFilepath, tripFiles))

def createRandomMap(mapFilepath):
    exePath = os.path.join(os.environ["SUMO_HOME"], "bin", "netgenerate")
    procRes = subprocess.run([exePath, "--rand", "-o", mapFilepath, "--rand.iterations=200", "--turn-lanes", "1", "-L", "2", "-j", "traffic_light"])
    if procRes.returncode != 0:
        raise Exception("Executing netgenerate failed.")

def createLaneDetectors(mapFilepath, detectorLength = 20):
    mapFolderPath = os.path.dirname(mapFilepath)
    laneDetectorFilePath = os.path.join(mapFolderPath, "lanedetector.xml")
    exePath = os.path.join(os.environ["SUMO_HOME"], "tools/output", "generateTLSE3Detectors.py")
    procRes = subprocess.run(["python", exePath, "-n", mapFilepath, "-o", laneDetectorFilePath, "-l", str(detectorLength)])
    if procRes.returncode != 0:
        raise Exception("Executing generateTLSE3Detectors.py failed.")

    laneDetectorXml = xmlReader.parse(laneDetectorFilePath)
    for detector in laneDetectorXml.getroot().findall("e3Detector"):
        detector.set("openEntry", "true")

    with open(laneDetectorFilePath, "wb") as saveFile:
            laneDetectorXml.write(saveFile)

def modifyTrafficLightPhases(mapFilepath):
    mapFolderPath = os.path.dirname(mapFilepath)
    tlPhasesFilepath = os.path.join(mapFolderPath, "trafficlightPhases.xml")
    routeFilepath = os.path.join(mapFolderPath, "routes.xml")
    exePath = os.path.join(os.environ["SUMO_HOME"], "tools", "tlsCycleAdaptation.py")
    procRes = subprocess.run(["python", exePath, "-n", mapFilepath, "-r", routeFilepath, "-o", tlPhasesFilepath])
    if procRes.returncode != 0:
        raise Exception("Executing tlsCycleAdaptation.py failed.")