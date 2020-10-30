#!/usr/bin/env python3

import unittest
import simulator as sim
import trafficLightControllers.staticLights as staticLightCtrl
import trafficLightControllers.dynamicTrafficLights as dynamicLightCtrl

def test_map(tester, mapPath):
    staticSim = sim.SumoSim(mapPath, staticLightCtrl.staticTrafficLightController())
    staticTime = staticSim.run()

    dynamicSim = sim.SumoSim(mapPath, dynamicLightCtrl.dynamicTrafficLightController())
    dynamicTime = dynamicSim.run()

    print()
    print("static passenger: " + str(staticTime.getPassengerWaitingTime()))
    print("static pass co2:  " + str(staticTime.getPassengerCO2()))
    print("static emergency: " + str(staticTime.getEmergencyWaitingTime()))
    print()
    print("dynamic passenger: " + str(dynamicTime.getPassengerWaitingTime()))
    print("dynamic pass co2:  " + str(dynamicTime.getPassengerCO2()))
    print("dynamic emergency: " + str(dynamicTime.getEmergencyWaitingTime()))

    tester.assertTrue(staticTime.getPassengerWaitingTime() >= dynamicTime.getPassengerWaitingTime())
    tester.assertTrue(staticTime.getEmergencyWaitingTime() >= dynamicTime.getEmergencyWaitingTime())
    tester.assertTrue(staticTime.getPassengerCO2() >= dynamicTime.getPassengerCO2())

class TestSmallMaps(unittest.TestCase):

    def test_1_1TL1W_Lane(self):
        test_map(self, "testMaps/1-1TL1W-Lane-N/network.net.xml")

"""    def test_1_3TL3W_Intersection(self):
        test_map(self, "testMaps/1-3TL3W-Intersection/network.net.xml")

    def test_1_4TL4W_Intersection(self):
        test_map(self, "testMaps/1-4TL4W-Intersection/network.net.xml")

    def test_1_Circular_Lane(self):
        test_map(self, "testMaps/1-Circular-Lane/network.net.xml")

    def test_2_4TL4W_Intersection(self):
        test_map(self, "testMaps/2-4TL4W-Intersection/network.net.xml")

    def test_2_4TL4W_Intersection_2(self):
        test_map(self, "testMaps/2-4TL4W-Intersection-2/network.net.xml")

    def test_2_Circular_Lane(self):
        test_map(self, "testMaps/2-Circular-Lane/network.net.xml")

    def test_4_4TL4W_Intersection(self):
        test_map(self, "testMaps/4-4TL4W-Intersection/network.net.xml")

"""



if __name__ == '__main__':
    unittest.main()