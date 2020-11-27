import os
from subprocess import run
import time
import random
from trafficLightControllers import fairPrediction
import sumoTools
import simulator as sim
from multiprocessing import Pool, cpu_count
from trafficLightControllers import mappingBasedController

bits = mappingBasedController.ctrl.bits()
startMax = 14000
mutChange = 0.4
cutoff = 280
initialTries = 800
threads = 10

# todo add rules to ignore bullshit configs
# for example, if we change the light when there are 10 on current, 20 on other and 20 s since last change, 
# we should also change it for all times > 20 and all other > 20
# with that, create a dictionary of current results, and dont recompute bullshit mutations 
def getResult(config, mapConfigFile):
    newController = mappingBasedController.ctrl(config)  # lqf 5676
    newResult = sim.SumoSim(mapConfigFile, newController).run(
        True, startMax, 500, cutoff)
    append_if_not_exists(
        "results.txt", f"config {config:b} avg {newResult.getAverageTravelTime()} total {newResult.getTotalRuntime()}")
    return newResult.getAverageTravelTime()


def runHillClimbing(mapConfigFile, config, result):
    while True:
        (bestResult, bestConfig) = runHillClimbingIter(config, mapConfigFile)

        if bestResult >= result:
            break

        config = bestConfig
        result = bestResult

    append_if_not_exists("results.txt", "Converged")


def runHillClimbingIter(config, mapConfigFile):
    processData = []
    bitIndices=list(range(bits))
    random.shuffle(bitIndices)
    for i in bitIndices:
        newConfig = config ^ (1 << i)
        processData.append((newConfig, mapConfigFile))

    results = []
    with Pool(threads) as mpPool:
        results = mpPool.starmap(getResult, processData)

    indMin = results.index(min(results))
    bestConfig = processData[indMin][0]

    return (min(results), bestConfig)


def runGenetic(mapConfigFile, lenBest, lenGen):
    for _ in range(15):
        append_if_not_exists("results.txt", "\n")
        best = readBest(lenBest)
        newGen = createNewGeneration(best, lenGen)

        processData = []
        for config in newGen:
            processData.append((config, mapConfigFile))

        with Pool(threads) as mpPool:
            mpPool.starmap(getResult, processData)

        append_if_not_exists    ("results.txt", "\n")
        global mutChange
        mutChange /= 2


def createNewGeneration(currentConfigs, generationSize):
    newGen = []
    for _ in range(generationSize):
        configL = currentConfigs[random.randint(0, len(currentConfigs) - 1)]
        configR = currentConfigs[random.randint(0, len(currentConfigs) - 1)]
        child = 0
        for bit in range(bits):
            randVal = random.random()
            if randVal <= mutChange/2:
                child |= (1 << bit)
            elif randVal <= mutChange:
                pass
            elif randVal <= 0.5:
                child |= (configL & (1 << bit))
            else:
                child |= (configR & (1 << bit))

        newGen.append(child)

    return newGen


def getConfigAndScore(line):
    lineSplit = line.split()
    config = 0
    if len(lineSplit[1]) > bits/2:
        config = int(lineSplit[1], 2)
    else:
        config = int(lineSplit[1])

    score = float(lineSplit[3])
    return (config, score)


def readBest(count):
    f = open("results.txt", "r")
    lines = f.readlines()
    lines = list(filter(lambda line: len(line) > 100, lines))
    configsAndScores = [getConfigAndScore(line) for line in lines]
    configsAndScores.sort(key=lambda tup: tup[1])
    configs = [t[0] for t in configsAndScores]
    best = configs[0:count]
    return best


def GetInitial(mapConfigFile):
    processData = []
    for _ in range(initialTries):
        newConfig = random.randint(0, 1 << bits)
        processData.append((newConfig, mapConfigFile))

    results = []
    with Pool(threads) as mpPool:
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
    mapConfigFile = sim.createSimSumoConfigWithRandomTraffic(mapFilepath)

    random.seed(time.time())
    #GetInitial(mapConfigFile)

    runGenetic(mapConfigFile, 12, 150)
    #best = readBest(1)[0]
    #runHillClimbing(mapConfigFile, best, 238)
