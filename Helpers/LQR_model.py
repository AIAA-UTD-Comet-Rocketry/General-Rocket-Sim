# official concurrently update LQR model

import matplotlib.pyplot as plt
import control as ct
import numpy as np

# following function is to use for generating plots and saving it in a file using maltlab library
# x_axis_vector = time vector
# y_axis_vector = response vector
# title = plot is str var with title of plot diag
# str_x_axis = x-axis label
# str_y_axis = y-a xis label
#  str_file_name = file name
def plotting_func(x_axis_vector,
                     y_axis_vector,
                     str_title,
                     str_x_axis,
                     str_y_axis,
                     str_file_name):

    plt.figure(figsize=(8,6))
    plt.plot(x_axis_vector, y_axis_vector, color='blue', linewidth=4)
    plt.title(str_title, fontsize=14)
    plt.xlabel(str_x_axis, fontsize=14)
    plt.ylabel(str_y_axis, fontsize=14)
    plt.tick_params(axis='both', which='major', labelsize=14)
    plt.grid(visible=True)
    plt.savefig(str_file_name, dpi=600) # pretty niche it can have adjustable resolution
    plt.show()

# state space vars x1 and x2 where x2 = dx/dt
# [dotted x1, dotted x2] = [{0, 1} {-k_a/m, -k_d/m}] [x1 x2] + [0 1/m]F
# which is dotted x = Ax + Bu equation that represents our state space model
# the output equation would be y = [1,0][x1 x2] + 0*F => y = Cx + Du
# to do the open space model

# setting the parameters
m = 10
ks = 100
kd = 5

# our system matrices
A = np.array([[0, 1], [-ks/m, -kd/m]])
B = np.array([[0], [1/m]])
C = np.array([[1, 0]])
D = np. array([[0]])

# defining state-space model
sys_state_space = ct.ss(A, B, C, D) # ct is our control sys library

# defining ini. condition
x0=np.array([[0],[0]])

# printing the system
print(sys_state_space)

# we need to apply our constant force at one newton
# to our system to see how it responds

# these parameters are to be changed!! this is currently
# a trial for me to understand what's going on. Later we implement
# more specific parameters to our flight

# these are our time vectors
start_time = 0
end_time = 20
number_samples = 500
time_vector = np.linspace(start_time, end_time, number_samples)

# then we are defining the control input vectors
control_input_vector = np.ones(number_samples)

# then we simulate the system: state space, time vect, control input, ini. state
return_sim = ct.forced_response(sys_state_space,
                                time_vector,
                                control_input_vector,
                                x0) # this reduces the structure as to why at first we don't get an output
# this produces the structure that we need to later decompose in the following lines

# output forced response:
# time response data obj which consists
# of time values of returned objs
print(return_sim.time)
# computed out puts:
print(return_sim.outputs)
#the state sequence of our system
print(return_sim.states)
# the inputs being used
print(return_sim.inputs) # to be expected from : np.ones(number_samples)

# now we plot our output: for our position over time
plotting_func(return_sim.time,
              return_sim.states[0, :],
              str_title='Position vs Time Graph',
              str_x_axis='Time [s]',
              str_y_axis='Position [m]',
              str_file_name='../OpenLoopResponse1.png')
# here we can see how an output of a simulation with a constant force of one (F),
# it will ocilate until done, but we need ours much much faster

# our velocity over time
plotting_func(return_sim.time,
              return_sim.states[1, :],
              str_title='Velocity vs Time Graph',
              str_x_axis='Time [s]',
              str_y_axis='Velocity [m/s]',
              str_file_name='../OpenLoopResponse2.png')

# alreadyhaving computed the system

####### here we determine/implement our steady state control input
# in our simulation


# now we need to define our ud (desired steady state)
# in this case we want our system to go to two

# xd is a constant, so we sub x by xd and u by ud:
# 0 = Axd + Bud
# where xd = 0 as its in a constant steady state. assuming we have desired control input ud
# to produce the desired steady state we do:
# ud = -(B^T B)^(-1) B^T Axd -> which we compute:

# desired state:
xd = np.array([[2],[0]])

matrix1 = np.matmul(np.linalg.inv(np.matmul(B.T, B)), B.T)
matrix2 = np.matmul(matrix1, A)

ud = np.matmul(matrix2, xd)
time_vector = np.linspace(start_time, end_time, number_samples)

control_input_vector = ud[0, 0]*np.ones(number_samples)

# printing output:
print("Control Input Vector: ", control_input_vector)

# simulating the system
return_sim = ct.forced_response(sys_state_space,
                                time_vector,
                                control_input_vector,
                                x0)
# plotting the output:
plotting_func(return_sim.time,
              return_sim.states[0, :],
              str_title='Position vs Time Graph',
              str_x_axis='Time [s]',
              str_y_axis='Position [m]',
              str_file_name='../OpenLoopResponse1.png')
plotting_func(return_sim.time,
              return_sim.states[1, :],
              str_title='Velocity vs Time Graph',
              str_x_axis='Time [s]',
              str_y_axis='Velocity [m/s]',
              str_file_name='../OpenLoopResponse2.png')

####Finally we get into our LQR control:
# assuming our desired state is zero for our LQR implementation
# Q =  positive-semi definite symmetric matrix = q*I = cost weighting matrix
# R =  defined as a positive-definite symmetric matrix = r*I = input weighing matrix
# J = ∫₀∞ [ xᵀ Q x + uᵀ R u ] dt,  Q = Qᵀ ≥ 0,  R = Rᵀ > 0
Q = 10*np.array([[10, 0],[0, 10]]) # is our chosen state penalty (penalizes state errors)
R = 1*np.array([[1]]) # and this is our actuation penalty
# that penalizes our input controls

###
# in short a brief comment for my own understanding is that  LQR,
# L (linear) is that we assume the system can be
# represented in a linear state space : x = Ax + Bu
# Q(quadratic): evaluates our performance using a quadratic cost function J:
# J = ∫₀∞ [ xᵀ Q x + uᵀ R u ] dt
# R(regulator) continuously pushes our system errors back to 0 or a point of reference x reference
## Q will penalize any deviations from our target trajectory (makes system respond faster)
    # while R prevents excessive energy consumption or mechanical wear
    # thus LQR basically achieves our performance goals with
    # the least amount of actuator effort
    # Riccati formula: we want tp minimize tot total future cost J,
# which we apply riccati using a matrix S for remaining cost xᵀ S x:
    # K can be directly calculated as K = R⁻¹ Bᵀ S where S is solution to:
        # Aᵀ S + S A - S B R⁻¹ Bᵀ S + Q = 0
            # the algebraic riccati equation
###

# u = -Kx -> u = -K (x current - x reference)  ->optimal controller
# -K is our feedback control matrix (gain matrix)
K, S, E = ct.lqr(sys_state_space, Q, R)
# S being solution to riccati as stated bellow,
# E is our closed loop eigen values
print(K, S, E)
## decomposing our aerodynamics in absolute coordinates
# using dotted curly *~x = (A-BK) ~x )which A-BK will be asymptomatically stable
# eigen values being to the left half of complex plane
# so our setting point curly x (~x) will approach zero for steady state system
    # so x becomes xd : dotted x = (A-BK)x-(A-BK)xd <--closed loop system simulation
    #                               Acl     Bcl
Acl = A - np.matmul(B,K) # Acl = A - BK
Bcl = -Acl # Bcl = -(A - BK)
Dcl =  Dcl = np.array([[0,0]]) # our x = Ax + Bu -> y = Cx + Du
# defining our new state space
sys_state_space_cl = ct.ss(Acl, Bcl, C, Dcl) # which has our state equation

# defining time vectors for our simulation
time_vector = np.linspace(start_time, end_time, number_samples)
#now we are defining our input vectors for closed loop sim
input_cl = np.zeros(shape=(2, number_samples))
input_cl[0, :] = xd[0, 0]*np.ones(number_samples)
input_cl[1, :] = xd[1, 0]*np.ones(number_samples)

return_simcl = ct.forced_response(sys_state_space_cl,
                                  time_vector,
                                  input_cl,
                                  x0)
plotting_func(return_simcl.time,
              return_simcl.states[0, :],
              str_title= 'Position vs Time Graph',
              str_x_axis='Time [s]',
              str_y_axis='Position [m]',
              str_file_name='../OpenLoopResponse1.png') #1st state
plotting_func(return_simcl.time,
              return_simcl.states[1, :],
              str_title='Velocity vs Time Graph',
              str_x_axis='Time [s]',
              str_y_axis='Velocity [m/s]',
              str_file_name='../OpenLoopResponse2.png') #second state