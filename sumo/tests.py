#!/usr/bin/env python3

import unittest
import simulator as sim
import trafficLightControllers.staticLights as staticLightCtrl
import trafficLightControllers.largestQueueFirstTLController as largestQueueFirstLightCtrl
import trafficLightControllers.shortestQueueFirstTLController as shortestQueueFirstLightCtrl
import trafficLightControllers.randomTLController as randomLightCtrl


def test_map(tester, mapPath):
    # normal traffic lights using phase
    staticSim = sim.SumoSim(mapPath, staticLightCtrl.staticTrafficLightController())
    staticTime = staticSim.run()

    # dynamic traffic lights using random green phases
    randomSim = sim.SumoSim(mapPath, randomLightCtrl.randomLightController())
    randomTime = randomSim.run()

    # dynamic traffic lights using largest queue first algorithm
    largestQueueFirstSim = sim.SumoSim(mapPath, largestQueueFirstLightCtrl.largestQueueFirstLightController())
    largestQueueFirstTime = largestQueueFirstSim.run()

    # dynamic traffic lights using shortest queue first algorithm
    shortestQueueFirstSim = sim.SumoSim(mapPath, shortestQueueFirstLightCtrl.shortestQueueFirstLightController())
    shortestQueueFirstTime = shortestQueueFirstSim.run()

    print_results(staticTime, "static")
    print_results(randomTime, "random green phase")
    print_results(largestQueueFirstTime, "largest queue first")
    print_results(shortestQueueFirstTime, "shortest queue first")

    tester.assertTrue(staticTime.getPassengerWaitingTime() >= randomTime.getPassengerWaitingTime())
    tester.assertTrue(staticTime.getEmergencyWaitingTime() >= randomTime.getEmergencyWaitingTime())

    tester.assertTrue(staticTime.getPassengerWaitingTime() >= largestQueueFirstTime.getPassengerWaitingTime())
    tester.assertTrue(staticTime.getEmergencyWaitingTime() >= largestQueueFirstTime.getEmergencyWaitingTime())

    tester.assertTrue(staticTime.getPassengerWaitingTime() >= shortestQueueFirstTime.getPassengerWaitingTime())
    tester.assertTrue(staticTime.getEmergencyWaitingTime() >= shortestQueueFirstTime.getEmergencyWaitingTime())

    tester.assertEqual(0, staticTime.getCollisionsCount())
    tester.assertEqual(0, randomTime.getCollisionsCount())
    tester.assertEqual(0, largestQueueFirstTime.getCollisionsCount())
    tester.assertEqual(0, shortestQueueFirstTime.getCollisionsCount())


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