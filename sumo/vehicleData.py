from vehicleEmissionsData import VehicleEmissionData

import os
import sys

# we need to import python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

import traci.constants as tc

class VehicleData():
    def __init__(self, sim, vehicleID, vehicleClass, routeStartTime):
        self.vehicleID = vehicleID
        self.vehicleClass = vehicleClass
        self.routeStarted = routeStartTime
        self.routeEnded = self.routeStarted
        self.timeWaiting = 0
        self.emissions = VehicleEmissionData(self.vehicleID)

        sim.vehicle.subscribe(self.vehicleID, self.getSubscriptions() + self.emissions.getSubscriptions())

    def getSubscriptions(self):
        return (tc.VAR_ACCUMULATED_WAITING_TIME,)

    def updateVehicleData(self, sim, subscribedData, timeStep):
        self.routeEnded += 1
        self.timeWaiting = subscribedData[tc.VAR_ACCUMULATED_WAITING_TIME]
        self.emissions.updateEmissions(sim, subscribedData, timeStep)

    def getVehicleClass(self):
        return self.vehicleClass

    def getRouteStarted(self):
        return self.routeStarted
    
    def getRouteEnded(self):
        return self.routeEnded

    def getTravelTime(self):
        return self.routeEnded - self.routeStarted

    def getTimeWaiting(self):
        return self.timeWaiting

    def getEmissions(self):
        return self.emissions