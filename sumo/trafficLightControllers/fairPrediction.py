#!/usr/bin/env false
# This shebang prevents the direct execution of this script,
# as it is meant to be imported by Python as part of another script.

# Currently we do not specify a custom step length when launching sumo,
# and the default value at the time of writing is 1 second.
# I will go with this assumption while implementing this algorithm.
# TODO If the step length changes in the future, this needs to be adapted too.
STEP_LENGTH = 1.0
HISTORY_LEN = 15 * 60
SPLIT_MIN = 20
CYCLE_MIN = 120
CYCLE_MAX = 240
DEBUG = False

from trafficLightController import TrafficLightController
import math

def signed_devs(arr):
    count = len(arr)
    if count == 0:
        return 0
    mean = sum(arr) / count
    return [entry - mean for entry in arr]

def stdev(arr):
    count = len(arr)
    if count == 0:
        return 0
    mean = sum(arr) / count
    devs = [math.pow(entry - mean, 2) for entry in arr]
    return math.sqrt(sum(devs) / count)

# This class is the main entry point of this traffic light controller.
# The test execution environment requires this class to be called 'ctrl'.
# Certain shared functionalities are implemented in its parent class.
class ctrl(TrafficLightController):

    def __init__(self):

        # The constructor of TrafficLightController expects
        # the name of the controller as its only argument.
        super().__init__("FP", 'b')

    def init(self, sim):
        super().init(sim)

        # These are the only instance attributes this class has, therefore
        # all methods will operate only on these and will not introduce more.
        self.delay_groups = {}
        self.cycle_plans = {}

    # This method is called in each step by TrafficLightController's
    # update() method with up-to-date data in tlIntersection.
    def updateLights(self, sim, steps):

        # Calculate real-world time and prevent further use of steps
        seconds = steps * STEP_LENGTH
        del steps

        for inters in self.tlIntersections:
            iID = inters.tlID
            groups = inters.getTrafficLightGroups()

            if iID not in self.cycle_plans:
                self.cycle_plans[iID] = Plan(seconds, len(groups))
            plan = self.cycle_plans[iID]

            cycle_over = plan.is_over(seconds)

            totals = []
            means = []
            for i, group in enumerate(groups):
                # Create a unique ID for each group, derived from:
                #  - the ID of the intersection the group belongs to,
                #  - the index of the group in the list.
                gID = "{}.{}".format(inters.tlID, i)

                # Find the current group's instance of Delays.
                # If it doesn't exist, create a new one.
                if gID not in self.delay_groups:
                    self.delay_groups[gID] = Delays()
                delays = self.delay_groups[gID]

                # Feed the current list of vehicle IDs into the Delays instance
                delays.update(seconds, group.getVehicleIDsFromDetectors())

                #if cycle_over:
                delays.clear_before(seconds - HISTORY_LEN)
                totals.append(delays.total(seconds))
                means.append(delays.mean(seconds))

            if cycle_over:
                if DEBUG:
                    print("########################################")
                plan.update(seconds, totals, means)

            inters.setGroupAsGreen(groups[plan.get_target(seconds)], sim)

            # The lower, the better
            if DEBUG:
                efficiency = sum(totals)
                fairness = stdev(means)
                print("### eff {:>15.4} fai {:>15.4}".format(efficiency, fairness))

class Plan:

    def __init__(self, seconds, count):
        split = max(SPLIT_MIN, CYCLE_MIN / count)
        self.splits = [split] * count
        self.update_timestamps(seconds)
        self.last_total = 0

    def update_timestamps(self, seconds):
        base = seconds
        timestamps = []
        for split in self.splits:
            base += split
            timestamps.append(base)
        if DEBUG:
            print("{} at {}".format(timestamps, seconds))
        self.timestamps = timestamps

    def is_over(self, seconds):
        return self.timestamps[-1] <= seconds

    def get_target(self, seconds):
        return len(list(filter(
            lambda timestamp: timestamp <= seconds,
            self.timestamps
        )))

    # TODO This needs tuning, especially for variable cycle length
    def update(self, seconds, totals, means):
        if len(totals) != len(means) != len(self.splits):
            raise Exception("Argument length mismatch in Plan.update()")

        count = len(self.splits)
        deviations = signed_devs(means)
        if DEBUG:
            print("### Deviations: {}".format(deviations))

        for i in range(count):
            old = self.splits[i]
            dev = deviations[i]
            self.splits[i] = max(SPLIT_MIN, old + dev)

        cycle = sum(self.splits)
        mul = min(1, CYCLE_MAX / cycle) * max(1, CYCLE_MIN / cycle)

        if mul != 1:
            for i in range(count):
                self.splits[i] *= mul

        if DEBUG:
            print("### Splits: {} {}".format(self.splits, sum(self.splits)))
        self.update_timestamps(seconds)

class Delays:

    def __init__(self):

        # Key  : vehicle ID
        # Value: arrival timestamp in seconds
        self.arrivals = {}

        # Each entry is an instance of Departure
        self.departed = []

    # seconds: current timestamp in seconds
    # present: list of vehicle IDs present on the detector
    def update(self, seconds, present):
        old_arrivals = self.arrivals.copy()
        for vID, arrival in old_arrivals.items():

            # Skip seen vehicles that are still present
            if vID in present:
                continue

            # Process vehicles that have left the detector
            self.departed.append(Departure(seconds, seconds - arrival))
            del self.arrivals[vID]

        for vID in present:

            # Skip vehicles that we have seen
            if vID in self.arrivals:
                continue

            # Store arrival timestamp of new vehicles
            self.arrivals[vID] = seconds
        if DEBUG:
            print("+" * len(self.arrivals), end='')
            print("-" * len(self.departed))

    # Clears stored delays of vehicles that have left the detector
    def clear_departed(self):
        self.departed = []

    # Clears stored delays that happened before the provided timestamp
    def clear_before(self, seconds):
        self.departed = list(filter(
            lambda departure: seconds <= departure.timestamp,
            self.departed
        ))

    def total_present(self, seconds):
        total = 0.0
        for vID, arrival in self.arrivals.items():
            total += seconds - arrival
        return total

    def total_past(self):
        total = 0.0
        for departure in self.departed:
            total += departure.delay
        return total

    def total(self, seconds):
        return self.total_present(seconds) + self.total_past()

    def mean_present(self, seconds):
        count = len(self.arrivals)
        if count == 0:
            return 0
        else:
            return self.total_present(seconds) / count

    def mean_past(self):
        count = len(self.departed)
        if count == 0:
            return 0
        else:
            return self.total_past() / count

    def mean(self, seconds):
        count = len(self.arrivals) + len(self.departed)
        if count == 0:
            return 0
        else:
            return self.total(seconds) / count

class Departure:

    def __init__(self, timestamp, delay):

        # Departure timestamp in seconds
        self.timestamp = timestamp

        # Delay in seconds
        self.delay = delay
