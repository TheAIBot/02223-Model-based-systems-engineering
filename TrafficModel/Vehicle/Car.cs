using System;
using System.Drawing;

namespace TrafficModel.Vehicle
{
    public class Car : Vehicle
    {
        public Car(Point pos, Size size, int rotation, Point velocity, int visionRadius) 
            : base (pos, size, rotation, velocity, visionRadius, Vehicle.PriorityType.CAR)
        {

        }
    
        public override void Tick()
        {
            Console.WriteLine("Car tick!");
        }

    }
}