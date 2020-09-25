using System;
using System.Collections.Generic;
using System.Text;

namespace TrafficModel.Intersections
{
    public abstract class Intersection
    {
        public abstract void Tick(TrafficSim sim);
        public abstract bool CanPass(Road from, Road to);
    }
}
