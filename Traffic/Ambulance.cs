using System;
using System.Drawing;

namespace Traffic
{
    public class Ambulance : Vehicle
    {
        public Ambulance(Point pos, Size size, int rotation, Point velocity, int visionRadius) 
            : base (pos, size, rotation, velocity, visionRadius, Vehicle.PriorityType.EMERGENCY)
        {

        }
    
        public override void tick()
        {
            Console.WriteLine("Ambulance tick!");
        }

    }
}