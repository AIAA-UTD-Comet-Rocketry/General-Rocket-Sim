import json
import math
from rocketpy.mathutils.function import Function
from rocketpy.motors import motor
import numpy as np
import pandas as pd

# HERE ARE THE VARIABLES YOU WILL HAVE TO CHANGE

Parameters = {}

#Non Rocket Parameters
varyingPossibilities = ["airbrake", "finposition", "weatherHour"]


Parameters["varyingVariable"] = varyingPossibilities[2]

Parameters["hasBottail"] = False

Parameters["numberSims"] = 60
Parameters["processes"] = 4

Parameters["fahrenheit_temp"] = 56
Parameters["envParams"] = {
    "latitude": 31.043722,
    "longitude": -103.532806,
    "elevation": 915,
    "type": "custom_atmosphere",
    "wind_u": 1.5,
    "wind_v": 1.5,
    "file": "ECMWF"
}




Parameters["generatedFilesLocation"] = "IrecSims/"


#motor
Parameters["dryMotorMass"] = 4.85
Parameters["propellant_mass"] = 9.26 -4.85
Parameters["grainInnerRadius"] = .02
Parameters["grainOuterRadius"] = .04
Parameters["grainHeight"] = 0.127
Parameters["the_nozzle_radius"] = 0.098 / 2
Parameters["the_throat_radius"] = .02286
Parameters["the_nozzle_position"] = Parameters["grainHeight"] * 4.25
Parameters["grain_center_of_mass_position"] = 0
Parameters["center_of_dry_mass_within_motor"] = 0
Parameters["motor_thrust_file"] = "Test Burn Csv real.csv"
Parameters["burn_time"] = 3.396
Parameters["numGrains"] = 6
Parameters["grainSeparation"] = .003175
Parameters["motorLength"] = (Parameters["grainHeight"] + Parameters["grainSeparation"]) * Parameters["numGrains"] - Parameters["grainSeparation"]
Parameters["the_motor_position"] = 2.59

#rocket general
Parameters["spMass"] = 13.9
Parameters["rocket_radius"] = 0.154686/2
Parameters["spLength"] = 0.889+1.19+0.152
Parameters["the_center_of_mass_without_motor"] = 1.6
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
Parameters["lower_railbutton_position"] = 2.79
Parameters["upper_railbutton_position"] = 1.96
Parameters["railbutton_angular_position"] = 130


#environment

#final rocket stuff
Parameters["inclination"] = 88
Parameters["heading"] = 315
Parameters["rail_length"] = 7.096

#airbrakes
Parameters["using-airbrakes"] = False
if(Parameters["using-airbrakes"]):
    Parameters["air_brake_drag"] = "ReferencedFiles/air_brake_drag_full.csv"
    Parameters["airbrake_sample_rate"] = 100 # 1 herz, so every .1 seconds
    Parameters["airbrake_clamp"] = True
    Parameters["override_rocketdrag_with_airbrakedrag"] = True
    Parameters["airbrake_area"] = 2 # in meters

# Parameters["halfway_to_target"] = 1524

lookupTable = "./ReferencedFiles/FinalLookupTable.csv"

# vel range is 0, 275

# alt range is X, 3048

minAlt = 2500
maxAlt = 3048

minVel = 0
maxVel = 275

# angleVals = [90, 85, 80, 75, 70, 65]
angleVals = [65, 70, 75, 80, 85, 90]

Parameters["parachutes"] = {}




print("YOU MUST STILL FILL IN THE FOLLOWING VARIABLES:\nVARIABLES START\n\n")


with open("ReferencedFiles/RelevantOpenRocket.json", "r") as f:
    jsonData = json.load(f)
print("Fin position is currently set to: " + str(jsonData["fin_position"]))
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

_, _, points = motor.Motor.import_eng("ReferencedFiles/" + Parameters["motor_thrust_file"])
thrust_source = points
interpolation_method = "linear"
thrust = Function(thrust_source, "Time (s)", "Thrust (N)", interpolation_method, "zero")
Parameters["impulse"] = thrust.integral(0, Parameters["burn_time"])

Parameters["spCentralAxis"] = (Parameters["rocket_radius"]**2)*Parameters["spMass"]*1/2
Parameters["spCentralDiameter"] = ((1/4)*Parameters["spMass"]*(Parameters["rocket_radius"])**2) + (1/12)*Parameters["spMass"]*(Parameters["spLength"])**2

Parameters["power_off"] = 1
Parameters["power_on"] = 1
Parameters["kelvin_temp"] = (Parameters["fahrenheit_temp"] - 32) * 5/9 + 273.15
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
def airbrake_controller_function(time, sampling_rate, state, state_history, observed_variables, air_brakes, env):
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
    print(f"The index is: {altitudeIndex}, while the number of altitudes is {len(altitudeVals)}")
    # print(altitudeVals)

    # print(f"row value we're getting is {angleIndex * numVelPoints + velocityIndex}, and column value is {altitudeIndex}")

    # should be good
    deploymentLevel = table.iloc[angleIndex * numVelPoints + velocityIndex][altitudeIndex] / 127.0


    print(f"Our aaltitude was {above_ground_altitude}, our velocity Y was {vz}, our angle was {pitch}")



    # Check if the rocket has reached burnout
    if (vz > 0 and time > Parameters["burn_time"]):
        air_brakes.deployment_level = deploymentLevel
        canDeployAirbrake = True
        print(f"WE CAN DEPLOY! Deployment level is {deploymentLevel}. Also, time is {time}, row value we're getting is {angleIndex * numVelPoints + velocityIndex}, and column value is {altitudeIndex}, as \
              angle value is {angleIndex} and velocity index is {velocityIndex}")
            
    return (
        "airbrake" + str(canDeployAirbrake),
        time,
        air_brakes.deployment_level,
        air_brakes.drag_coefficient(air_brakes.deployment_level, mach_number),
    )

Parameters["airbrake_controller_function"] = airbrake_controller_function
