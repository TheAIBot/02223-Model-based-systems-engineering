using System;
using System.Collections.Generic;
using System.Drawing;
using System.Numerics;
using System.Security.Cryptography;
using System.Threading;
using TrafficModel.Intersections;

namespace TrafficModel.Vehicles
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

        private static int NewID = 0;
        public readonly int ID;
        public readonly float Size;
        protected readonly PriorityType Priority;
        protected readonly float MaxVelocity;
        protected readonly float VisionRadius;

        public Road CurrentRoad { get; protected set; }
        public Vector2 Pos { get; protected set; }
        protected Vector2 Velocity { get; set; }

        protected readonly List<Road> Path = new List<Road>();
        public Road NextRoad 
        {
            get
            {
                return Path.Count > 0 ? Path[0] : null;
            }
        }
        

        protected Vehicle(Road road, Vector2 pos, float maxVelocity, float size, float visionRadius, PriorityType priority) 
        {
            CurrentRoad = road;
            Pos = pos;
            MaxVelocity = maxVelocity;
            Velocity = new Vector2(0, 0);
            Size = size;
            VisionRadius = visionRadius;
            Priority = priority;
            ID = Interlocked.Increment(ref NewID);
        }

        private class PathNode
        {
            internal readonly PathNode PrevNode;
            internal readonly Road CurrRoad;

            internal PathNode(PathNode prev, Road curr)
            {
                this.PrevNode = prev;
                this.CurrRoad = curr;
            }
        }

        public void SetPathTo(Road end)
        {
            Queue<PathNode> goThrough = new Queue<PathNode>();
            HashSet<Road> SeenRoads = new HashSet<Road>();

            goThrough.Enqueue(new PathNode(null, CurrentRoad));

            while (goThrough.Count > 0)
            {
                PathNode curr = goThrough.Dequeue();

                if (curr.CurrRoad == end)
                {
                    PathNode endNode = curr;
                    while (endNode != null)
                    {
                        Path.Add(endNode.CurrRoad);
                        endNode = endNode.PrevNode;
                    }

                    Path.RemoveAt(Path.Count - 1);
                    Path.Reverse();
                    return;
                }

                SeenRoads.Add(curr.CurrRoad);

                foreach (var road in curr.CurrRoad.NextRoads)
                {
                    if (SeenRoads.Contains(road))
                    {
                        continue;
                    }

                    goThrough.Enqueue(new PathNode(curr, road));
                }
            }

            throw new Exception("Failed to find a path.");
        }

        public abstract void Tick(TrafficSim sim);
    }

}
