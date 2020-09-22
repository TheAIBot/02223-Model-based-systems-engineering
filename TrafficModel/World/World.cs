using System;
using System.Collections.Generic;
using System.Linq;

namespace TrafficModel.World
{
    public static class World
    {
        private static readonly List<WorldObject> GameObjects = new List<WorldObject>();
        private static readonly Stack<WorldObject> Trash = new Stack<WorldObject>();
        private static readonly Stack<WorldObject> NewObjects = new Stack<WorldObject>();

        public static void UpdateWorld()
        {
            AddObjects();
            UpdateObjects();
            RemoveObjects();
        }

        private static void RemoveObjects()
        {
            while (Trash.Any())
            {
                try
                {
                    GameObjects.Remove(Trash.Pop());
                }
                catch (Exception e)
                {
                    Console.WriteLine($"Exception while removing worldObject: {e.Message}");
                    Console.WriteLine($"Stack trace: {e.StackTrace}");
                }
            }
        }

        private static void UpdateObjects()
        {
            for (var i = GameObjects.Count - 1; i >= 0; i--)
            {
                if (GameObjects[i].Enabled == false)
                {
                    continue;
                }

                GameObjects[i].Update();
            }
        }

        private static void AddObjects()
        {
            while (NewObjects.Any())
            {
                GameObjects.Add(NewObjects.Pop());
            }
        }

        public static void AddObject(WorldObject worldObject)
        {
            if (GameObjects.Contains(worldObject) || NewObjects.Contains(worldObject))
            {
                Console.WriteLine($"Attempt to add existing/queued object with id={worldObject.Id}. Ignoring.");
            }

            NewObjects.Push(worldObject);
        }

        public static void DestroyObject(WorldObject worldObject)
        {
            Trash.Push(worldObject);
        }
    }
}