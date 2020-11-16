import os
import time
import random
import sumoTools
import simulator as sim
from trafficLightControllers import mappingBasedController


def test_map(mapPath):
    bits = 125
    sumoTools.createLaneDetectors(mapPath)
    mapConfigFile = sim.createSimSumoConfigWithRandomTraffic(mapPath)

    random.seed(time.time())

    for _ in range(100):
        config = random.randint(0, 1 << bits)
        controller = mappingBasedController.ctrl(config)
        result = sim.SumoSim(mapConfigFile, controller).run()
        append_if_not_exists(
            "results.txt", f"config {config} total {result.getTotalRuntime()} average {result.getAverageTravelTime()}")

        resultInt = result.getTotalRuntime()

        while True:
            results = [resultInt]
            for i in range(bits):
                newConfig = config ^ (1 << i)
                newController = mappingBasedController.ctrl(newConfig)
                newResult = sim.SumoSim(mapConfigFile, newController).run()
                results.append(newResult.getTotalRuntime())
                append_if_not_exists(
                    "results.txt", f"config {newConfig} total {newResult.getTotalRuntime()} average {newResult.getAverageTravelTime()}")

            indMin = results.index(min(results))
            if results[indMin] == resultInt:
                break

            config = config ^ (1 << (indMin-1))
            resultInt = results[indMin]


def append_if_not_exists(filename, string):
    if os.path.exists(filename):
        append_write = 'a'  # append if already exists
    else:
        append_write = 'w'  # make a new file if not

    highscore = open(filename, append_write)
    highscore.write(string + '\n')
    highscore.close()


if __name__ == '__main__':
    test_map("testMaps/4-4TL4W-Intersection-LARGE/network.net.xml")
