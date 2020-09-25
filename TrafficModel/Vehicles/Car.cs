using System;
using System.Numerics;

namespace TrafficModel.Vehicles
{
    public class Car : Vehicle
    {
        private const float CAR_MAX_SPEED = 0.13f;
        private const float CAR_VISION_RADIUS = 8.0f;
        private const float CAR_SIZE = 4.5f;

        public Car(Road road, Vector2 pos) 
            : base(road, pos, CAR_MAX_SPEED, CAR_SIZE, CAR_VISION_RADIUS, PriorityType.CAR)
        {

        }
    
        public override void Tick(TrafficSim sim)
        {
            //if the car has driven to its destination then remove the car
            //from the simulation
            if (NextRoad == null)
            {
                sim.RemoveVehicle(this);
                return;
            }

            Vector2 roadDir = Vector2.Normalize(CurrentRoad.RoadEnd - CurrentRoad.RoadStart);
            Vector2 newCarPos = Pos + roadDir * MaxVelocity;

            //if car is still on the same road then just move the car
            if (CurrentRoad.PosWithinRoad(newCarPos))
            {
                Pos = newCarPos;
                return;
            }

            //car position puts it at the next road so ask the
            //intersection if the car can be moved to the next road
            if (!CurrentRoad.CanPassIntersection(NextRoad))
            {
                Pos = CurrentRoad.RoadEnd;
                return;
            }

            //move car to the next road
            CurrentRoad.RemoveVehicle(this);
            CurrentRoad = NextRoad;
            CurrentRoad.AddVehicle(this);

            //car moved to th next road so remove it from the path
            Path.RemoveAt(0);
        }
    }
}