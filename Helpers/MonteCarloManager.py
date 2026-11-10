import logging
from numpy.random import normal, choice

class MonteCarloManager():
    def __init__(self, Parameters, inUse):
        self.variables = {}
        self.num_sims = 200
        self.num_processes = 10
        if inUse:
            self.variables["rocket_mass"] = {
                "type": "normal",
                "deviation": 1
            }
            self.variables["rocket_inertia_11"] = {
                "type": "normal",
                "deviation": 0.005
            }
            self.variables["rocket_inertia_33"] = {
                "type": "normal",
                "deviation": 0.005
            }
            self.variables["motor_dry_mass"] = {
                "type": "normal",
                "deviation": 0
            }
            self.variables["motor_inertia_11"] = {
                "type": "normal",
                "deviation": 0
            }
            self.variables["motor_inertia_33"] = {
                "type": "normal",
                "deviation": 0
            }
            self.variables["impulse"] = {
                "type": "normal",
                "deviation": 100
            }
            self.variables["motor_position"] = {
                "type": "normal",
                "deviation": 0
            }
            self.variables["burn_time"] = {
                "type": "normal",
                "deviation": 1
            }
            self.variables["motor_density"] = {
                "type": "normal",
                "deviation": 0.001
            }
            self.variables["rocket_radius"] = {
                "type": "normal",
                "deviation": 0.001
            }
            self.variables["inclination"] = {
                "type": "normal",
                "deviation": 3
            }
            self.variables["heading"] = {
                "type": "normal",
                "deviation": 15
            }
            self.variables["temperature"] = {
                "type": "normal",
                "deviation": 5
            }
            self.variables["fin_position"] = {
                "type": "normal",
                "deviation": 0.01
            }
            self.variables["atmosphere_pressure"] = {
                "type": "normal",
                "deviation": 10
            }

            self.PopulateMeans(Parameters)

            self.setup_logging()

    def PopulateMeans(self, Parameters):
        for key in self.variables.keys():
            if key not in Parameters:
                raise KeyError(f"Did not find {key} in Parameters!")
            else:
                self.variables[key]["mean"] = Parameters[key]

    def SampleValue(self, key):
        if key not in self.variables:
            raise KeyError(f"DIT NOT FIND KEY {key}!")
        else:
            valuePair = self.variables[key]
            if valuePair["type"] == "normal":
                return normal(valuePair["mean"], valuePair["deviation"])
            else:
                raise ValueError(f"Key {key} has invalid type {valuePair["type"]}!")

    def SetSampledValues(self, Parameters):
        flight_setting = {}
        for key in self.variables.keys():
            sampledVal = self.SampleValue(key)
            Parameters[key] = sampledVal
            flight_setting[key] = sampledVal
        return flight_setting
    #sets up the ability to log inputs.
    def setup_logging(self):
        class MyHandler(logging.FileHandler):
            def emit(self, record):
                super().emit(record)  # Call the superclass's emit method
                self.flush()  # Flush after each log message

        # Use your custom handler
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        handler = MyHandler('../Output/app.log', 'a')
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)