import math
from rocketpy.mathutils.function import Function
from rocketpy.motors import motor
import numpy as np
import pandas as pd
import bisect

# HERE ARE THE VARIABLES YOU WILL HAVE TO CHANGE

#other stuff
varyingPossibilities = ["airbrake", "finposition", "weatherHour"]
varyingVariable = varyingPossibilities[2]

numberSims = 40
processes = 10

latitude = 31.0437
longitude = -103.532806

generatedFilesLocation ="IrecSims/"

#motor
propellant_mass = 10.476-5.578
dryMotorMass = 5.578
grainInnerRadius = .02921/2
grainOuterRadius = .0806/2
grainHeight = 0.12488164
the_nozzle_radius = .05224
the_throat_radius= .0216
the_nozzle_position = grainHeight * 4.25
grain_center_of_mass_position = 0
center_of_dry_mass_within_motor = 0
motor_thrust_file = "updatedthrustcurve.csv"
burn_time = 3.611
numGrains = 6
grainSeparation = .003175
motorLength = (grainHeight + grainSeparation) * numGrains - grainSeparation

#rocket general
spMass = 17.052
spRadius = 0.154686/2
spLength = 0.152+0.305+0.508+0.864+0.152
the_center_of_mass_without_motor = 1.78
power_off_file = "Sp25CDOFF4.24.csv"
power_on_file = "Sp25CDON4.24.csv"

#nose cone
nose_cone_length = .813
nose_cone_type = "von karman"

#fins
the_fin_position = 2.57
finSpan = 0.216
root_chord=0.279
tip_chord=0.091
fin_cant_angle = 0
fin_sweep_length = 0.173
numFins = 4

#bottail
boattailPos = 0.813+0.152+0.305+0.508+0.864+0.152
boattail_bottom_radius = 0.129/2
bottail_length = 0.203

#parachutes
drogueRadius = 0.61/2
drogueCdS = 0.97*3.1415*(drogueRadius)**2
lightRadius = 3.05/2
lightCdS = 2.2*3.1415*(lightRadius)**2
lag_rec = 0
lag_se = 0
drogueTrigger = "apogee"
lightTrigger = 450

#rail buttons
lower_railbutton_position = 2.79
upper_railbutton_position = 1.96
railbutton_angular_position = 130


#environment
fahrenheit_temp = 85
envParams = {
    "latitude": 31.043722,
    "longitude": -103.532806,
    "elevation": 915,
    "type": "standard_atmosphere",
    "file": "ECMWF"
}

#final rocket stuff
inclination = 89
heading = 90
rail_length = 4.1416

#airbrakes
air_brake_drag_file = "ReferencedFiles/AirbrakeDrag.csv"
airbrake_sample_rate = 100 # 1 herz, so every .1 seconds
airbrake_clamp = True
override_rocketdrag_with_airbrakedrag = True
airbrake_area = 2 # in meters

halfway_to_target = 1524

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

lookupTable = "./FinalLookupTable.csv"
table = pd.read_csv(lookupTable, header=None)

# vel range is 0, 275

# alt range is X, 3048

minAlt = 2500
maxAlt = 3048

minVel = 0
maxVel = 275




angleVals = [90, 85, 80, 75, 70, 65]

numVelPoints = 100
numAltPoints = 100

velIncrementAmount = (maxVel - minVel) / (numVelPoints - 1)
altIncrementAmount = (maxAlt - minAlt) / (numAltPoints - 1)

velocityVals = [vel for vel in np.arange(minVel, maxVel + 1, velIncrementAmount)]
altitudeVals = np.arange(minAlt, maxAlt + 1, altIncrementAmount)

numAngles = len(angleVals)
numVelocities = len(velocityVals)
numAltitudes = len(altitudeVals)

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
    velocityIndex = binarySearch(velocityVals, vz, 0, numVelocities - 1)
    altitudeIndex = binarySearch(altitudeVals, above_ground_altitude, 0, numAltitudes - 1)

    altitudeIndex = len(altitudeVals) - altitudeIndex - 1

    print(f"The goddamn altitude: {above_ground_altitude}")
    print(f"The index is: {altitudeIndex}")
    print("Altitude array:")
    print(altitudeVals)

    deploymentLevel = table.iloc[angleIndex * numVelocities + velocityIndex][altitudeIndex]


    print(f"Our aaltitude was {above_ground_altitude}, our velocity Y was {vz}, our angle was {pitch}")



    # Check if the rocket has reached burnout
    if (vy > 0 and time > burn_time):
        air_brakes.deployment_level = deploymentLevel
        canDeployAirbrake = True
        print(f"WE CAN DEPLOY! Deployment level is {deploymentLevel}")
    
    return (
        "airbrake" + str(canDeployAirbrake),
        time,
        air_brakes.deployment_level,
        air_brakes.drag_coefficient(air_brakes.deployment_level, mach_number),
    )





# HERE ARE THE VARIABLES YOU DON'T HAVE TO CHANGE
totalMotorMass = dryMotorMass + propellant_mass
totalHeight = grainHeight * numGrains
# area = pi * r^2 * height
motor_volume = (((np.pi * grainOuterRadius ** 2) - (np.pi * grainInnerRadius ** 2)) * totalHeight)
motor_11_inertia = (1/12)*dryMotorMass*(grainOuterRadius)**2
motor_density = propellant_mass/motor_volume
motor_33_inertia = ((1/4)*dryMotorMass*(grainOuterRadius)**2) + (1/12)*dryMotorMass*(motorLength)**2
the_motor_position = spLength + nose_cone_length + grainHeight/2 - (totalHeight)/2
the_motor_center_of_dry_mass_position = the_motor_position

_, _, points = motor.Motor.import_eng("ReferencedFiles/" + motor_thrust_file)
thrust_source = points
interpolation_method = "linear"
thrust = Function(thrust_source, "Time (s)", "Thrust (N)", interpolation_method, "zero")
impulse = thrust.integral(0, burn_time)

spCentralAxis = (spRadius**2)*spMass*1/2
spCentralDiameter = ((1/4)*spMass*(spRadius)**2) + (1/12)*spMass*(spLength)**2
rocket_center_of_dry_mass_position = (the_center_of_mass_without_motor * spMass + the_motor_center_of_dry_mass_position * dryMotorMass) / (dryMotorMass + spMass)

power_off = 1
power_on = 1
kelvin_temp = (fahrenheit_temp - 32) * 5/9 + 273.15
nose_position = 0