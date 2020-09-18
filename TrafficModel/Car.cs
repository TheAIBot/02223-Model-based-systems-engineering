using System;
using System.Drawing;

namespace TrafficModel
{
    public class Car : Vehicle
    {
        public Car(Point pos, Size size, int rotation, Point velocity, int visionRadius) 
            : base (pos, size, rotation, velocity, visionRadius, Vehicle.PriorityType.CAR)
        {

        }
    
        public override void tick()
        {
            Console.WriteLine("Car!");
        }

    }
}