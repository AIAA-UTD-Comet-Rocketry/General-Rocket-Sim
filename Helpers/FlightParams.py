from datetime import date
import logging
from scipy.stats import norm
from matplotlib import pyplot as plt

from rocketpy import Environment
import json
import math
from rocketpy.mathutils.function import Function
from rocketpy.motors import motor
import numpy as np
import pandas as pd
import requests
from Helpers.GetWeatherData import GetWeatherData

# HERE ARE THE VARIABLES YOU WILL HAVE TO CHANGE

Parameters = {}

#Non Rocket Parameters
varyingPossibilities = ["Fin Position", "Hour", "Day"]
varyingPossibilitiesKeyMapping = ["fin_position", "hour", "day"]

# put the start end range (inclusive), then the # of elements you want in between them
varyingRanges = [
    [2.67, 2.92, 11],
    [0, 7, 8],
    [5, 15, 11]
]


Parameters["iterative_variables"] = [varyingPossibilities[2], varyingPossibilities[1]]

Parameters["hasBottail"] = False

Parameters["obtaining_motor_csv"] = True

Parameters["numberSims"] = 200
Parameters["processes"] = 10
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
Parameters["day"] = date.today()
Parameters["hour"] = 14

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

# Parameters["halfway_to_target"] = 1524

lookupTable = "../InputFiles/FinalLookupTable.csv"

# vel range is 0, 275

# alt range is X, 3048

minAlt = 2500
maxAlt = 3048

minVel = 0
maxVel = 275

# angleVals = [90, 85, 80, 75, 70, 65]
angleVals = [65, 70, 75, 80, 85, 90]

Parameters["parachutes"] = {}

launchDate = [2025, 6, 12, 8]

# Iterate the loop to read the cell values
env = Environment(
    date=launchDate,
    latitude=Parameters["latitude"],
    longitude=Parameters["longitude"],
)

#env = Environment(latitude = FlightParams.envParams["latitude"], longitude = FlightParams.envParams["longitude"], elevation = FlightParams.envParams["elevation"])


Parameters["doing_monte_carlo"] = False
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

def getPitch(q):
    def quat_conjugate(q):
        w, x, y, z = q
        return np.array([w, -x, -y, -z])

    def quat_mul(a, b):
        aw, ax, ay, az = a
        bw, bx, by, bz = b
        return np.array([
            aw*bw - ax*bx - ay*by - az*bz,
            aw*bx + ax*bw + ay*bz - az*by,
            aw*by - ax*bz + ay*bw + az*bx,
            aw*bz + ax*by - ay*bx + az*bw
        ])

    def rotate_vector_by_quat(v, q):
        qv = np.array([0.0, v[0], v[1], v[2]])
        qc = quat_conjugate(q)
        return quat_mul(quat_mul(q, qv), qc)[1:]  # vector part

    # World up vector
    up = np.array([0.0, 0.0, 1.0])
    obj_up = rotate_vector_by_quat(up, q)

    # Angle from flat plane (XY plane)
    theta = np.arccos(np.clip(obj_up[2], -1.0, 1.0))  # radians
    pitch = np.degrees(theta)
    return 90 - pitch

# note: when getting our csv, check it against min and max values. 
# altitude is column, velocity row

table = pd.read_csv(lookupTable, header=None)

numVelPoints = int(table.shape[0] / len(angleVals))
numAltPoints = table.shape[1]

velIncrementAmount = (maxVel - minVel) / (numVelPoints - 1)
altIncrementAmount = (maxAlt - minAlt) / (numAltPoints - 1)

velocityVals = np.linspace(minVel, maxVel, numVelPoints)
altitudeVals = np.linspace(minAlt, maxAlt, numAltPoints)
# altitudeVals = np.arange(minAlt, maxAlt + 1, altIncrementAmount)

numAngles = len(angleVals)

def closerIndex(arr, val, smallerIndex, largerIndex):
    distI = val - arr[smallerIndex]
    distJ = arr[largerIndex] - val
    return (smallerIndex if distI < distJ else largerIndex)

# binary searches to find ideal index
def binarySearch(arr, val, i, j):
    # if down to last two elements, take closest one instead
    if(i + 1 == j):
        return closerIndex(arr, val, i, j)

    midIndex = (j + i) // 2

    # typical binary search activities
    if(arr[midIndex] == val):
        return midIndex
    elif(val > arr[midIndex]):
        return binarySearch(arr, val, midIndex, j)
    else:
        return binarySearch(arr, val, i, midIndex)

# airbrake_deploy_altitude = 2000
def airbrake_controller_function(time, sampling_rate, state, state_history, observed_variables, air_brakes, sensors, env):
    canDeployAirbrake = False

    # deployment_time = air_brakes.airbrake_deploy_time

    # state = [x, y, z, vx, vy, vz, e0, e1, e2, e3, wx, wy, wz]
    altitude_ASL = state[2]
    above_ground_altitude = altitude_ASL - env.elevation
    vx, vy, vz = state[3], state[4], state[5]
    e0, e1, e2, e3 = state[6], state[7], state[8], state[9]

    print(f"E0: {e0}, E1: {e1}, E2: {e2}, E3: {e3}")


    # Get winds in x and y directions
    wind_x, wind_y = env.wind_velocity_x(altitude_ASL), env.wind_velocity_y(altitude_ASL)

    y_velocity = abs(vy - wind_y)

    # Calculate Mach number, by first getting entire speed
    free_stream_speed = (
        (wind_x - vx) ** 2 + (wind_y - vy) ** 2 + (vz) ** 2
    ) ** 0.5
    mach_number = free_stream_speed / env.speed_of_sound(altitude_ASL)

    # Get previous state from state_history
    previous_state = state_history[-1]
    previous_vz = previous_state[5]

    # If we wanted to we could get the returned values from observed_variables:
    # returned_time, deployment_level, drag_coefficient = observed_variables[-1]

    # Example quaternion in (w, x, y, z)
    pitch = getPitch(np.array([e0, e1, e2, e3]))  # ~15° rotation around Y

    print("Angle from flat plane (deg):", pitch)

    # ALTITUDES IS COLUMN, VELCOITIES IS ROWS


    # gets closest index to this angle
    angleIndex = binarySearch(angleVals, pitch, 0, numAngles - 1)
    velocityIndex = binarySearch(velocityVals, vz, 0, numVelPoints - 1)
    altitudeIndex = binarySearch(altitudeVals, above_ground_altitude, 0, numAltPoints - 1)

    altitudeIndex = len(altitudeVals) - altitudeIndex - 1
    angleIndex = len(angleVals) - angleIndex - 1

    print(f"The goddamn altitude: {above_ground_altitude}")
    print(f"The altitude index is: {altitudeIndex}, while the number of altitudes is {len(altitudeVals)}")
    print(f"The velocity index is: {velocityIndex}, while the number of altitudes is {len(velocityVals)}")
    # print(altitudeVals)

    # print(f"row value we're getting is {angleIndex * numVelPoints + velocityIndex}, and column value is {altitudeIndex}")

    # should be good
    deploymentLevel = table.iloc[angleIndex * numVelPoints + velocityIndex][altitudeIndex] / 127.0


    print(f"Our aaltitude was {above_ground_altitude}, our velocity Y was {vz}, our angle was {pitch}")



    # Check if the rocket has reached burnout
    if (vz > 0 and time > Parameters["burn_time"]):
        air_brakes.deployment_level = deploymentLevel
        canDeployAirbrake = True
        print(f"WE CAN DEPLOY! Deployment level is {air_brakes.deployment_level}. Also, time is {time}, row value we're getting is {angleIndex * numVelPoints + velocityIndex}, and column value is {altitudeIndex}, as \
              angle value is {angleIndex} and velocity index is {velocityIndex}")
            
    return (
        "airbrake" + str(canDeployAirbrake),
        time,
        air_brakes.deployment_level,
        air_brakes.drag_coefficient(air_brakes.deployment_level, mach_number),
    )

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


def createDistributionPlot(resultsFile, dispersonResultArray, name, lowerProbBound, upperProbBound, maxDecimals, percentConfidence, hypothesis, unit, makeGraph, filename):
    mean = np.mean(dispersonResultArray)
    deviation = np.std(dispersonResultArray)
    unitString = ""
    if(unit == "meters"):
        unitString = "m"
    print(
        f'{name} -         Mean Value: {mean:0.3f} ' + unitString
    )
    resultsFile.write(f'{name} -         Mean Value: {mean:0.3f} ' + unitString + "\n")
    print(
        f'{name} - Standard Deviation: {deviation:0.3f} m' + unitString
    )
    resultsFile.write(f'{name} - Standard Deviation: {deviation:0.3f} m' + unitString + "\n")
    if(makeGraph):

        print(f"Arr: {dispersonResultArray}")
        minimum = np.min(dispersonResultArray)
        maximum = np.max(dispersonResultArray)
        theBins = list()

        #using scott's rule to find the number of bins
        binWidth = 3.5 * deviation / np.power(len(dispersonResultArray), 1/3)
        numBins = int(np.round((maximum-minimum)/binWidth))

        changeInZ = (maximum - minimum) / numBins
        #test add
        zIterator = minimum
        for iterator in range(numBins):
            theBins.append(zIterator)
            zIterator += changeInZ
        finalValue = np.ceil(zIterator * np.power(10, maxDecimals)) / np.power(10, maxDecimals)
        theBins.append(finalValue)
        plt.figure()
        plt.xlim(minimum, maximum)
        minTextSize = 8
        maxTickCount = 50
        xTickBins = theBins
        if(numBins > maxTickCount):
            xTickBins = list()
            changeInZ = (maximum - minimum) / 50.0
            zIterator = minimum
            for iterator in range(50):
                xTickBins.append(zIterator)
                zIterator += changeInZ
        binListToString = list()
        for currentBin in xTickBins:
            binListToString.append(str(round(currentBin, maxDecimals)))
        plt.xticks(ticks = xTickBins, labels = binListToString, rotation = 75, fontsize = minTextSize)
        plt.hist(dispersonResultArray, bins=theBins)
        plt.title(name)
        plt.xlabel(name)
        plt.ylabel("Number of Occurences")

        plt.axvline(mean, color='k', linestyle='solid', linewidth=4)
        plt.axvline(mean - deviation, color='g', linestyle='solid', linewidth=3)
        plt.axvline(mean - 2*deviation, color='g', linestyle='solid', linewidth=3)
        plt.axvline(mean - 3*deviation, color='g', linestyle='solid', linewidth=3)
        plt.axvline(mean + deviation, color='g', linestyle='solid', linewidth=3)
        plt.axvline(mean + 2*deviation, color='g', linestyle='solid', linewidth=3)
        plt.axvline(mean + 3*deviation, color='g', linestyle='solid', linewidth=3)
        plt.savefig(Parameters["generatedFilesLocation"] + str(filename) + "Graph.png", bbox_inches="tight", pad_inches=0)
        plt.show()
    lowerZ = (lowerProbBound - mean)/deviation
    upperZ = (upperProbBound - mean)/deviation
    probabilityInRange = norm.cdf(upperZ) - norm.cdf(lowerZ)
    print("PROBABILITY THE " + name +  " IS IN BETWEEN " + str(round(lowerProbBound, 4)) + " AND " + str(round(upperProbBound, 4)) + " IS: " + str(round(probabilityInRange * 100, 2)) + "%")
    resultsFile.write("PROBABILITY THE " + name +  " IS IN BETWEEN " + str(round(lowerProbBound, 4)) + " AND " + str(round(upperProbBound, 4)) + " IS: " + str(round(probabilityInRange * 100, 2)) + "%\n")
    if(percentConfidence != 100):
        aVal = (100 - percentConfidence)/100
        newZ = np.abs(norm.ppf(aVal/2))
        lowerBoundOfInterval = mean - newZ * deviation/np.sqrt(len(dispersonResultArray))
        upperBoundOfInterval = mean + newZ * deviation/np.sqrt(len(dispersonResultArray))
        print("There is a " + str(percentConfidence) + f"% chance that the mean of the " + name + 
              " falls within THIS RANGE: " + str(lowerBoundOfInterval) + ", " + str(upperBoundOfInterval))
        resultsFile.write("There is a " + str(percentConfidence) + f"% chance that the mean of the " + name + 
              " falls within THIS RANGE: " + str(lowerBoundOfInterval) + ", " + str(upperBoundOfInterval) + "\n")
        if(hypothesis != None):
            criticalValue = norm.ppf(aVal / 2)
            testStatistic = (mean - hypothesis) * np.sqrt(len(dispersonResultArray))/deviation
            print("\nWe have the hypothesis that our mean is greater than or equal to " + str(hypothesis) + ". With our critical percent, our critical value is " +
                str(criticalValue) + ". Then, our test statistic is " + str(testStatistic))
            resultsFile.write("\nWe have the hypothesis that our mean is greater than or equal to " + str(hypothesis) + ". With our critical percent, our critical value is " +
                str(criticalValue) + ". Then, our test statistic is " + str(testStatistic) + "\n")
            if(testStatistic < criticalValue):
                print("Since our test statistic is more extreme than our critical value, we can reject the null hypothesis that the mean is " + str(hypothesis) + ".\n")
                resultsFile.write("Since our test statistic is more extreme than our critical value, we can reject the null hypothesis that the mean is " + str(hypothesis) + ".\n\n")
            else:
                print("Since our test statistic is less extreme than our critical value, we can NOT reject the null hypothesis that the mean is " + str(hypothesis) + ".\n")
                resultsFile.write("Since our test statistic is less extreme than our critical value, we can NOT reject the null hypothesis that the mean is " + str(hypothesis) + ".\n\n")

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

def SetNewValuesForIteration(nextIndex):
    for 