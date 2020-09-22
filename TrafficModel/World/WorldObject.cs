using System;

namespace TrafficModel.World
{
    public abstract class WorldObject
    {
        public Guid Id { get; }
        public string Name { get; set; }
        public bool Enabled { get; set; } = true;

        protected WorldObject()
        {
            Id = Guid.NewGuid();
            World.AddObject(this); // It may be removed, but then every object must be added to World after initialization
        }

        public virtual void Update()
        {
        }

        public override bool Equals(object obj)
        {
            if (obj == null || GetType() != obj.GetType()) return false;

            var other = (WorldObject) obj;
            return other.Id.Equals(Id);
        }

        public override string ToString()
        {
            return $"{Name}({Id})";
        }

        protected bool Equals(WorldObject other)
        {
            return Id.Equals(other.Id);
        }

        public override int GetHashCode()
        {
            return Id.GetHashCode();
        }
    }
}