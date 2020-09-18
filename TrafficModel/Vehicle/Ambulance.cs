using System;
using System.Drawing;

namespace TrafficModel.Vehicle
{
    public class Ambulance : Vehicle
    {
        public Ambulance(Point pos, Size size, int rotation, Point velocity, int visionRadius) 
            : base (pos, size, rotation, velocity, visionRadius, Vehicle.PriorityType.EMERGENCY)
        {

        }
    
        public override void Tick()
        {
            Console.WriteLine("Ambulance tick!");
        }

    }
}