from rocketpy import Environment, SolidMotor, Rocket, Flight
from numpy.random import normal, choice
from time import process_time
import numpy as np
from wind import windArray_u, windArray_v

import FlightParams

import logging

# Configure logging
def runFlightWithMonteCarlo(numOfSims, envParams, analysis_parameters, initial_cpu_time, termOnApogee, launchDate):
    logging.basicConfig(
        filename='app.log',  # Change this to your desired log file
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filemode='a',  # 'w' for overwrite, 'a' for append
    )
    flightData = ["", "", ""]
    env = Environment(latitude=envParams["latitude"], longitude=envParams["longitude"], elevation=envParams["elevation"], date=launchDate)
    i=0
    
    settings = flight_settings(analysis_parameters, numOfSims)

    for setting in settings:
        start_time = process_time()
        env.set_atmospheric_model(type=envParams["type"], pressure= setting["atmosphere_pressure"], temperature= setting["temperature"], file=envParams["file"]) # Wind: (wind direction: 0 = North to South wind/90 = East to West wind, wind speed: m/s)
        # env.set_atmospheric_model(type=envParams["type"], pressure= setting["atmosphere_pressure"], temperature= setting["temperature"], wind_u= windArray_u(0,5), wind_v= windArray_v(0,5)) # Wind: (wind direction: 0 = North to South wind/90 = East to West wind, wind speed: m/s)
        MotorOne = SolidMotor(
            thrust_source="ReferencedFiles/" + FlightParams.motor_thrust_file, #Thrustcurve.org Mike Haberer - Rock Sim, Also uploaded to Google
            burn_time = FlightParams.burn_time,#Straight from thrustcurve.org
            reshape_thrust_curve=(FlightParams.burn_time, setting["impulse"]),
            nozzle_radius= setting["nozzle_radius"], # Part List
            throat_radius= setting["throat_radius"], # Part List
            grain_number=FlightParams.numGrains, #Based on cross-section
            grain_separation= FlightParams.grainSeparation, # Good
            grain_density= setting["grain_density"], #Calculated mass of grain / volume of grain , for this i did - the core since it should be empty? not sure
            grain_outer_radius= FlightParams.grainOuterRadius, # Good
            grain_initial_inner_radius= setting["grain_initial_inner_radius"], # Good
            grain_initial_height= setting["grain_initial_height"] , # Good
            interpolation_method = "linear",
            coordinate_system_orientation="combustion_chamber_to_nozzle",
            nozzle_position = FlightParams.the_nozzle_position,#eyeballed
            grains_center_of_mass_position= FlightParams.grain_center_of_mass_position,
            dry_mass=setting["motor_dry_mass"], #kg thrustcurve
            dry_inertia=(FlightParams.motor_11_inertia, FlightParams.motor_11_inertia, FlightParams.motor_33_inertia), #based off drawing
            center_of_dry_mass_position= FlightParams.center_of_dry_mass_within_motor,
        )

        #Pretty Much done except grain density and maybe nozz)le position

        Sp25 = Rocket(
            mass = setting["rocket_mass"], #OpenRocket
            radius = FlightParams.spRadius, #OpenRocket
            inertia = (FlightParams.spCentralDiameter, FlightParams.spCentralDiameter, FlightParams.spCentralAxis), # Calculated via Open Rocket
            coordinate_system_orientation = "nose_to_tail",
            center_of_mass_without_motor = setting["rocket_CM"], # OpenRocket
            power_off_drag ="ReferencedFiles/" + str(FlightParams.power_off_file), #Uploaded to drive
            power_on_drag = "ReferencedFiles/" + str(FlightParams.power_on_file), #Uploaded to drive
        )

        # CHANGE ONCE YOU FIND A GOOD WAY TO DO SO
        # Sp25.power_off_drag *= setting["power_off_drag"]
        # Sp25.power_on_drag *= setting["power_on_drag"]

        nose_cone = Sp25.add_nose(
            length = FlightParams.nose_cone_length, kind = FlightParams.nose_cone_type, position = FlightParams.nose_position)
        fin_set = Sp25.add_trapezoidal_fins(n=FlightParams.numFins, root_chord= FlightParams.root_chord, tip_chord=FlightParams.tip_chord, span=FlightParams.finSpan,
            position = setting["fin_position"],cant_angle=FlightParams.fin_cant_angle, sweep_length=FlightParams.fin_sweep_length)
        boattail = Sp25.add_tail(top_radius = FlightParams.spRadius, bottom_radius = FlightParams.boattail_bottom_radius,length = FlightParams.bottail_length,position = FlightParams.boattailPos)

        if(setting["time_to_deploy_airbrake_after_burnout"] != -1):
            Sp25.add_air_brakes(
                drag_coefficient_curve= FlightParams.air_brake_drag_file,
                controller_function= FlightParams.airbrake_controller_function,
                sampling_rate= FlightParams.airbrake_sample_rate,
                reference_area = FlightParams.airbrake_area,
                clamp = FlightParams.airbrake_clamp,
                initial_observed_variables=[0, 0, 0],
                override_rocket_drag= FlightParams.override_rocketdrag_with_airbrakedrag,
                name = "Air brakes",
                airbrake_time = setting["time_to_deploy_airbrake_after_burnout"]
            )

        Sp25.add_motor(MotorOne, FlightParams.the_motor_position)
        
        rail_buttons = Sp25.set_rail_buttons(
            upper_button_position= FlightParams.upper_railbutton_position,
            lower_button_position= FlightParams.lower_railbutton_position,
            angular_position=FlightParams.railbutton_angular_position
        )

        Drogue = Sp25.add_parachute(
            "Drogue",
            cd_s = setting["cd_s_drogue"],
            trigger = FlightParams.drogueTrigger
        )
        Light = Sp25.add_parachute(
            "Light",
            cd_s = setting["cd_s_light"],
            trigger = FlightParams.lightTrigger
        )

        try:
            # MotorOne.draw()
            # MotorOne.all_info()

            # Sp25.draw()
            # Sp25.all_info()
            
            testFlight = Flight(
                rocket=Sp25, environment=env,rail_length = FlightParams.rail_length,inclination = setting["inclination"],
                heading=setting["heading"], terminate_on_apogee = termOnApogee
            )
            inputOutput = export_flight_data(setting, testFlight, process_time() - start_time, env)
            flightData[0] += "\n" + str(inputOutput[0])
            flightData[1] += "\n" + str(inputOutput[1])
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

        # Skip if certain values are negative, which happens due to the normal curve but isnt realistic
        if flight_setting["lag_rec"] < 0 or flight_setting["lag_se"] < 0:
            continue

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