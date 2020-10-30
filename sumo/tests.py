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
    print("static emergency: " + str(staticTime.getEmergencyWaitingTime()))
    print()
    print("dynamic passenger: " + str(dynamicTime.getPassengerWaitingTime()))
    print("dynamic emergency: " + str(dynamicTime.getEmergencyWaitingTime()))

    tester.assertTrue(staticTime.getPassengerWaitingTime() >= dynamicTime.getPassengerWaitingTime())
    tester.assertTrue(staticTime.getEmergencyWaitingTime() >= dynamicTime.getEmergencyWaitingTime())
    tester.assertEqual(0, staticTime.getCollisionsCount())
    tester.assertEqual(0, dynamicTime.getCollisionsCount())

class TestSmallMaps(unittest.TestCase):

    def test_1_1TL1W_Lane(self):
        test_map(self, "testMaps/1-1TL1W-Lane/network.net.xml")

"""
    def test_1_3TL3W_Intersection(self):
        test_map(self, "testMaps/1-3TL3W-Intersection/network.net.xml")

    def test_1_4TL4W_Intersection(self):
        test_map(self, "testMaps/1-4TL4W-Intersection/network.net.xml")

    def test_2_4TL4W_Intersection(self):
        test_map(self, "testMaps/2-4TL4W-Intersection/network.net.xml")

    def test_3_4TL4W_Intersection_2(self):
        test_map(self, "testMaps/3-4TL4W-Intersection/network.net.xml")

    def test_4_4TL4W_Intersection(self):
        test_map(self, "testMaps/4-4TL4W-Intersection/network.net.xml")

"""



if __name__ == '__main__':
    unittest.main()