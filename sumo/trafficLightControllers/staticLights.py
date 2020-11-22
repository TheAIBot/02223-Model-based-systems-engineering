from trafficLightController import TrafficLightController

class ctrl(TrafficLightController):

    def __init__(self):
        super().__init__("Static", 'c')
    
    def updateLights(self, sim, ticks):
        pass