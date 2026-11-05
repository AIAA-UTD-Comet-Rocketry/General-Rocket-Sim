from numpy.random import normal, choice

class MonteCarloManager():
    def __init__(self, Parameters, inUse):
        self.variables = {}
        if inUse:
            self.variables["spMass"] = {
                "type": "normal",
                "deviation": 4
            }
            self.variables["rocket_inertia_11"] = {
                "type": "normal",
                "deviation": 0.5
            }
            self.variables["rocket_inertia_33"] = {
                "type": "normal",
                "deviation": 0/5
            }
            self.variables["dry_motor_mass"] = {
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
                "deviation": 0.01
            }
            self.variables["rocket_radius"] = {
                "type": "normal",
                "deviation": 0.01
            }
            self.variables["inclination"] = {
                "type": "normal",
                "deviation": 5
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
                "deviation": 0.2
            }
            self.variables["atmosphere_pressure"] = {
                "type": "normal",
                "deviation": 10
            }

            self.PopulateMeans(Parameters)

    def PopulateMeans(self, Parameters):
        for key in self.variables.keys:
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
        for key in self.variables.keys:
            sampledVal = self.SampleValue(key)
            Parameters[key] = sampledVal