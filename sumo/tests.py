#!/usr/bin/env python3

import unittest
import simulator as sim
import trafficLightControllers.staticLights as staticLightCtrl
import trafficLightControllers.largestQueueFirstTLController as largestQueueFirstLightCtrl
import trafficLightControllers.shortestQueueFirstTLController as shortestQueueFirstLightCtrl

def test_map(tester, mapPath):
    mapConfigFile = sim.createSimSumoConfigWithRandomTraffic(mapPath)

    # normal traffic lights using phase
    staticSim = sim.SumoSim(mapConfigFile, staticLightCtrl.staticTrafficLightController())
    staticTime = staticSim.run()

    # dynamic traffic lights using largest queue first algorithm
    dynamicSim = sim.SumoSim(mapConfigFile, largestQueueFirstLightCtrl.largestQueueFirstLightController())
    dynamicTime = dynamicSim.run()

    print_results(staticTime, "static")
    print_results(dynamicTime, "largest queue first")

    tester.assertTrue(staticTime.getPassengerWaitingTime() >= dynamicTime.getPassengerWaitingTime())
    tester.assertTrue(staticTime.getEmergencyWaitingTime() >= dynamicTime.getEmergencyWaitingTime())
    tester.assertEqual(0, staticTime.getCollisionsCount())
    tester.assertEqual(0, dynamicTime.getCollisionsCount())


def print_results(time, title):
    print()
    print(f"########## {title} simulation results ##########")
    print(f"Passenger vehicle waiting time: {time.getPassengerWaitingTime()}")
    print(f"Emergency vehicle waiting time: {time.getEmergencyWaitingTime()}")
    print(f"Average vehicle travel time: {time.getAverageTravelTime()}")
    print(f"HC emission (mg): {time.getEmissions()[0].getHCEmissions()}")
    print(f"##################################################")
    print()


class TestSmallMaps(unittest.TestCase):

    def test_1_1TL1W_Lane(self):
        test_map(self, "testMaps/1-1TL1W-Lane/network.net.xml")

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


if __name__ == '__main__':
    unittest.main()