# Algorithms

## Fixed-cycle controller [ITLC]

- Cycle time: duration of a complete cycle
- Split time: duration of a state
- Offset: the starting time of a cycle relative to other traffic lights

Longer cycle time is better for high traffic.
Split time can be adjusted to give preference to busy roads.
Offset can be adjusted to create green waves, for example.

## Expert Systems (artificial intelligence) [ITLC]

_A computer system that emulates the decision-making ability of a human expert._

- Knowledge-based: uses a set of if-then rules

Multiple systems can communicate to allow for synchronization.
Rules can be optimized by analyzing how often they fire and how they perform.
Computational resource availability might become the limiting factor.

## Prediction-based optimization (simple) [ITLC]

The configuration for the next cycle is determined based on
the measurements taken in the current cycle.

High fluctuations are not handled well.

## Prediction-based optimization with delay time fairness [ITLC]

Measure the delay time of vehicles.
Estimate average delay time while filtering out fluctuations.
Optimize for:
 - minimal total delay
 - minimal total deviation from average delay (fairness)

Use data from the past 15 minutes to determine configuration for the next cycle.

## Fuzzy logic [ITLC]

_Should mimic human intelligence._

It can handle terms like "more", "less", "longer", for example:
_if there is more traffic from north to south, the lights should stay green longer_

Fuzzy variables have different weight,
for example 5 cars in a queue will result in:
 - 25% activation of "many"
 - 75% activation of "medium"

The controller determines the split times (state duration).
The order of the states is static, but they can be skipped if duration is 0.
The fuzzy variables have to be configured for a certain load of traffic.
Multiple intersections can communicate.

## Evolutionary algorithm [ITLC]

[Wikipedia article](https://en.wikipedia.org/wiki/Evolutionary_algorithm)

[Rechenberg, 1989](https://link.springer.com/chapter/10.1007/978-3-642-83814-9_6)

Good luck.

## Vehicular ad hoc networks [VANET]

_Each vehicle over the road periodically broadcasts the basic traveling data (i.e., location, speed, direction, destination, etc). Vehicles receive the basic traffic data of surrounding vehicles. Based on the location of each sender vehicle the receiver vehicle decide if they are located on the same traffic flow (i.e., same process) or not. The traffic density (di), traffic speed (si), and estimated traveling time (ti) are computed for each traffic flow inside the ready area according to [2]. For each traffic flow, the vehicle that is located closest to the traffic light reporting the traffic characteristics of such a flow to the intelligent traffic light._

They also use SUMO.

# Sources

 - ITLC: [Intelligent Traffic Light Control](https://findit.dtu.dk/en/catalog/2399485817)
 - VANET: [An Intelligent Traffic Light Scheduling Algorithm Through VANETs](https://ieeexplore.ieee.org/document/6927714)
