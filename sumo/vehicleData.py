from vehicleEmissionsData import VehicleEmissionData

class VehicleData():
    def __init__(self, sim, vehicleID, vehicleClass, routeStartTime):
        self.vehicleID = vehicleID
        self.vehicleClass = vehicleClass
        self.routeStarted = routeStartTime
        self.routeEnded = self.routeStarted
        self.timeWaiting = 0
        self.emissions = VehicleEmissionData(self.vehicleID)
        self.emissions.subscribeToEmissions(sim)

    def updateVehicleData(self, sim, timeStep):
        self.routeEnded += 1
        self.timeWaiting = sim.vehicle.getAccumulatedWaitingTime(self.vehicleID)
        self.emissions.updateEmissions(sim, timeStep)

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