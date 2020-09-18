using System;

namespace TrafficModel
{
    public class TrafficLight
    {
        public enum Light
        {
            GREEN = 0,
            YELLOW = 1,
            RED = 2
        }

        public Light CurrentLight { get; private set; }

        // measured in seconds
        public int GreenDuration { get; private set; }
        public int YellowDuration { get; private set; }
        public int RedDuration { get; private set; }

        public TrafficLight(Light initialLight, int greenDuration, int yellowDuration, int redDuration)
        {
            CurrentLight = initialLight;
            GreenDuration = greenDuration;
            YellowDuration = yellowDuration;
            RedDuration = redDuration;
        }
    
        public void Tick()
        {
            Console.WriteLine("Traffic Light tick!");
        }

    }
}