import os
import subprocess

def gen_random_routes(mapFilepath):
    mapFolderPath = os.path.dirname(mapFilepath)
    routeFilepath = os.path.join(mapFolderPath, "routes.xml")
    randomTripsPath = os.path.join(os.environ["SUMO_HOME"], "tools", "randomTrips.py")
    subprocess.run(["python", randomTripsPath, "-n", mapFilepath, "-e", "1000", "--seed", "56", "--route-file", routeFilepath])

    return routeFilepath
