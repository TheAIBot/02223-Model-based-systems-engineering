# Algorithms

## Fixed-cycle controller

- Cycle time: duration of a complete cycle
- Split time: duration of a state
- Offset: the starting time of a cycle relative to other traffic lights

Longer cycle time is better for high traffic.
Split time can be adjusted to give preference to busy roads.
Offset can be adjusted to create green waves, for example.

## Expert Systems (artificial intelligence)

_A computer system that emulates the decision-making ability of a human expert._

- Knowledge-based: uses a set of if-then rules

Multiple systems can communicate to allow for synchronization.
Rules can be optimized by analyzing how often they fire and how they perform.
Computational resource availability might become the limiting factor.

## Prediction-based optimization (simple)

The configuration for the next cycle is determined based on
the measurements taken in the current cycle.

High fluctuations are not handled well.

## Prediction-based optimization with delay time fairness

Measure the delay time of vehicles.
Estimate average delay time while filtering out fluctuations.
Optimize for:
 - minimal total delay
 - minimal total deviation from average delay (fairness)

Use data from the past 15 minutes to determine configuration for the next cycle.

## Fuzzy logic

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
