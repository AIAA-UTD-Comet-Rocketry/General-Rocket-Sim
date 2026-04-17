from rocketpy import Environment, SolidMotor, Rocket, Flight

from numpy.random import normal, choice
from time import process_time
import numpy as np
import pandas as pd
from wind import windArray_u, windArray_v

import FlightParams

import logging

# Configure logging
def runFlightWithMonteCarlo(numOfSims, envParams, analysis_parameters, initial_cpu_time, termOnApogee, launchDate, obtainingMotorValue):
    logging.basicConfig(
        filename='app.log',  # Change this to your desired log file
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filemode='a',  # 'w' for overwrite, 'a' for append
    )
    flightData = ["", "", ""]
    env = Environment(latitude=FlightParams.Parameters["envParams"]["latitude"], longitude=FlightParams.Parameters["envParams"]["longitude"], elevation=FlightParams.Parameters["envParams"]["elevation"], date=launchDate)
    # env.set_atmospheric_model(type=envParams["type"], file=envParams["file"], wind_u=FlightParams.Parameters["envParams"]["wind_u"], wind_v=FlightParams.Parameters["envParams"]["wind_v"])
    i=0
    
    settings = flight_settings(analysis_parameters, numOfSims)

    for setting in settings:
        start_time = process_time()
        env.set_atmospheric_model(type=envParams["type"], file=envParams["file"], wind_u=setting["wind-u"], wind_v=setting["wind-v"])
        # env.set_atmospheric_model(type=envParams["type"], pressure= setting["atmosphere_pressure"], temperature= setting["temperature"], wind_u= windArray_u(0,5), wind_v= windArray_v(0,5)) # Wind: (wind direction: 0 = North to South wind/90 = East to West wind, wind speed: m/s)
        MotorOne = SolidMotor(
            thrust_source="ReferencedFiles/" + FlightParams.Parameters["motor_thrust_file"], #Thrustcurve.org Mike Haberer - Rock Sim, Also uploaded to Google
            burn_time = FlightParams.Parameters["burn_time"],#Straight from thrustcurve.org
            reshape_thrust_curve=(FlightParams.Parameters["burn_time"], setting["impulse"]),
            nozzle_radius= setting["nozzle_radius"], # Part List
            throat_radius= setting["throat_radius"], # Part List
            grain_number=FlightParams.Parameters["numGrains"], #Based on cross-section
            grain_separation= FlightParams.Parameters["grainSeparation"], # Good
            grain_density= setting["grain_density"], #Calculated mass of grain / volume of grain , for this i did - the core since it should be empty? not sure
            grain_outer_radius= FlightParams.Parameters["grainOuterRadius"], # Good
            grain_initial_inner_radius= setting["grain_initial_inner_radius"], # Good
            grain_initial_height= setting["grain_initial_height"] , # Good
            interpolation_method = "linear",
            coordinate_system_orientation="combustion_chamber_to_nozzle",
            nozzle_position = FlightParams.Parameters["the_nozzle_position"],#eyeballed
            grains_center_of_mass_position= FlightParams.Parameters["grain_center_of_mass_position"],
            dry_mass=setting["motor_dry_mass"], #kg thrustcurve
            dry_inertia=(FlightParams.Parameters["motor_11_inertia"], FlightParams.Parameters["motor_11_inertia"], FlightParams.Parameters["motor_33_inertia"]), #based off drawing
            center_of_dry_mass_position= FlightParams.Parameters["center_of_dry_mass_within_motor"],
        )

        #Pretty Much done except grain density and maybe nozz)le position

        Sp25 = Rocket(
            mass = setting["rocket_mass"], #OpenRocket
            radius = FlightParams.Parameters["rocket_radius"], #OpenRocket
            inertia = (FlightParams.Parameters["spCentralDiameter"], FlightParams.Parameters["spCentralDiameter"], FlightParams.Parameters["spCentralAxis"]), # Calculated via Open Rocket
            coordinate_system_orientation = "nose_to_tail",
            center_of_mass_without_motor = FlightParams.Parameters["the_center_of_mass_without_motor"], # OpenRocket
            power_off_drag ="ReferencedFiles/" + str(FlightParams.Parameters["power_off_file"]), #Uploaded to drive
            power_on_drag = "ReferencedFiles/" + str(FlightParams.Parameters["power_on_file"]), #Uploaded to drive
        )

        print("Center of mass without motor is currently set to: " + str(FlightParams.Parameters["the_center_of_mass_without_motor"]))

        # CHANGE ONCE YOU FIND A GOOD WAY TO DO SO
        # Sp25.power_off_drag *= setting["power_off_drag"]
        # Sp25.power_on_drag *= setting["power_on_drag"]

        nose_cone = Sp25.add_nose(
            length = FlightParams.Parameters["nose_cone_length"], kind = FlightParams.Parameters["nose_cone_type"], position = FlightParams.Parameters["nose_position"])
        fin_set = Sp25.add_trapezoidal_fins(n=FlightParams.Parameters["num_fins"], root_chord= FlightParams.Parameters["root_chord"], tip_chord=FlightParams.Parameters["tip_chord"], span=FlightParams.Parameters["fin_span"],
            position = FlightParams.Parameters["fin_position"],cant_angle=FlightParams.Parameters["fin_cant_angle"], sweep_length=FlightParams.Parameters["fin_sweep_length"])
        
        if(FlightParams.Parameters["hasBottail"]):
            boattail = Sp25.add_tail(top_radius = FlightParams.Parameters["rocket_radius"], bottom_radius = FlightParams.Parameters["boattail_bottom_radius"],length = FlightParams.Parameters["boattail_length"],position = FlightParams.Parameters["boattailPos"])

        if(FlightParams.Parameters["using-airbrakes"]):
            Sp25.add_air_brakes(
                drag_coefficient_curve= FlightParams.Parameters["air_brake_drag"],
                # drag_coefficient_curve= 1,
                controller_function= FlightParams.Parameters["airbrake_controller_function"],
                sampling_rate= FlightParams.Parameters["airbrake_sample_rate"],
                reference_area = FlightParams.Parameters["airbrake_area"],
                clamp = FlightParams.Parameters["airbrake_clamp"],
                initial_observed_variables=[0, 0, 0],
                override_rocket_drag= FlightParams.Parameters["override_rocketdrag_with_airbrakedrag"],
                name = "Air brakes",
                airbrake_time = setting["time_to_deploy_airbrake_after_burnout"],
            )

        Sp25.add_motor(MotorOne, FlightParams.Parameters["the_motor_position"])
        
        rail_buttons = Sp25.set_rail_buttons(
            upper_button_position= FlightParams.Parameters["upper_railbutton_position"],
            lower_button_position= FlightParams.Parameters["lower_railbutton_position"],
            angular_position=FlightParams.Parameters["railbutton_angular_position"]
        )

        for parachute in FlightParams.Parameters["parachutes"].values():
            Sp25.add_parachute(
                parachute["name"],
                cd_s = parachute["cd"],
                lag = parachute["lag"],
                trigger = parachute["trigger"]
            )

        neededTimes = pd.read_csv("ReferencedFiles/requiredSampleTimes.csv", header = 0)
        sampledMasses = [Sp25.total_mass(t) for t in neededTimes["Flight_Time_(s)"].to_numpy()]
        neededTimes["mass"] = sampledMasses
        neededTimes = neededTimes.rename(columns={"Flight_Time_(s)": "time"})
        neededTimes.to_csv("ReferencedFiles/massMapping.csv", index = None)
        print("csv stuff finished!")


        try:
            # MotorOne.draw()
            # MotorOne.all_info()

            # Sp25.draw()
            # Sp25.all_info()

            print("Center of mass without motor is currently set to: " + str(FlightParams.Parameters["the_center_of_mass_without_motor"]))

            testFlight = Flight(
                rocket=Sp25, environment=env,rail_length = FlightParams.Parameters["rail_length"],inclination = setting["inclination"],
                heading=setting["heading"], terminate_on_apogee = termOnApogee
            )
            # testFlight.info()
            print("flgith complete1")
            inputOutput = export_flight_data(setting, testFlight, process_time() - start_time, env)
            flightData[0] += "\n" + str(inputOutput[0])
            flightData[1] += "\n" + str(inputOutput[1])

            print("\n\n\nMass function:")
            print(Sp25.total_mass)
            print("\n\n\n")

        except Exception as E:
            flightData[2] += str(E) + "\n" + str(export_flight_error(setting))
        # Register time
        i+=1
        if(i % 10 == 0):
            logging.getLogger().info(f"Curent iteration: {i:06d} | Average Time per Iteration: {(process_time() - initial_cpu_time)/i:2.6f} s")
    return flightData

def flight_settings(analysis_parameters, total_number):
    i = 0
    while i < total_number:
        # Generate a flight setting
        flight_setting = {}
        for parameter_key, parameter_value in analysis_parameters.items():
            if type(parameter_value) is tuple:
                flight_setting[parameter_key] = normal(*parameter_value)
            else:
                flight_setting[parameter_key] = choice(parameter_value)

        # # Skip if certain values are negative, which happens due to the normal curve but isnt realistic
        # if flight_setting["lag_rec"] < 0 or flight_setting["lag_se"] < 0:
        #     continue

        # Update counter
        i += 1
        # Yield a flight setting
        yield flight_setting

def export_flight_data(flight_setting, flight_data, exec_time, env):
    # Generate flight results
    flight_result = {
        "out_of_rail_time": flight_data.out_of_rail_time,
        "out_of_rail_velocity": flight_data.out_of_rail_velocity,
        "max_velocity": flight_data.speed.max,
        "apogee_time": flight_data.apogee_time,
        "apogee_altitude": flight_data.apogee - env.elevation,
        "apogee_x": flight_data.apogee_x,
        "apogee_y": flight_data.apogee_y,
        "impact_x": flight_data.x_impact,
        "impact_y": flight_data.y_impact,
        "initial_static_margin": flight_data.rocket.static_margin(0),
        "out_of_rail_static_margin": flight_data.rocket.static_margin(
            flight_data.out_of_rail_time
        ),
        "out_of_rail_stability_margin": flight_data.out_of_rail_stability_margin,
        "execution_time": exec_time,
    }

    # Take care of parachute results
    return [flight_setting, flight_result]

def export_flight_error(flight_setting):
    print()
    return flight_setting