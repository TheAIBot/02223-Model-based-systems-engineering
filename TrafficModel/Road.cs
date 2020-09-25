using System;
using System.Collections.Generic;
using System.Drawing;
using System.Numerics;
using System.Threading;
using TrafficModel.Intersections;
using TrafficModel.Vehicles;

namespace TrafficModel
{
    public class Road
    {
        private static int NewID = 0;
        public readonly int ID;

        public readonly Vector2 RoadStart;
        public readonly Vector2 RoadEnd;
        public readonly List<Road> NextRoads = new List<Road>();
        public Intersection RoadIntersection = null;
        public readonly List<Vehicle> Vehicles = new List<Vehicle>();


        public Road(Vector2 start, Vector2 end)
        {
            this.RoadStart = start;
            this.RoadEnd = end;
            ID = Interlocked.Increment(ref NewID);
        }

        public void SetIntersection(Intersection intersection)
        {
            RoadIntersection = intersection;
        }

        public bool CanPassIntersection(Road to)
        {
            if (RoadIntersection == null)
            {
                return true;
            }

            return RoadIntersection.CanPass(this, to);
        }

        public void AddOutgoingRoad(Road road)
        {
            NextRoads.Add(road);
        }

        public void AddVehicle(Vehicle vehicle)
        {
            Vehicles.Add(vehicle);
        }

        public void RemoveVehicle(Vehicle vehicle)
        {
            Vehicles.Remove(vehicle);
        }

        internal bool GetAnyCollidingVehicle(Vector2 frontPos, Vector2 backpos)
        {
            throw new NotImplementedException();
        }

        internal bool PosWithinRoad(Vector2 pos)
        {
            Vector2 roadCenter = (RoadStart + RoadEnd) * 0.5f;
            float distCenterToEnd = Vector2.Distance(roadCenter, RoadEnd);
            float distCenterToPos = Vector2.Distance(roadCenter, pos);

            return distCenterToEnd > distCenterToPos;
        }
    }
}