from datetime import date, timedelta
import logging

from Helpers.IterationManager import IterationManager
from Helpers.MonteCarloManager import MonteCarloManager
from Helpers.LookupTable import LookupTable
from rocketpy import Environment
import json
from rocketpy.mathutils.function import Function
from rocketpy.motors import motor
import numpy as np
import pandas as pd
from Helpers.GetWeatherData import GetWeatherData

# HERE ARE THE VARIABLES YOU WILL HAVE TO CHANGE

Parameters = {}

Parameters["start_day"] = date.today()

Parameters["day"] = [Parameters["start_day"].year, Parameters["start_day"].month, Parameters["start_day"].day]
Parameters["hour"] = 14
Parameters["doing_monte_carlo"] = True


Parameters["has_bottail"] = False

Parameters["obtaining_motor_csv"] = True

Parameters["latitude"] = 31.043722
Parameters["longitude"] = -103.532806

# elevation was 750 meters
'''
url = f"https://openzenith.cyopsys.com/api/elevation?lat={Parameters['latitude']}&lon={Parameters['longitude']}"
response = requests.get(url, timeout=10)
print("URL:", response.url)
print("Status:", response.status_code)
print("Content-Type:", response.headers.get("Content-Type"))
print("Response:", repr(response.text[:1000]))

returnedData = response.json()

print(returnedData["elevation"])

Parameters["elevation"] = returnedData["elevation"]
'''
Parameters["elevation"] = 750

Parameters["atmosphere_type"] = "standard_atmosphere"
Parameters["env_file"] = None


Parameters["fahrenheit_temp"] = 67
Parameters["pressure"] = None
Parameters["wind_u"] = None
Parameters["wind_v"] = None

# (year, month, day, hour)

if(Parameters["atmosphere_type"] == "custom_atmosphere"):
    Parameters["pressure"], Parameters["fahrenheit_temp"], Parameters["wind_u"], Parameters["wind_v"] = GetWeatherData(Parameters["date"], Parameters["latitude"], Parameters["longitude"])




Parameters["generated_files_location"] = "../Output/"


#motor
Parameters["motor_dry_mass"] = 4.85
Parameters["propellant_mass"] = 9.256 - 4.853
Parameters["grain_inner_radius"] = .02
Parameters["grain_outer_radius"] = .04
Parameters["grain_height"] = 0.127
Parameters["nozzle_radius"] = 0.098 / 2
Parameters["throat_radius"] = .02286
Parameters["nozzle_position"] = Parameters["grain_height"] * 4.25
Parameters["grain_center_of_mass_position"] = 0
Parameters["center_of_dry_mass_within_motor"] = 0
Parameters["motor_thrust_file"] = "FUUUUCK.eng"
Parameters["burn_time"] = 3.35
Parameters["num_grains"] = 6
Parameters["grain_separation"] = .003175
Parameters["motor_position"] = 2.204 + .614/2

#rocket general
Parameters["rocket_mass"] = 14.953
Parameters["rocket_radius"] = 0.154686/2
Parameters["rocket_length"] = 3.08
Parameters["center_of_mass_without_motor"] = 1.8
Parameters["rocket_center_of_dry_mass_position"] = Parameters["center_of_mass_without_motor"]
Parameters["power_off_file"] = "2026LSCCDOFF.csv"
Parameters["power_on_file"] = "2026LSCCDON.csv"

#nose cone
Parameters["nose_cone_length"] = 0.813
Parameters["nose_cone_type"] = "von karman"

#fins
Parameters["fin_position"] = 2.78
Parameters["fin_span"] = 0.216
Parameters["root_chord"] =0.279
Parameters["tip_chord"] = 0.091
Parameters["fin_cant_angle"] = 0
Parameters["fin_sweep_length"] = 0.173
Parameters["num_fins"] = 4

#bottail
if(Parameters["has_bottail"]):
    Parameters["bottail_pos"] = 0.813+0.152+0.305+0.508+0.864+0.152
    Parameters["bottail_bottom_radius"] = 0.129/2
    Parameters["bottail_length"] = 0.203

#rail buttons
Parameters["lower_railbutton_position"] = 3.01
Parameters["upper_railbutton_position"] = 3.01 - 0.952
Parameters["railbutton_angular_position"] = 150


#environment

#final rocket stuff
Parameters["inclination"] = 84
Parameters["heading"] = 240
Parameters["rail_length"] = 7.096

#airbrakes
Parameters["using_airbrakes"] = True

if(Parameters["using_airbrakes"]):
    Parameters["air_brake_drag"] = "../InputFiles/AirbrakeDrag.csv"
    Parameters["airbrake_sample_rate"] = 100 # 1 herz, so every .1 seconds
    Parameters["airbrake_clamp"] = True
    Parameters["override_rocket_drag"] = True
    Parameters["airbrake_area"] = 2 # in meters
    Parameters["airbrake_policy"] = LookupTable(Parameters["burn_time"])


Parameters["parachutes"] = {}

launchDate = [2025, 6, 12, 8]

# Iterate the loop to read the cell values
env = Environment(
    date=launchDate,
    latitude=Parameters["latitude"],
    longitude=Parameters["longitude"],
)

#env = Environment(latitude = FlightParams.envParams["latitude"], longitude = FlightParams.envParams["longitude"], elevation = FlightParams.envParams["elevation"])


Parameters["terminate_at_apogee"] = False

print("YOU MUST STILL FILL IN THfE FOLLOWING VARIABLES:\nVARIABLES START\n\n")


with open("../InputFiles/RelevantOpenRocket.json", "r") as f:
    jsonData = json.load(f)
for key in Parameters:
    # first do something like check if rail_position, if so get rail_id and from that do f"rail_{rail_id}_mass"
    # or something like that
    
    if key in jsonData:
        # print(f"Found {key} in the json, setting it now!")
        Parameters[key] = jsonData[key]
    else:
        print(f"{key},")

print("\n\nVARIABLES END\n\n")







Parameters["rocket_axis"] = (Parameters["rocket_radius"]**2)*Parameters["rocket_mass"]*1/2


Parameters["rocket_inertia_11"] = Parameters["rocket_radius"] * 2
Parameters["rocket_inertia_33"] = Parameters["rocket_axis"]

Parameters["total_motor_mass"] = Parameters["motor_dry_mass"] + Parameters["propellant_mass"]
Parameters["motor_length"] = Parameters["grain_height"] * Parameters["num_grains"]
# area = pi * r^2 * height
Parameters["motor_volume"] = (((np.pi * Parameters["grain_outer_radius"] ** 2) - (np.pi * Parameters["grain_inner_radius"] ** 2)) * Parameters["motor_length"])
Parameters["motor_inertia_11"] = (1/12)*Parameters["motor_dry_mass"]*(Parameters["grain_outer_radius"])**2
Parameters["motor_density"] = Parameters["propellant_mass"]/Parameters["motor_volume"]
Parameters["motor_inertia_33"] = ((1/4)*Parameters["motor_dry_mass"]*(Parameters["grain_outer_radius"])**2) + (1/12)*Parameters["motor_dry_mass"]*(Parameters["motor_length"])**2
Parameters["the_motor_center_of_dry_mass_position"] = Parameters["motor_position"]

_, _, points = motor.Motor.import_eng("../InputFiles/" + Parameters["motor_thrust_file"])
points = np.asarray(points, dtype=float)
_, unique_indices = np.unique(points[:, 0], return_index=True)
points = points[np.sort(unique_indices)].tolist()
interpolation_method = "linear"
thrust = Function(points, "Time (s)", "Thrust (N)", interpolation_method, "zero")
Parameters["impulse"] = thrust.integral(0, Parameters["burn_time"])

print(f"Impulse is: {Parameters['impulse']}")

Parameters["power_off"] = 1
Parameters["power_on"] = 1
Parameters["nose_position"] = 0

Parameters["atmosphere_pressure"] = env.pressure_ISA(Parameters["elevation"])


def calcKelvinfromFahrenheit(fTemp):
    return (fTemp - 32) * 5/9 + 273.15

newTempArr = []
if isinstance(Parameters["fahrenheit_temp"], float) or isinstance(Parameters["fahrenheit_temp"], int):
    Parameters["temperature"] = calcKelvinfromFahrenheit(Parameters["fahrenheit_temp"])
else:
    for i in range(0, len(Parameters["fahrenheit_temp"]), 1):
        newTempArr.append((Parameters["fahrenheit_temp"][i][0], calcKelvinfromFahrenheit(Parameters["fahrenheit_temp"][i][1])))
    Parameters["temperature"] = newTempArr

Parameters["monte_carlo"] = MonteCarloManager(Parameters, Parameters["doing_monte_carlo"])


if(Parameters["doing_monte_carlo"]):
    Parameters["iterative_handler"] = IterationManager(Parameters["start_day"])
    Parameters["iterative_handler"].UpdateIterativeVariables(Parameters)