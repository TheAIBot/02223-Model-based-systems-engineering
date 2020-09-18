using System;
using System.Drawing;

namespace Traffic
{
    public class Bus : Vehicle
    {
        public Bus(Point pos, Size size, int rotation, Point velocity, int visionRadius) 
            : base (pos, size, rotation, velocity, visionRadius, Vehicle.PriorityType.PUBLIC_TRANSPORT)
        {

        }
    
        public override void tick()
        {
            Console.WriteLine("Bus tick!");
        }

    }
}