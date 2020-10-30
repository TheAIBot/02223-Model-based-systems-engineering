from __future__ import absolute_import
from __future__ import print_function

import os
import sys
import optparse
import random
import pathlib as Path

import routeGen

# we need to import python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

from sumolib import checkBinary  # noqa
import traci  # noqa

class SimMeasurements():
    def __init__(self, timestep):
        self.timeStep = timestep
        self.passengerWaits = dict()
        self.passengerCO2s = dict()
        self.emergencyWaits = dict()

    def update(self, sim):
        for vehicleID in traci.vehicle.getIDList():
            vehicleClass = traci.vehicle.getVehicleClass(vehicleID)
            if vehicleClass == "passenger":
                self.passengerWaits[vehicleID] = traci.vehicle.getAccumulatedWaitingTime(vehicleID)
                self.passengerCO2s[vehicleID] = traci.vehicle.getCO2Emission(vehicleID) * self.timeStep
            elif vehicleClass == "emergency":
                self.emergencyWaits[vehicleID] = traci.vehicle.getAccumulatedWaitingTime(vehicleID)

    def getPassengerWaitingTime(self):
        passengerSum = 0
        for k, v in self.passengerWaits.items():
            passengerSum += v
        return passengerSum

    def getPassengerCO2(self):
        passengerSum = 0
        for k, v in self.passengerCO2s.items():
            passengerSum += v
        return passengerSum


    def getEmergencyWaitingTime(self):
        emergencySum = 0
        for k, v in self.emergencyWaits.items():
            emergencySum += v
        return emergencySum

class SumoSim():

    def __init__(self, mapFilepath, trafficLightController):
        self.tlCtrl = trafficLightController

        routesFilepath = routeGen.gen_random_routes(mapFilepath, 50)

        mapFolder = os.path.dirname(mapFilepath)
        mapName = Path.Path(mapFilepath).stem
        mapConfigFilepath = os.path.join(mapFolder, mapName + ".sumocfg")
        with open(mapConfigFilepath, "w") as mapConfig:
            print("<configuration>", file=mapConfig)
            print("    <input>", file=mapConfig)
            print("        <net-file value=\"{}\"/>".format(os.path.basename(mapFilepath)), file=mapConfig)
            print("        <route-files value=\"{}\"/>".format(os.path.basename(routesFilepath)), file=mapConfig)
            print("        <additional-files value=\"{}\"/>".format("lanedetector.xml"), file=mapConfig)
            print("    </input>", file=mapConfig)
            print("</configuration>", file=mapConfig)

        traci.start([checkBinary('sumo'), "-c", mapConfigFilepath, "--device.emissions.probability", "1", "--tripinfo-output", "tripinfo.xml", "--waiting-time-memory", "100000"])
        trafficLightController.init(traci)

    def run(self):
        measurements = SimMeasurements(1)

        ticks = 0
        while traci.simulation.getMinExpectedNumber() > 0:
            self.tlCtrl.updateLights(traci)

            measurements.update(traci)

            traci.simulationStep()
            ticks += 1

        traci.close()
        sys.stdout.flush()

        return measurements