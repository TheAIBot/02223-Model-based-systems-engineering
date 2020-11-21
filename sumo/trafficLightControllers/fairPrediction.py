#!/usr/bin/env false
# This shebang prevents the direct execution of this script,
# as it is meant to be imported by Python as part of another script.

# Currently we do not specify a custom step length when launching sumo,
# and the default value at the time of writing is 1 second.
# I will go with this assumption while implementing this algorithm.
# TODO If the step length changes in the future, this needs to be adapted too.
STEP_LENGTH = 1.0

# The number of seconds of the past that will be used for prediction
HISTORY_LEN = 5 * 60

# Whether or not to prefer recent history over old history
RECENCY_BIAS = True

# Defines the curve: 1.0 is linear, 2.0 is quadratic, 3.0 is cubic...
RECENCY_BIAS_EXPONENT = 1.5

# Decay of preference to remain in the current phase (time to half)
LAZINESS_DECAY = 5

# Decay of patience to remain in the current phase (time to half)
# Note: this is a maximum value and will be lowered based on traffic volume
PATIENCE_DECAY = 100

DEBUG = False

from trafficLightController import TrafficLightController
import math

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
        self.last_switch = {}
        self.last_target = {}
        self.backoff = {}

    # This method is called in each step by TrafficLightController's
    # update() method with up-to-date data in tlIntersection.
    def updateLights(self, sim, steps):

        # Calculate real-world time and prevent further use of steps
        seconds = steps * STEP_LENGTH
        del steps

        for inters in self.tlIntersections:
            iID = inters.tlID
            groups = inters.getTrafficLightGroups()
            count = len(groups)
            delay_group = []

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

                delays.clear_before(seconds - HISTORY_LEN)
                delay_group.append(delays)

            if iID not in self.last_target:
                self.last_target[iID] = 0
            last_target = self.last_target[iID]

            if iID not in self.backoff:
                self.backoff[iID] = False

            if self.backoff[iID]:
                if inters.inGroupsGreenPhase(groups[last_target]):
                    self.backoff[iID] = False
                    self.last_switch[iID] = seconds
                else:
                    pass
                    #inters.setGroupAsGreen(groups[last_target], sim)
                continue

            if iID not in self.last_switch:
                self.last_switch[iID] = seconds
            last_switch = self.last_switch[iID]

            # Used to make a decision in low traffic
            hysteresis = [
                math.log(delay_group[i].total(seconds) + 1)
                for i in range(count)
            ]

            # Used to react quickly to change in traffic
            pressure = [
                math.log(delay_group[i].total_present(seconds) + 1)
                for i in range(count)
            ]

            # Used to provide fairness in high traffic
            neglect = [
                math.log(delay_group[i].mean(seconds) + 1)
                for i in range(count)
            ]

            # Reflects the amount of traffic
            volume = sum(hysteresis) / count

            laziness = 2 ** (0 - (seconds - last_switch) / LAZINESS_DECAY)
            patience = 2 ** \
                (1 - (seconds - last_switch) / (PATIENCE_DECAY / (volume + 1)))
            patience = min(1, patience)

            scores = [0] * count
            for i in range(count):
                score = 1
                score *= (hysteresis[i] + 1) / (volume + 1)
                score *= pressure[i] + 1
                score *= (neglect[i] + 1) * (volume + 1)
                scores[i] = score

            scores[last_target] *= laziness * volume + 1
            scores[last_target] *= patience

            highest = max(scores)
            # Prefer the current target if it's a tie
            if scores[last_target] == highest:
                target = last_target
            else:
                target = scores.index(highest)

            if target != last_target:
                self.last_target[iID] = target
                self.backoff[iID] = True

            inters.setGroupAsGreen(groups[target], sim)

            if DEBUG:
                print(
                    "\n### {:>4s} [l{:>7.2f}][p{:>7.2f}]"
                    .format(iID, laziness, patience)
                )
                print_table(
                    hysteresis, pressure, volume, neglect, scores, target
                )

def print_table(h, p, v, n, s, t):
    print("### hyst {}".format(fmt_arr(h, "[{:>8.2f}]")))
    print("### pres {}[v{:>7.2f}]".format(fmt_arr(p, "[{:>8.2f}]"), v))
    print("### negl {}".format(fmt_arr(n, "[{:>8.2f}]")))
    print("### scor {}".format(fmt_arr(s, "[{:>8.2f}]")))
    print("### targ {}".format(
        fmt_arr(['#'*8 if i == t else '' for i in range(len(s))], "[{:8}]"))
    )

def fmt_arr(arr, fmt):
    return ''.join([fmt.format(e) for e in arr])

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
            self.arrivals[vID] = seconds - 1

    # Clears stored delays of vehicles that have left the detector
    def clear_departed(self):
        self.departed = []

    # Clears stored delays that happened before the provided timestamp
    def clear_before(self, seconds):
        self.departed = list(filter(
            lambda departure: seconds <= departure.timestamp,
            self.departed
        ))

    def __weight(self, seconds, departtime, bias_exp):
        if not RECENCY_BIAS:
            return 1
        age = seconds - departtime
        weight = (HISTORY_LEN - age) / HISTORY_LEN
        return max(0, min(weight, 1)) ** bias_exp

    def count_past(self, seconds, bias_exp=RECENCY_BIAS_EXPONENT):
        if not RECENCY_BIAS:
            return len(self.departed)
        count = 0
        for departure in self.departed:
            count += self.__weight(seconds, departure.timestamp, bias_exp)
        return count

    def total_present(self, seconds):
        total = 0
        for vID, arrival in self.arrivals.items():
            total += seconds - arrival
        return total

    def total_past(self, seconds, bias_exp=RECENCY_BIAS_EXPONENT):
        total = 0
        for departure in self.departed:
            weight = self.__weight(seconds, departure.timestamp, bias_exp)
            total += departure.delay * weight
        return total

    def total(self, seconds, bias_exp=RECENCY_BIAS_EXPONENT):
        return self.total_present(seconds) + self.total_past(seconds, bias_exp)

    def mean_present(self, seconds):
        count = len(self.arrivals)
        if count == 0:
            return 0
        else:
            return self.total_present(seconds) / count

    def mean_past(self, seconds, bias_exp=RECENCY_BIAS_EXPONENT):
        count = self.count_past(seconds, bias_exp)
        if count == 0:
            return 0
        else:
            return self.total_past(seconds, bias_exp) / count

    def mean(self, seconds, bias_exp=RECENCY_BIAS_EXPONENT):
        count = len(self.arrivals) + self.count_past(seconds, bias_exp)
        if count == 0:
            return 0
        else:
            return self.total(seconds, bias_exp) / count

class Departure:

    def __init__(self, timestamp, delay):

        # Departure timestamp in seconds
        self.timestamp = timestamp

        # Delay in seconds
        self.delay = delay
