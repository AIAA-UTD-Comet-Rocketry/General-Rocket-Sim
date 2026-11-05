class MonteCarloManager():
    def __init__(self, Parameters, inUse):
        self.varDict = {}
        if inUse:
            self.varDict["spMass"] = {
                "type": "normal",
                "deviation": 4
            }
            self.varDict["rocket_inertia_11"] = {
                "type": "normal",
                "deviation": 0.5
            }
            self.varDict["rocket_inertia_33"] = {
                "type": "normal",
                "deviation": 0/5
            }
            self.varDict["dry_motor_mass"] = {
                "type": "normal",
                "deviation": 0
            }
            self.varDict["motor_inertia_11"] = {
                "type": "normal",
                "deviation": 0
            }
            self.varDict["motor_inertia_33"] = {
                "type": "normal",
                "deviation": 0
            }
            self.varDict["impulse"] = {
                "type": "normal",
                "deviation": 100
            }
            self.varDict["motor_position"] = {
                "type": "normal",
                "deviation": 0
            }
            self.varDict["burn_time"] = {
                "type": "normal",
                "deviation": 1
            }
            self.varDict["motor_density"] = {
                "type": "normal",
                "deviation": 0.01
            }
            self.varDict["rocket_radius"] = {
                "type": "normal",
                "deviation": 0.01
            }
            self.varDict["inclination"] = {
                "type": "normal",
                "deviation": 5
            }
            self.varDict["heading"] = {
                "type": "normal",
                "deviation": 15
            }
            self.varDict["temperature"] = {
                "type": "normal",
                "deviation": 5
            }
            self.varDict["fin_position"] = {
                "type": "normal",
                "deviation": 0.2
            }
            self.varDict["atmosphere_pressure"] = {
                "type": "normal",
                "deviation": 10
            }