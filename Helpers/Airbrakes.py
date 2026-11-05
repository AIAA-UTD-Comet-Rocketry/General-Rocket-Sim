import numpy as np
from abc import ABC, abstractmethod

class Airbrake(ABC):
    def __init__(self, burnoutTime):
        self.burnoutTime = burnoutTime

    def getPitch(self, q):
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
    
    @abstractmethod
    def airbrake_controller_function(self, time, sampling_rate, state, state_history, observed_variables, air_brakes, sensors, env):
        pass