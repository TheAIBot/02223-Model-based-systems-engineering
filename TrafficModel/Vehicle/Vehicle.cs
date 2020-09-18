using System.Drawing;

namespace TrafficModel.Vehicle
{
    public abstract class Vehicle
    {
        public enum Direction
        {
            LEFT = 0,
            RIGHT = 1,
            STRAIGHT = 2,
            REVERSE = 3
        }

        public enum PriorityType
        {
            CAR = 0,
            PUBLIC_TRANSPORT = 1,
            EMERGENCY = 2
        }

        protected Point Pos { get; private set; }
        protected Size Size { get; private set; }
        protected int Rotation { get; private set; }
        protected Point Velocity { get; private set; }
        protected int VisionRadius { get; private set; }
        protected PriorityType Priority { get; private set; }

        public Vehicle(Point pos, Size size, int rotation, Point velocity,
         int visionRadius, PriorityType priority) {
            Pos = pos;
            Size = size;
            Rotation = rotation;
            Velocity = velocity;
            VisionRadius = visionRadius;
            Priority = priority;
        }

        public abstract void Tick();
    }

}
