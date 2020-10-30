from vehicleData import VehicleData

class SimMeasurements():
    def __init__(self, timestep):
        self.timeStep = timestep
        self.time = 0
        self.vehiclesData = dict()

    def update(self, sim):
        for vehicleID in sim.vehicle.getIDList():
            if vehicleID not in self.vehiclesData:
                vehicleClass = sim.vehicle.getVehicleClass(vehicleID)
                self.vehiclesData[vehicleID] = VehicleData(vehicleID, vehicleClass, self.time)
            
            self.vehiclesData[vehicleID].updateVehicleData(sim, self.timeStep)
        self.time += 1

    def getPassengerWaitingTime(self):
        passengerSum = 0
        for v in self.vehiclesData.values():
            if v.getVehicleClass() == "passenger":
                passengerSum += v.getTimeWaiting()
        return passengerSum

    def getEmissions(self):
        return [v.getEmissions() for v in self.vehiclesData.values()]

    def getEmergencyWaitingTime(self):
        emergencySum = 0
        for v in self.vehiclesData.values():
            if v.getVehicleClass() == "emergency":
                emergencySum += v.getTimeWaiting()
        return emergencySum

    def getVehicleCount(self):
        return len(self.vehiclesData)

    def getTotalRuntime(self):
        return self.time