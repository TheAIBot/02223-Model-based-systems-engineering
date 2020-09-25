using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace TrafficModel.Intersections
{
    public class RoadConnection
    {
        public readonly Road From;
        public readonly Road To;

        public RoadConnection(Road from, Road to)
        {
            this.From = from;
            this.To = to;
        }
    }

    public class RoadConnectionGroup
    {
        public readonly RoadConnection[] Connections;

        public RoadConnectionGroup(RoadConnection[] roadCconnections)
        {
            this.Connections = roadCconnections;
        }

        internal bool HasEnteringRoad(Road road)
        {
            for (int i = 0; i < Connections.Length; i++)
            {
                if (Connections[i].From == road)
                {
                    return true;
                }
            }

            return false;
        }
    }

    public enum TrafficLightState
    {
        Red,
        Yellow,
        Green
    }

    public class TrafficGroupState
    {
        public readonly List<Road> InternalRoads = new List<Road>();
        internal readonly RoadConnectionGroup ConnectionGroup;
        public TrafficLightState State;

        internal TrafficGroupState(RoadConnectionGroup group)
        {
            this.ConnectionGroup = group;
            this.State = TrafficLightState.Red;
        }

        internal bool HasEnteringRoad(Road road)
        {
            return ConnectionGroup.HasEnteringRoad(road);
        }

        internal void AddInternalRoad(Road road)
        {
            InternalRoads.Add(road);
        }
    }

    public class TrafficLight : Intersection
    {
        public readonly List<TrafficGroupState> TrafficGroups = new List<TrafficGroupState>();
        TrafficLightState[] StateOrder = new TrafficLightState[] { TrafficLightState.Yellow, TrafficLightState.Green, TrafficLightState.Yellow, TrafficLightState.Red };
        int TrafficStateIndex = 0;
        int TrafficStateCounter = 0;
        int TrafficGroupStateChangeIndex = 0;
        private const int STATE_TICK_DURATION = 100;

        public TrafficLight(TrafficSim sim, RoadConnectionGroup[] groups)
        {
            foreach (var group in groups)
            {
                TrafficGroups.Add(new TrafficGroupState(group));
                foreach (var connection in group.Connections)
                {
                    Road internalRoad = new Road(connection.From.RoadEnd, connection.To.RoadStart);
                    TrafficGroups.Last().AddInternalRoad(internalRoad);
                    sim.AddRoad(internalRoad);

                    connection.From.SetIntersection(this);
                    connection.From.AddOutgoingRoad(internalRoad);
                    internalRoad.AddOutgoingRoad(connection.To);
                }
            }
        }

        public override void Tick(TrafficSim sim)
        {
            var group = TrafficGroups[TrafficStateIndex];

            TrafficStateCounter++;
            if (TrafficStateCounter == STATE_TICK_DURATION)
            {
                TrafficStateCounter = 0;
                TrafficGroupStateChangeIndex++;
            }

            group.State = StateOrder[TrafficGroupStateChangeIndex];

            if (TrafficGroupStateChangeIndex == StateOrder.Length - 1)
            {
                TrafficGroupStateChangeIndex = 0;
                TrafficStateIndex = (TrafficStateIndex + 1) % TrafficGroups.Count;
            }
        }

        public override bool CanPass(Road from, Road to)
        {
            for (int i = 0; i < TrafficGroups.Count; i++)
            {
                if (TrafficGroups[i].HasEnteringRoad(from))
                {
                    return TrafficGroups[i].State == TrafficLightState.Green;
                }
            }

            return false;
        }
    }
}
