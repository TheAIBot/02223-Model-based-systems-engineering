import os
import sys

# we need to import python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

import traci.constants as tc

class VehicleEmissionData():
    def __init__(self, vehicleID):
        self.vehicleID = vehicleID
        self.hcEmissions = 0
        self.coEmissions = 0
        self.co2Emissions = 0
        self.noxEmissions = 0
        self.pmxEmissions = 0
        self.fuelConsumption = 0

    def getSubscriptions(self):
        return (tc.VAR_HCEMISSION, tc.VAR_COEMISSION, tc.VAR_CO2EMISSION, tc.VAR_NOXEMISSION, tc.VAR_PMXEMISSION, tc.VAR_FUELCONSUMPTION)

    def updateEmissions(self, sim, subscribedData, timeStep):
        self.hcEmissions += subscribedData[tc.VAR_HCEMISSION] * timeStep
        self.coEmissions += subscribedData[tc.VAR_COEMISSION] * timeStep
        self.co2Emissions += subscribedData[tc.VAR_CO2EMISSION] * timeStep
        self.noxEmissions += subscribedData[tc.VAR_NOXEMISSION] * timeStep
        self.pmxEmissions += subscribedData[tc.VAR_PMXEMISSION] * timeStep
        self.fuelConsumption += subscribedData[tc.VAR_FUELCONSUMPTION] * timeStep

    def getHCEmissions(self):
        return self.hcEmissions

    def getCOEmissions(self):
        return self.coEmissions

    def getCO2Emissions(self):
        return self.co2Emissions

    def getNOXEmissions(self):
        return self.noxEmissions

    def getPMXEmissions(self):
        return self.pmxEmissions

    def getFuelConsumption(self):
        return self.fuelConsumption