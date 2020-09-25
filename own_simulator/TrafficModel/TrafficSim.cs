using System;
using System.Collections.Generic;
using System.Text;
using TrafficModel.Intersections;
using TrafficModel.Vehicles;

namespace TrafficModel
{
    public class TrafficSim
    {
        public readonly List<Vehicle> AddedVehicles = new List<Vehicle>();
        public readonly List<Vehicle> RemovedVehicles = new List<Vehicle>();

        public readonly List<Vehicle> Vehicles = new List<Vehicle>();
        public readonly List<Road> Roads = new List<Road>();
        public readonly List<Intersection> Intersections = new List<Intersection>();

        public void Tick()
        {
            RemovedVehicles.Clear();
            AddedVehicles.Clear();

            foreach (var vehicle in Vehicles)
            {
                vehicle.Tick(this);
            }

            foreach (var intersection in Intersections)
            {
                intersection.Tick(this);
            }

            foreach (var vehicle in RemovedVehicles)
            {
                Vehicles.Remove(vehicle);
            }

            foreach (var vehicle in AddedVehicles)
            {
                Vehicles.Add(vehicle);
            }
        }

        internal void RemoveVehicle(Vehicle vehicle)
        {
            RemovedVehicles.Add(vehicle);
        }

        internal void AddVehicle(Vehicle vehicle)
        {
            AddedVehicles.Add(vehicle);
        }

        public void AddVehicleToSim(Vehicle vehicle)
        {
            Vehicles.Add(vehicle);
        }

        public void AddIntersection(Intersection intersection)
        {
            Intersections.Add(intersection);
        }

        public void AddRoad(Road road)
        {
            Roads.Add(road);
        }
    }
}
