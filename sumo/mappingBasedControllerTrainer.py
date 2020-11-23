import os
import time
import random
import sumoTools
import simulator as sim
from multiprocessing import Pool, cpu_count
from trafficLightControllers import mappingBasedController


def getResult(config, mapConfigFile, maxSteps):
    newController = mappingBasedController.ctrl(config)  # lqf 5676
    newResult = sim.SumoSim(mapConfigFile, newController).run(True, maxSteps)
    return newResult.getTotalRuntime()


def test_map(mapPath):
    bits = 125
    startMax = 12000
    mapConfigFile = sim.createSimSumoConfigWithRandomTraffic(mapPath)

    random.seed(time.time())
    config, resultInt = GetInitial(bits, mapConfigFile, startMax)

    append_if_not_exists("results.txt", f"config {config} total {resultInt}")
    if(resultInt >= startMax):
        return

    while True:
        processData = []
        for i in range(bits):
            newConfig = config ^ (1 << i)
            processData.append((newConfig, mapConfigFile, resultInt))

        results = []
        with Pool(cpu_count()) as mpPool:
            results = mpPool.starmap(getResult, processData)

        indMin = results.index(min(results))
        config = config ^ (1 << (indMin))

        append_if_not_exists(
            "results.txt", f"config {config} total {min(results)}")

        if results[indMin] == resultInt:
            break

        resultInt = results[indMin]

    append_if_not_exists("results.txt", "Converged")


def GetInitial(bits, mapConfigFile, startMax):
    processData = []
    for _ in range(cpu_count()):
        newConfig = random.randint(0, 1 << bits)
        processData.append((newConfig, mapConfigFile, startMax))

    results = []
    with Pool(cpu_count()) as mpPool:
        results = mpPool.starmap(getResult, processData)

    imin = results.index(min(results))
    config = processData[imin][0]
    resultInt = min(results)
    return config, resultInt


def append_if_not_exists(filename, string):
    if os.path.exists(filename):
        append_write = 'a'  # append if already exists
    else:
        append_write = 'w'  # make a new file if not

    highscore = open(filename, append_write)
    highscore.write(string + '\n')
    highscore.close()


if __name__ == '__main__':
    mapSavePath = "random_map"
    if not os.path.isdir(mapSavePath):
        os.mkdir(mapSavePath)
    mapFilepath = os.path.join(mapSavePath, "rng1" + ".net.xml")
    sumoTools.createRandomMap(mapFilepath)
    sumoTools.createLaneDetectors(mapFilepath)
    while True:
        test_map(mapFilepath)
