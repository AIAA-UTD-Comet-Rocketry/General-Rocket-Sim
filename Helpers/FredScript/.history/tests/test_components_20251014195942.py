import os
import sys

# The directory of *this file*
script_dir = os.path.dirname(__file__)

# The project root (one level up)
project_root = os.path.abspath(os.path.join(script_dir, ".."))

# Add the src folder to sys.path
sys.path.append(os.path.join(project_root, "src"))

from src.openrocket_parser.simulations.loader import load_simulations_from_xml

sims = load_simulations_from_xml('sample.ork')

if sims:
    # Get the first simulation
    my_sim = sims[0]

    print(f"Loaded simulation: {my_sim.name}")
    print(f"Time to Apogee: {my_sim.summary.get('timetoapogee')} seconds")

    # The flight data is a pandas DataFrame
    flight_df = my_sim.flight_data

    # Print the max altitude from the time-series data
    max_altitude_from_data = flight_df['altitude'].max()
    print(f"Max altitude from data: {max_altitude_from_data:.2f} meters")