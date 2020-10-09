import os
import subprocess

def gen_random_routes(mapFilepath):
    mapFolderPath = os.path.dirname(mapFilepath)
    routeFilepath = os.path.join(mapFolderPath, "routes.xml")
    subprocess.run(["<SUMO_HOME>/tools/randomTrips.py", "-n", mapFilepath, "--seed", "56", "--route-file", "-o", ])

    return routeFilepath
