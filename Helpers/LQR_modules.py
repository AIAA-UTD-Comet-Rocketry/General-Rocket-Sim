import numpy as np


class vertical_rocket_dynamics:
    # my current K, S, E = ct.lqr(sys_state_space, Q, R) is perfect for mass spring dampener
    # but rocket dynamics are nonlinear system, relevant equation:
    # dh_dt = v
    # dv_dt = -g - (0.5 * rho(h) * C_D(h, v, u) * A * v_rel * abs(v_rel)) / m(t)
    # so puttin it in separate modules accounting for verticle components

    def __init__(
        self,
        mass_function,
        density_function,
        cd_area_function,
        wind_function=None,
        gravity=9.80665
    ):

        self.mass_function = mass_function
        self.density_function = density_function
        self.cd_area_function = cd_area_function

        self.wind_function = wind_function or (lambda h: 0.0)

        self.g = gravity

    def dynamics(self, t, x, u):

        h, v = x

        # Atmospheric density
        rho = self.density_function(h)

        # Rocket mass at current flight time
        mass = self.mass_function(t)

        # Vertical wind
        wind_z = self.wind_function(h)

        # Velocity relative to atmosphere
        v_rel = v - wind_z

        # Effective drag coefficient multiplied by reference area.
        # Units: m^2
        cd_area = self.cd_area_function(h, v_rel, u)

        # Signed aerodynamic drag
        drag = (
            0.5
            * rho
            * cd_area
            * v_rel
            * abs(v_rel)
        )

        # Vertical equations of motion
        dh = v

        dv = -self.g - drag / mass

        return np.array([dh, dv])

class Linearization:
# we have: dx_dt = f(x, u)
# Jacobians (partial derivatives), but want
# A = df_dx  # partial derivative of f with respect to x
# B = df_du  # partial derivative of f with respect to u

    @staticmethod
    def calculate_A(dymics, t, x, u, epsilon=1e-5): 