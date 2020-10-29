import xml.etree.ElementTree as ET
import sys

def gen_trip_stats():
    fileName = 'tripinfo.xml'

    tree = ET.parse(fileName)
    root = tree.getroot()

    # all tripinfo tags
    total_trips    = 0
    total_duration = 0
    total_CO_abs   = 0
    total_CO2_abs  = 0
    total_HC_abs   = 0
    total_PMx_abs  = 0
    total_NOx_abs  = 0
    total_fuel_abs = 0
    total_elec_abs = 0

    for child in root:
        total_trips = total_trips + 1
        total_duration = total_duration + float(child.get('duration'))

        for emission in child.iter('emissions'):
            CO = float(emission.get('CO_abs'))
            CO2 = float(emission.get('CO2_abs'))
            HC = float(emission.get('HC_abs'))
            PMx = float(emission.get('PMx_abs'))
            NOx = float(emission.get('NOx_abs'))
            fuel = float(emission.get('fuel_abs'))
            elec = float(emission.get('electricity_abs'))
            total_CO_abs = total_CO_abs + CO
            total_CO2_abs = total_CO2_abs + CO2
            total_HC_abs = total_HC_abs + HC
            total_PMx_abs = total_PMx_abs + PMx
            total_NOx_abs = total_NOx_abs + NOx
            total_fuel_abs = total_fuel_abs + fuel
            total_elec_abs = total_elec_abs + elec

    mean_duration = total_duration / total_trips
    mean_CO = total_CO_abs / total_trips
    mean_CO2 = total_CO2_abs / total_trips
    mean_HC = total_HC_abs / total_trips
    mean_PMx = total_PMx_abs / total_trips
    mean_NOx = total_NOx_abs / total_trips
    mean_fuel = total_fuel_abs / total_trips
    mean_elec = total_elec_abs / total_trips


    result = f"""#################### Trip Statistics ####################
########## General ##########
File name:                      {fileName}
Total trips (num vehicles):     {total_trips}

Total vehicle duration (steps): {total_duration}
Mean vehicle duration (steps):  {mean_duration}

########## Emissions ##########
Total CO emitted (mg):          {total_CO_abs}
Total CO2 emitted (mg):         {total_CO2_abs}
Total HC emitted (mg):          {total_HC_abs}
Total PMx emitted (mg):         {total_PMx_abs}
Total NOx emitted (mg):         {total_NOx_abs}
Total fuel emitted (mg):        {total_fuel_abs}
Total electricity emitted (mg): {total_elec_abs}

Mean CO emitted (mg):           {mean_CO}
Mean CO2 emitted (mg):          {mean_CO2}
Mean HC emitted (mg):           {mean_HC}
Mean PMx emitted (mg):          {mean_PMx}
Mean NOx emitted (mg):          {mean_NOx}
Mean fuel emitted (mg):         {mean_fuel}
Mean electricity emitted (mg):  {mean_elec}
#########################################################"""

    with open('simulation_result.txt', 'w') as file: # file would be created if not exists
        try:
            file.write(result)
        except:
            pass