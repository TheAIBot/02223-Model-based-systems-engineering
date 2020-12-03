#!/usr/bin/env python3

import os
import argparse
import simulator
import sumoTools

from trafficLightControllers import *
algorithms = {
    "static":   staticLights,
    "random":   randomTLController,
    "largest":  largestQueueFirstTLController,
    "weight":   magicController,
    "fair":     fairPrediction,
    "mapping":  mappingBasedController,
}

def pprint(content):
    print("\x1B[0m{}\x1B[2m".format(content))

def get_args():
    p = argparse.ArgumentParser(description = "Run a traffic simulation")
    p.add_argument(
        "ALGORITHM",
        metavar = "ALGORITHM",
        choices = algorithms.keys(),
        help = "Algorithm that controls the traffic lights. Options: {}"
            .format(list(algorithms.keys())),
        type = str,
    )
    p.add_argument(
        "-d", "--density",
        metavar = "DENSITY",
        default = 1.0,
        help = "Traffic density",
        type = float,
    )
    p.add_argument(
        "-l", "--length",
        metavar = "LENGTH",
        default = 20,
        help = "Detector length",
        type = int,
    )
    return p.parse_args()

def main():
    args = get_args()
    algo = args.ALGORITHM
    tra_den = args.density
    det_len = args.length
    exec(algo, tra_den, det_len)

def exec(algo, tra_den, det_len):
    dir_path = "random_map"

    pprint("Creating directory '{}'...".format(dir_path))

    try:
        if not os.path.isdir(dir_path):
            os.mkdir(dir_path)
    except Exception as ex:
        pprint("Failed to create directory: {}".format(ex))
        exit(1)

    map_path = os.path.join(dir_path, "rng-for-gui.net.xml")
    pprint("Generating random map '{}'...".format(map_path))

    try:
        sumoTools.createRandomMap(map_path)
    except Exception as ex:
        pprint("Failed to generate random map: {}".format(ex))
        exit(1)

    pprint("Generating lane detectors...")

    try:
        sumoTools.createLaneDetectors(map_path, det_len)
    except Exception as ex:
        pprint("Failed to generate lane detectors: {}".format(ex))
        exit(1)

    pprint("Generating SUMO configuration...")

    try:
        config_path = simulator.createSimSumoConfigWithRandomTraffic(
            map_path,
            additionalTrafficlighPhases = True,
        )
    except Exception as ex:
        pprint("Failed to generate SUMO configuration: {}".format(ex))
        exit(1)

    ctrl = algorithms[algo].ctrl()

    try:
        if ctrl.needsTrainning():
            pprint("This algorithm requires training, please wait...")
            ctrl.setTrainningRound(True)
            simulator.SumoSim(config_path, ctrl, scale = tra_den, gui = False) \
                     .run(takeMeasurements = False)
            ctrl.setTrainningRound(False)
    except Exception as ex:
        pprint("Simulation failed while training: {}".format(ex))
        exit(1)

    pprint("Launching SUMO GUI...")

    try:
        simulator.SumoSim(config_path, ctrl, scale = tra_den, gui = True) \
                 .run()
    except Exception as ex:
        pprint("Simulation failed: {}".format(ex))

if __name__ == "__main__":
    main()
