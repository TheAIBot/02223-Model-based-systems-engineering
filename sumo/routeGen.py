import os
import subprocess

def gen_random_routes(mapFilepath, nVec):
    mapFolderPath = os.path.dirname(mapFilepath)
    routeFilepath = os.path.join(mapFolderPath, "routes.xml")
    randomTripsPath = os.path.join(os.environ["SUMO_HOME"], "tools", "randomTrips.py")
    subprocess.run(["python", randomTripsPath, "-n", mapFilepath, "-e", str(nVec), "--seed", "56",
     "--trip-attributes=type=\"vehicle1\"", "--additional-file", "vehicle_type.add.xml", "--route-file", routeFilepath])
    return routeFilepath