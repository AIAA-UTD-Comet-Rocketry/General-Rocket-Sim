from rocketpy import Environment, SolidMotor, Rocket, Flight
from numpy.random import normal, choice
from time import process_time
import pandas as pd
from Helpers.FlightParams import Parameters
import logging

# Configure logging
def RunFlightWithMonteCarlo(numOfSims, initial_cpu_time):
    logging.basicConfig(
        filename='app.log',  # Change this to your desired log file
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filemode='a',  # 'w' for overwrite, 'a' for append
    )
    flightData = ["", "", ""]

    
    env = Environment(latitude=Parameters["latitude"], longitude=Parameters["longitude"], elevation=Parameters["elevation"], date=[*Parameters["day"], int(Parameters["hour"])])
    env.set_atmospheric_model(type=Parameters["atmosphere_type"], file=Parameters["env_file"], wind_u=Parameters["wind_u"], wind_v=Parameters["wind_v"], pressure=Parameters["pressure"])
    i=0

    if not Parameters["doing_monte_carlo"]:
        numOfSims = 1

    for i in range(numOfSims):
        settings = Parameters["monte_carlo"].SetSampledValues(Parameters)
        start_time = process_time()
        # env.set_atmospheric_model(type=envParams["atmosphere_type"], temperature =envParams["temperature"])
        MotorOne = SolidMotor(
            thrust_source="../InputFiles/" + Parameters["motor_thrust_file"], #Thrustcurve.org Mike Haberer - Rock Sim, Also uploaded to Google
            burn_time = Parameters["burn_time"],#Straight from thrustcurve.org
            reshape_thrust_curve=(Parameters["burn_time"], Parameters["impulse"]),
            nozzle_radius= Parameters["nozzle_radius"], # Part List
            throat_radius= Parameters["throat_radius"], # Part List
            grain_number=Parameters["num_grains"], #Based on cross-section
            grain_separation= Parameters["grain_separation"], # Good
            grain_density= Parameters["motor_density"], #Calculated mass of grain / volume of grain , for this i did - the core since it should be empty? not sure
            grain_outer_radius= Parameters["grain_outer_radius"], # Good
            grain_initial_inner_radius= Parameters["grain_inner_radius"], # Good
            grain_initial_height= Parameters["grain_height"] , # Good
            interpolation_method = "linear",
            coordinate_system_orientation="combustion_chamber_to_nozzle",
            nozzle_position = Parameters["nozzle_position"],#eyeballed
            grains_center_of_mass_position= Parameters["grain_center_of_mass_position"],
            dry_mass=Parameters["motor_dry_mass"], #kg thrustcurve
            dry_inertia=(Parameters["motor_inertia_11"], Parameters["motor_inertia_11"], Parameters["motor_inertia_33"]), #based off drawing
            center_of_dry_mass_position= Parameters["center_of_dry_mass_within_motor"],
        )
        #Pretty Much done except grain density and maybe nozz)le position

        Sp25 = Rocket(
            mass = Parameters["rocket_mass"], #OpenRocket
            radius = Parameters["rocket_radius"], #OpenRocket
            inertia = (Parameters["rocket_inertia_11"], Parameters["rocket_inertia_11"], Parameters["rocket_inertia_33"]), # Calculated via Open Rocket
            coordinate_system_orientation = "nose_to_tail",
            center_of_mass_without_motor = Parameters["center_of_mass_without_motor"], # OpenRocket
            power_off_drag ="../InputFiles/" + str(Parameters["power_off_file"]), #Uploaded to drive
            power_on_drag = "../InputFiles/" + str(Parameters["power_on_file"]), #Uploaded to drive
        )


        nose_cone = Sp25.add_nose(
            length = Parameters["nose_cone_length"], kind = Parameters["nose_cone_type"], position = Parameters["nose_position"])
        fin_set = Sp25.add_trapezoidal_fins(n=Parameters["num_fins"], root_chord= Parameters["root_chord"], tip_chord=Parameters["tip_chord"], span=Parameters["fin_span"],
            position = Parameters["fin_position"],cant_angle=Parameters["fin_cant_angle"], sweep_length=Parameters["fin_sweep_length"])
        
        if(Parameters["has_bottail"]):
            boattail = Sp25.add_tail(top_radius = Parameters["rocket_radius"], bottom_radius = Parameters["boattail_bottom_radius"],length = Parameters["boattail_length"],position = Parameters["boattailPos"])

        if(Parameters["using_airbrakes"]):
            Sp25.add_air_brakes(
                drag_coefficient_curve= Parameters["air_brake_drag"],
                # drag_coefficient_curve= 1,
                controller_function= Parameters["airbrake_policy"].airbrake_controller_function,
                sampling_rate= Parameters["airbrake_sample_rate"],
                reference_area = Parameters["airbrake_area"],
                clamp = Parameters["airbrake_clamp"],
                initial_observed_variables=[0, 0, 0],
                override_rocket_drag= Parameters["override_rocket_drag"],
                name = "Air brakes",
            )

        Sp25.add_motor(MotorOne, Parameters["motor_position"])
        
        rail_buttons = Sp25.set_rail_buttons(
            upper_button_position= Parameters["upper_railbutton_position"],
            lower_button_position= Parameters["lower_railbutton_position"],
            angular_position=Parameters["railbutton_angular_position"]
        )

        for parachute in Parameters["parachutes"].values():
            Sp25.add_parachute(
                parachute["name"],
                cd_s = parachute["cd"],
                lag = parachute["lag"],
                trigger = parachute["trigger"]
            )

        '''
        neededTimes = pd.read_csv("..InputFiles/requiredSampleTimes.csv", header = 0)
        sampledMasses = [Sp25.total_mass(t) for t in neededTimes["Flight_Time_(s)"].to_numpy()]
        neededTimes["mass"] = sampledMasses
        neededTimes = neededTimes.rename(columns={"Flight_Time_(s)": "time"})
        neededTimes.to_csv("..InputFiles/massMapping.csv", index = None)
        print("csv stuff finished!")
        '''


        try:
            # MotorOne.draw()
            # MotorOne.all_info()

            Sp25.draw()
            # Sp25.all_info()

            print("Center of mass without motor is currently set to: " + str(Parameters["center_of_mass_without_motor"]))

            testFlight = Flight(
                rocket=Sp25, environment=env,rail_length = Parameters["rail_length"], inclination = Parameters["inclination"],
                heading=Parameters["heading"], terminate_on_apogee = Parameters["terminate_at_apogee"]
            )
            print('printing ts crack')
            testFlight.plots.trajectory_3d()
            testFlight.info()
            print("flgith complete1")
            inputOutput = export_flight_data(settings, testFlight, process_time() - start_time, env, Parameters["terminate_at_apogee"])
            flightData[0] += "\n" + str(inputOutput[0])
            flightData[1] += "\n" + str(inputOutput[1])

            print("\n\n\nMass function:")
            print(Sp25.total_mass)
            print("\n\n\n")

        except Exception as E:
            flightData[2] += str(E) + "\n" + str(export_flight_error(settings))
        # Register time
        i+=1
        if(i % 10 == 0):
            logging.getLogger().info(f"Curent iteration: {i:06d} | Average Time per Iteration: {(process_time() - initial_cpu_time)/i:2.6f} s")
    return flightData

def export_flight_data(flight_setting, flight_data, exec_time, env, termOnApogee):
    # Generate flight results
    flight_result = {
        "out_of_rail_time": flight_data.out_of_rail_time,
        "out_of_rail_velocity": flight_data.out_of_rail_velocity,
        "max_velocity": flight_data.speed.max,
        "apogee_time": flight_data.apogee_time,
        "apogee_altitude": flight_data.apogee - env.elevation,
        "apogee_x": flight_data.apogee_x,
        "apogee_y": flight_data.apogee_y,
        "initial_static_margin": flight_data.rocket.static_margin(0),
        "out_of_rail_static_margin": flight_data.rocket.static_margin(
            flight_data.out_of_rail_time
        ),
        "out_of_rail_stability_margin": flight_data.out_of_rail_stability_margin,
        "execution_time": exec_time,
    }

    if not termOnApogee:
        flight_result["impact_x"] = flight_data.x_impact
        flight_result["impact_y"] = flight_data.y_impact

    # Take care of parachute results
    return [flight_setting, flight_result]

def export_flight_error(flight_setting):
    print()
    return flight_setting