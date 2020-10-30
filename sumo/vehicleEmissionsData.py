class VehicleEmissionData():
    def __init__(self):
        self.hcEmissions = 0
        self.coEmissions = 0
        self.co2Emissions = 0
        self.noxEmissions = 0
        self.pmxEmissions = 0
        self.fuelConsumption = 0

    def updateEmissions(self, sim, vehicleID, timeStep):
        self.hcEmissions += sim.vehicle.getHCEmission(vehicleID) * timeStep
        self.coEmissions += sim.vehicle.getCOEmission(vehicleID) * timeStep
        self.co2Emissions += sim.vehicle.getCO2Emission(vehicleID) * timeStep
        self.noxEmissions += sim.vehicle.getNOxEmission(vehicleID) * timeStep
        self.pmxEmissions += sim.vehicle.getPMxEmission(vehicleID) * timeStep
        self.fuelConsumption += sim.vehicle.getFuelConsumption(vehicleID) * timeStep

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