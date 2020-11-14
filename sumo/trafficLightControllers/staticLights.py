from trafficLightController import TrafficLightController

class ctrl(TrafficLightController):

    def __init__(self):
        super().__init__("Static")
    
    def updateLights(self, sim, ticks):
        pass