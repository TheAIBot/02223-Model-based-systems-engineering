using System.Drawing;

namespace TrafficModel
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

        public enum PriorityType {
            CAR = 0,
            PUBLIC_TRANSPORT = 1,
            EMERGENCY = 2
        }

        protected Point Pos;
        protected Size Size;
        protected int Rotation;
        protected Point Velocity;
        protected int VisionRadius;
        protected PriorityType Priority;

        public Vehicle(Point pos, Size size, int rotation, Point velocity,
         int visionRadius, PriorityType priority) {
            Pos = pos;
            Size = size;
            Rotation = rotation;
            Velocity = velocity;
            VisionRadius = visionRadius;
            Priority = priority;
        }

        public abstract void tick();
    }

}
