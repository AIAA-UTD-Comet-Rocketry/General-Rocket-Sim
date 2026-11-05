import numpy as np
import pandas as pd
from Helpers.Airbrakes import Airbrake

class LookupTable(Airbrake):
    def __init__(self, burnoutTime):
        lookupTable = "../InputFiles/FinalLookupTable.csv"

        minAlt = 2500
        maxAlt = 3048

        minVel = 0
        maxVel = 275

        # angleVals = [90, 85, 80, 75, 70, 65]
        self.angleVals = [65, 70, 75, 80, 85, 90]

        # note: when getting our csv, check it against min and max values. 
        # altitude is column, velocity row

        self.table = pd.read_csv(lookupTable, header=None)

        self.numVelPoints = int(self.table.shape[0] / len(self.angleVals))
        self.numAltPoints = self.table.shape[1]

        velIncrementAmount = (maxVel - minVel) / (self.numVelPoints - 1)
        altIncrementAmount = (maxAlt - minAlt) / (self.numAltPoints - 1)

        self.velocityVals = np.linspace(minVel, maxVel, self.numVelPoints)
        self.altitudeVals = np.linspace(minAlt, maxAlt, self.numAltPoints)
        # altitudeVals = np.arange(minAlt, maxAlt + 1, altIncrementAmount)

        self.numAngles = len(self.angleVals)

        super().__init__(burnoutTime)

    def closerIndex(self, arr, val, smallerIndex, largerIndex):
        distI = val - arr[smallerIndex]
        distJ = arr[largerIndex] - val
        return (smallerIndex if distI < distJ else largerIndex)

    # binary searches to find ideal index
    def binarySearch(self, arr, val, i, j):
        # if down to last two elements, take closest one instead
        if(i + 1 == j):
            return self.closerIndex(arr, val, i, j)

        midIndex = (j + i) // 2

        # typical binary search activities
        if(arr[midIndex] == val):
            return midIndex
        elif(val > arr[midIndex]):
            return self.binarySearch(arr, val, midIndex, j)
        else:
            return self.binarySearch(arr, val, i, midIndex)

    # airbrake_deploy_altitude = 2000
    def airbrake_controller_function(self, time, sampling_rate, state, state_history, observed_variables, air_brakes, sensors, env):
        canDeployAirbrake = False

        # deployment_time = air_brakes.airbrake_deploy_time

        # state = [x, y, z, vx, vy, vz, e0, e1, e2, e3, wx, wy, wz]
        altitude_ASL = state[2]
        above_ground_altitude = altitude_ASL - env.elevation
        vx, vy, vz = state[3], state[4], state[5]
        e0, e1, e2, e3 = state[6], state[7], state[8], state[9]

        # print(f"E0: {e0}, E1: {e1}, E2: {e2}, E3: {e3}")


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
        pitch = self.getPitch(np.array([e0, e1, e2, e3]))  # ~15° rotation around Y

        # print("Angle from flat plane (deg):", pitch)

        # ALTITUDES IS COLUMN, VELCOITIES IS ROWS


        # gets closest index to this angle
        angleIndex = self.binarySearch(self.angleVals, pitch, 0, self.numAngles - 1)
        velocityIndex = self.binarySearch(self.velocityVals, vz, 0, self.numVelPoints - 1)
        altitudeIndex = self.binarySearch(self.altitudeVals, above_ground_altitude, 0, self.numAltPoints - 1)

        altitudeIndex = len(self.altitudeVals) - altitudeIndex - 1
        angleIndex = len(self.angleVals) - angleIndex - 1

        # print(f"The goddamn altitude: {above_ground_altitude}")
        # print(f"The altitude index is: {altitudeIndex}, while the number of altitudes is {len(self.altitudeVals)}")
        # print(f"The velocity index is: {velocityIndex}, while the number of altitudes is {len(self.velocityVals)}")
        # print(altitudeVals)

        # print(f"row value we're getting is {angleIndex * numVelPoints + velocityIndex}, and column value is {altitudeIndex}")

        # should be good
        deploymentLevel = self.table.iloc[angleIndex * self.numVelPoints + velocityIndex][altitudeIndex] / 127.0


        # print(f"Our aaltitude was {above_ground_altitude}, our velocity Y was {vz}, our angle was {pitch}")



        # Check if the rocket has reached burnout
        if (vz > 0 and time > self.burnoutTime):
            air_brakes.deployment_level = deploymentLevel
            canDeployAirbrake = True
            # print(f"WE CAN DEPLOY! Deployment level is {air_brakes.deployment_level}. Also, time is {time}, row value we're getting is {angleIndex * self.numVelPoints + velocityIndex}, and column value is {altitudeIndex}, as \
            #     angle value is {angleIndex} and velocity index is {velocityIndex}")
                
        return (
            "airbrake" + str(canDeployAirbrake),
            time,
            air_brakes.deployment_level,
            air_brakes.drag_coefficient(air_brakes.deployment_level, mach_number),
        )