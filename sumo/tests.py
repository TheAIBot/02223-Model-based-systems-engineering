#!/usr/bin/env python3

import unittest
import sumoTools
import simulator as sim
from trafficLightControllers import *

modules = {
    # normal traffic lights using phase
    "static": staticLights,

    # dynamic traffic lights using random green phases
    "random": randomTLController,

    # dynamic traffic lights using largest queue first algorithm
    "lqf": largestQueueFirstTLController,

    # dynamic traffic lights using shortest queue first algorithm
    "sqf": shortestQueueFirstTLController,
}

friendly = {
    "random": "random green phase",
    "lqf": "largest queue first",
    "sqf": "shortest queue first",
}

def test_map(tester, mapPath):
    sumoTools.createLaneDetectors(mapPath)
    mapConfigFile = sim.createSimSumoConfigWithRandomTraffic(mapPath)

    results = {}
    for name, module in modules.items():
        result = sim.SumoSim(mapConfigFile, module.ctrl()).run()
        results[name] = result
        

    for name, result in results.items():
        print_results(result, friendly.get(name, name))

    # The two loops are separated to ensure that results are always printed.

    for name, result in results.items():
        tester.assertEqual(
            0,
            result.getCollisionsCount(),
            f"{name} has collisions in {mapPath}"
        )
        tester.assertGreaterEqual(
            results["static"].getPassengerWaitingTime(),
            result.getPassengerWaitingTime(),
            f"{name} is slower than static for passengers in {mapPath}"
        )
        tester.assertGreaterEqual(
            results["static"].getEmergencyWaitingTime(),
            result.getEmergencyWaitingTime(),
            f"{name} is slower than static for emergency in {mapPath}"
        )

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
    
    def test_4_4TL4W_Intersection_large(self):
        test_map(self, "testMaps/4-4TL4W-Intersection-LARGE/network.net.xml")



if __name__ == '__main__':
    unittest.main()