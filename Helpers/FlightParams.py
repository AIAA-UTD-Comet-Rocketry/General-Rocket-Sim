from datetime import date, timedelta
import logging

from Helpers import LookupTable
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

#Non Rocket Parameters
varyingPossibilitiesName = ["Fin Position", "Day", "Hour"]
varyingPossibilitiesKeyMapping = ["fin_position", "day", "hour"]

# put the start end range (inclusive), then the # of elements you want in between them
varyingRanges = [
    [2.67, 2.92, 11],
    [0, 1, 2],
    [5, 6, 2]
]

for i in range(len(varyingRanges)):
    varyingRanges[i] = np.linspace(*varyingRanges[i]).tolist()
    if varyingPossibilitiesKeyMapping[i] == "day":
        for j in range(len(varyingRanges[i])):
            trueDate = Parameters["start_day"] + timedelta(days = j)
            varyingRanges[i][j] = [trueDate.year, trueDate.month, trueDate.day]

Parameters["iterative_variables"] = ["Day", "Hour"]

if(not Parameters["doing_monte_carlo"]):
    Parameters["iterative_variables"] = []

Parameters["readable_names"] = []
Parameters["true_names"] = []
Parameters["true_ranges"] = []
Parameters["true_current_indices"] = []

for i in range(len(Parameters["iterative_variables"])):
    try:
        currentStr = Parameters["iterative_variables"][i]
        trueIndex = varyingPossibilitiesName.index(currentStr)
        Parameters["readable_names"].append(varyingPossibilitiesName[trueIndex])
        Parameters["true_names"].append(varyingPossibilitiesKeyMapping[trueIndex])
        Parameters["true_ranges"].append(varyingRanges[trueIndex])
        Parameters["true_current_indices"].append(0)
    except ValueError:
        print("element not found! abort immedietly!")
        raise SystemExit

def UpdateIterativeVariables():
    for i in range(len(Parameters["true_names"])):
        trueParamString = Parameters["true_names"][i]
        trueIndexInRange = Parameters["true_current_indices"][i]
        trueNextVal = Parameters["true_ranges"][i][trueIndexInRange]


        Parameters[trueParamString] = trueNextVal


UpdateIterativeVariables()


Parameters["hasBottail"] = False

Parameters["obtaining_motor_csv"] = True

Parameters["numberSims"] = 5
Parameters["processes"] = 5
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




Parameters["generatedFilesLocation"] = "../Output/"


#motor
Parameters["dryMotorMass"] = 4.85
Parameters["propellant_mass"] = 9.256 - 4.853
Parameters["grainInnerRadius"] = .02
Parameters["grainOuterRadius"] = .04
Parameters["grainHeight"] = 0.127
Parameters["the_nozzle_radius"] = 0.098 / 2
Parameters["the_throat_radius"] = .02286
Parameters["the_nozzle_position"] = Parameters["grainHeight"] * 4.25
Parameters["grain_center_of_mass_position"] = 0
Parameters["center_of_dry_mass_within_motor"] = 0
Parameters["motor_thrust_file"] = "FUUUUCK.eng"
Parameters["burn_time"] = 3.35
Parameters["numGrains"] = 6
Parameters["grainSeparation"] = .003175
Parameters["motorLength"] = .914
Parameters["the_motor_position"] = 2.204 + .614/2

#rocket general
Parameters["spMass"] = 14.953
Parameters["rocket_radius"] = 0.154686/2
Parameters["spLength"] = 3.08
Parameters["the_center_of_mass_without_motor"] = 1.8
Parameters["rocket_center_of_dry_mass_position"] = Parameters["the_center_of_mass_without_motor"]
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
if(Parameters["hasBottail"]):
    Parameters["boattailPos"] = 0.813+0.152+0.305+0.508+0.864+0.152
    Parameters["boattail_bottom_radius"] = 0.129/2
    Parameters["boattail_length"] = 0.203

#parachutes
# Parameters["drogueRadius"] = 0.61/2
# Parameters["drogueCdS"] = 0.97*3.1415*(Parameters["drogueRadius"])**2
# Parameters["lightRadius"] = 3.05/2
# Parameters["lightCdS"] = 2.2*3.1415*(Parameters["lightRadius"])**2
# Parameters["lag_rec"] = 0
# Parameters["lag_se"] = 0
# Parameters["drogueTrigger"] = "apogee" 
# Parameters["lightTrigger"] = 450

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
Parameters["using-airbrakes"] = True
if(Parameters["using-airbrakes"]):
    Parameters["air_brake_drag"] = "../InputFiles/AirbrakeDrag.csv"
    Parameters["airbrake_sample_rate"] = 100 # 1 herz, so every .1 seconds
    Parameters["airbrake_clamp"] = True
    Parameters["override_rocketdrag_with_airbrakedrag"] = True
    Parameters["airbrake_area"] = 2 # in meters
    Parameters["airbrake_policy"] = LookupTable(Parameters["burn_time"])

# Parameters["halfway_to_target"] = 1524


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












# HERE ARE THE VARIABLES YOU DON'T HAVE TO CHANGE





Parameters["totalMotorMass"] = Parameters["dryMotorMass"] + Parameters["propellant_mass"]
Parameters["totalHeight"] = Parameters["grainHeight"] * Parameters["numGrains"]
# area = pi * r^2 * height
Parameters["motor_volume"] = (((np.pi * Parameters["grainOuterRadius"] ** 2) - (np.pi * Parameters["grainInnerRadius"] ** 2)) * Parameters["totalHeight"])
Parameters["motor_11_inertia"] = (1/12)*Parameters["dryMotorMass"]*(Parameters["grainOuterRadius"])**2
Parameters["motor_density"] = Parameters["propellant_mass"]/Parameters["motor_volume"]
Parameters["motor_33_inertia"] = ((1/4)*Parameters["dryMotorMass"]*(Parameters["grainOuterRadius"])**2) + (1/12)*Parameters["dryMotorMass"]*(Parameters["motorLength"])**2
Parameters["the_motor_center_of_dry_mass_position"] = Parameters["the_motor_position"]

_, _, points = motor.Motor.import_eng("../InputFiles/" + Parameters["motor_thrust_file"])
points = np.asarray(points, dtype=float)
_, unique_indices = np.unique(points[:, 0], return_index=True)
points = points[np.sort(unique_indices)].tolist()
interpolation_method = "linear"
thrust = Function(points, "Time (s)", "Thrust (N)", interpolation_method, "zero")
Parameters["impulse"] = thrust.integral(0, Parameters["burn_time"])

print(f"Impulse is: {Parameters['impulse']}")

Parameters["spCentralAxis"] = (Parameters["rocket_radius"]**2)*Parameters["spMass"]*1/2
Parameters["spCentralDiameter"] = ((1/4)*Parameters["spMass"]*(Parameters["rocket_radius"])**2) + (1/12)*Parameters["spMass"]*(Parameters["spLength"])**2

Parameters["power_off"] = 1
Parameters["power_on"] = 1
Parameters["nose_position"] = 0



def calcKelvinfromFahrenheit(fTemp):
    return (fTemp - 32) * 5/9 + 273.15

Parameters["airbrake_controller_function"] = airbrake_controller_function

newTempArr = []
if isinstance(Parameters["fahrenheit_temp"], float) or isinstance(Parameters["fahrenheit_temp"], int):
    Parameters["temperature"] = calcKelvinfromFahrenheit(Parameters["fahrenheit_temp"])
else:
    for i in range(0, len(Parameters["fahrenheit_temp"]), 1):
        newTempArr.append((Parameters["fahrenheit_temp"][i][0], calcKelvinfromFahrenheit(Parameters["fahrenheit_temp"][i][1])))
    Parameters["temperature"] = newTempArr

Parameters["monte_carlo_parameters"] = {
    # Rocket's dry mass without motor (kg) and its uncertainty (standard deviation)
    "rocket_mass": (Parameters["spMass"], 4), #.001
    # # Rocket's inertia moment perpendicular to its axis (kg*m^2)
    "rocket_inertia_11": (Parameters["spCentralDiameter"], 0.5),
    # # Rocket's inertia moment relative to its axis (kg*m^2)
    "rocket_inertia_33": (Parameters["spCentralAxis"], 0.5),
    # Motors's dry mass without propellant (kg) and its uncertainty (standard deviation)
    "motor_dry_mass": (Parameters["dryMotorMass"], 0), #.001
    # # Motor's dry inertia moment perpendicular to its axis (kg*m^2)
    "motor_inertia_11": (Parameters["motor_11_inertia"], 0),
    # # Motors's dry inertia moment relative to its axis (kg*m^2)
    "motor_inertia_33": (Parameters["motor_33_inertia"], 0),\
    # Distance between rocket's center of dry mass and motor's center of dry mass (m)
    # THIS is likely wrong, go back to check it

    "motor_dry_mass_position": (np.abs(Parameters["the_motor_center_of_dry_mass_position"] - Parameters["rocket_center_of_dry_mass_position"]), 0), #.001
    # Motor total impulse (N*s)
    "impulse": (Parameters["impulse"], 100), #25.3

    "motor_position": (Parameters["the_motor_position"], 0),

    # Motor burn out time (s)
    "burn_time": (Parameters["burn_time"], 1),
    # Motor's nozzle radius (m)
    "nozzle_radius": (Parameters["the_nozzle_radius"], 0), #.5 / 1000
    # Motor's nozzle throat radius (m)
    "throat_radius": (Parameters["the_throat_radius"], 0), #.5 / 1000
    # Motor's grain separation (axial distance between two grains) (m)
    "grain_separation": (Parameters["grainSeparation"], 0),
    # Motor's grain density (kg/m^3)
    "grain_density": (Parameters["motor_density"], 0), #20
    # Motor's grain outer radius (m)
    "grain_outer_radius": (Parameters["grainOuterRadius"], 0),
    # Motor's grain inner radius (m)
    "grain_initial_inner_radius": (Parameters["grainInnerRadius"], 0), #.3 / 1000
    # Motor's grain height (m)
    "grain_initial_height": (Parameters["grainHeight"], 0), #1 / 1000
    # Rocket's radius (kg*m^2)
    "radius": (Parameters["rocket_radius"], 0),
    # Nozle position relative to motor
    "nozzle_position": (Parameters["the_nozzle_position"], 0),
    # Distance between rocket's center of dry mass and and center of propellant mass (m) (negative)
    "grains_center_of_mass_position": (Parameters["rocket_center_of_dry_mass_position"]-(Parameters["the_motor_center_of_dry_mass_position"] + Parameters["the_motor_position"]), 0), #.0001
    # Axial distance between rocket's center of dry mass and nearest point in its nose cone (m)
    "nose_distance_to_CM": (Parameters["rocket_center_of_dry_mass_position"]-Parameters["nose_cone_length"], 0),
    # Launch rail inclination angle relative to the horizontal plane (degrees)
    "inclination": (Parameters["inclination"], 15), #1
    # Launch rail heading relative to north (degrees)
    "heading": (Parameters["heading"], 15), #2

    # # Drag coefficient times reference area for the drogue chute (m^2)
    # "cd_s_drogue": (FlightParams.Parameters["drogueCdS"], 0), #.02
    # # Drag coefficient times reference area for the light chute
    # "cd_s_light": (FlightParams.Parameters["lightCdS"], 0), #.02
    # # Time delay between parachute ejection signal is detected and parachute is inflated (s)
    # "lag_rec": (FlightParams.Parameters["lag_rec"], 0), #.2
    # # Time delay between sensor signal is received and ejection signal is fired (s)
    # "lag_se": (FlightParams.Parameters["lag_se"], 0), #.1

    # temperature in kelvin
    "temperature": (Parameters["temperature"], 0), #5
    # atmospheric pessure in pascals
    "atmosphere_pressure": (env.pressure_ISA(Parameters["elevation"]), 0), #300

    #without motor
    "rocket_CM": (Parameters["rocket_center_of_dry_mass_position"], 0), #.01

    # adding these, but they don't vary
    "time_to_deploy_airbrake_after_burnout": (0.1, 0),
    "fin_position": (2.62, 0)
}

if(Parameters["doing_monte_carlo"]):
    pass
else:
    for key in Parameters["monte_carlo_parameters"].keys():
        value = Parameters["monte_carlo_parameters"][key]
        Parameters["monte_carlo_parameters"][key] = (value[0], 0)


#sets up the ability to log inputs.
def setup_logging():
    class MyHandler(logging.FileHandler):
        def emit(self, record):
            super().emit(record)  # Call the superclass's emit method
            self.flush()  # Flush after each log message

    # Use your custom handler
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    handler = MyHandler('app.log', 'a')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# note: returns whether or not we're fully done
def UpdateIndices():
    for i in range(len(Parameters["true_names"]) - 1, -1, -1):
        if(Parameters["true_current_indices"][i] < len(Parameters["true_ranges"][i]) - 1):
            Parameters["true_current_indices"][i] += 1
            return False
        else:
            Parameters["true_current_indices"][i] = 0

    return True

def NextIteration():
    everythingFinished = UpdateIndices()
    if everythingFinished:
        return True

    UpdateIterativeVariables()
    return False