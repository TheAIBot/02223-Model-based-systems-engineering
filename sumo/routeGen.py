#!/usr/bin/env python3

import os
import subprocess
import random as rng
import xml.etree.ElementTree as xmlReader

def genRandomTrips(mapFilepath, routeIndex, vehicleCount, throughputMultiplier):
    tripsStartTime = round(rng.uniform(0, 1000))
    throughputInc = 1.0 / throughputMultiplier
    tripsReleaseTime = rng.uniform(100 * throughputInc, 400 * throughputInc)
    tripsEndTime = round(tripsStartTime + tripsReleaseTime)

    arrivalRate = max(1, round((tripsEndTime - tripsStartTime) / vehicleCount))

    mapFolderPath = os.path.dirname(mapFilepath)
    tripFilepath = os.path.join(mapFolderPath, "trips" + str(routeIndex) + ".xml")
    randomTripsPath = os.path.join(os.environ["SUMO_HOME"], "tools", "randomTrips.py")
    subprocess.run(["python", randomTripsPath, "-n", mapFilepath, "--begin=" + str(tripsStartTime), "--end=" + str(tripsEndTime), "--period=" + "{0:.1f}".format(arrivalRate), "--binomial=" + str(int(max(1, throughputMultiplier))), "--seed=" + "56", "--fringe-factor=50", "-o",  tripFilepath])
    return tripFilepath


def makeTripsCompatible(tripFiles):
    """A trip files designates a trip ID for each trip starting from 0.
    Duplicate trip ID is not allowed to this method will rewrite each
    trip ID so it is unique across all the trip files."""
    tripCounter = 0
    for tripFile in tripFiles:
        tripXml = xmlReader.parse(tripFile)
        tripRoot = tripXml.getroot()
        for trip in tripRoot.findall("trip"):
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
    subprocess.run([routerPath, "-n", mapFilepath, "--route-files", ",".join(tripFiles), "--no-step-log", "--seed", "56",  "--additional-files", vehicleTypePath, "-o", routeFilepath, "--ignore-errors", "true", "--no-warnings", "true"])
    return routeFilepath

def generateRoutes(mapFilepath, carsPerGen, genCount, throughputMultiplier):
    tripFiles = []
    for i in range(genCount):
        tripFiles.append(genRandomTrips(mapFilepath, i, carsPerGen, throughputMultiplier))
    return os.path.basename(genRoutesFromTrips(mapFilepath, tripFiles))
