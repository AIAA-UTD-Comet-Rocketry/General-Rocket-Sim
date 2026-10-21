import ansys.fluent.core as pyfluent

# Connect to Fluent (can be local or remote)
#session = pyfluent.launch_fluent(dimension=3,mode="solver", precision="double", processor_count=30, case_file_name="C:\\Users\\AIAA UT Dallas\\Desktop\\CFDTESTING-selected\\LeadingEdgeStudy\\LeadingEdgeStudy_files\\dp0\\FFF\\Fluent\\FFF.1-33.cas
# Load initial case
#session.read_case(r"C:\Users\AIAA UT Dallas\Desktop\CFDTESTING-selected\LeadingEdgeStudy\LeadingEdgeStudy_files\dp0\FFF\Fluent\FFF.1-32.cas")

#Given Information
Air_density = 101325 #Pa
Fluid_viscosity = 1.81e-5 #Pa-s
SimCount = 0
#Dependent on rocket
Diameter = 0.156 #m
Length = 3 #m

def Reynolds_number(velocity):
    return (Air_density * velocity * Length) / Fluid_viscosity
def Boundary_layer_thickness(Reyolds):
    return (Length*0.382)/((Reyolds)**0.2)
def inflation(boundary_layer_thickness):
    return boundary_layer_thickness/10
    
# Define list of velocities in m/s
velocities = [51.45, 102.9, 154.35, 205.8, 257.25]
Element = 0.02

#Reynolds_number = []
#Thickness = []
#Reynolds and Boundary Layer Calculation
#for i in range(len(velocities)):
#    Reynolds_number.append((Air_density * velocities[i] * Length) / Fluid_viscosity)
#    print(f"Velocity: {velocities[i]} m/s, Reynolds Number: {Reynolds_number[i]}")
#    Thickness.append((Length*0.382)/((Reynolds_number[i])**0.2))
##    print(f"Velocity: {velocities[i]} m/s, Boundary Layer Thickness: {Thickness[i]:.6f} m")

#Meshing



inlet_name = "inlet"
wall_zone = "rocket"

drag_results = {}
'''session.tui.define.models.solver.density_based_implicit
session.tui.define.models.solver
session.tui.define.models.viscous.kw_sst'''


# Set reference values function
'''def set_reference_values(vel):
    session.tui.report.reference_values.area = 0.01108
    session.tui.report.reference_values.density = 1.225
    session.tui.report.reference_values.length = 3
    session.tui.report.reference_values.pressure = 102539.85
    session.tui.report.reference_values.temperature = 302.594
    session.tui.report.reference_values.viscosity = 1.81e-05
    session.tui.report.reference_values.velocity = vel'''
try:
    # Main loop

    for vel in velocities:
        
        R = Reynolds_number(vel)
        BLT = Boundary_layer_thickness(R)
        Inflation = inflation(BLT)
        #geometry file from design modeler "C:\Users\AIAA UT Dallas\Desktop\CFDTESTING-selected\LeadingEdgeStudy\RocketFluid.stp"
        #geometry_file = "C:\\Users\\AIAA UT Dallas\\Desktop\\CFDTESTING-selected\\LeadingEdgeStudy\\RocketFluid.stp"
        Rmeshing = pyfluent.launch_fluent(
        mode=pyfluent.FluentMode.MESHING,
        product_version=pyfluent.FluentVersion.v252,
        processor_count=20
        )
        myflow = Rmeshing.workflow
        myflow.InitializeWorkflow(WorkflowType="Watertight Geometry")
        tasks = myflow.TaskObject
        import_geometry = tasks['Import Geometry']
        import_geometry.Arguments.set_state({
        'FileName': "C:\\Users\\Public\\Documents\\test\\testDM.agdb" , 'LengthUnit': "m"
        })
        import_geometry.Execute()
        
        add_local_sizing = myflow.TaskObject["Add Local Sizing"]
        add_local_sizing.Arguments = dict(
            {
                "AddChild": "yes",
                "BOIControlName": "Rocket",
                "BOIFaceLabelList": ["Solid"],
                "BOIGrowthRate": 1.2,
                "BOISize": 0.00020898,
            }
        )
        add_local_sizing.Execute()

        #inflation
        add_boundary_layers = myflow.TaskObject["Add Boundary Layers"]
        add_boundary_layers.AddChildToTask()
        add_boundary_layers.InsertCompoundChildTask()
        myflow.TaskObject["smooth-transition_1"].Arguments.update_dict(
            {
                "BLControlName": "FirstLayer",
                "NumberOfLayers": 11,
                "Rate": 1.2,
                "TransitionRatio": 0.5,
            }
        )
        add_boundary_layers.Execute()



        Rmeshing.tui.file.import_.cad("yes","C:\\Users\\Public\\Documents\\test\\testDM.agdb")
        #debugging to make sure named selections are correct
        Rmeshing.tui.mesh.surface_mesh()
        

        #Face sizing
        Rmeshing.tui.mesh.size_functions.create_size_function(
        "face-size",      # type
        "rocket",         # named selection zone
            .01             # element size
        )


        print(f"Running simulation for velocity: {vel} m/s")
        session = pyfluent.launch_fluent(dimension=3,mode="solver", precision="double", processor_count=20, case_file_name="C:\\Users\\AIAA UT Dallas\\Desktop\\CFDTESTING-selected\\LeadingEdgeStudy\\LeadingEdgeStudy_files\\dp0\\FFF\\Fluent\\FFF-52.cas")
        session.tui.file.read_mesh(new_mesh_file)
        session.tui.define.models.solver.density_based_implicit
        session.tui.define.models.solver
        session.tui.define.models.viscous.kw_sst        

        # Set boundary condition
        session.tui.define.boundary_conditions.velocity_inlet(
            inlet_name, "no", "yes", "yes", "no", 0, "yes", "no", str(vel), "no", 0, "no", 0, "no", "no", "yes", "no", 1, 0.05, 10, "no", 0
        )

        session.tui.report.reference_values.area(str(0.005566574))
        session.tui.report.reference_values.density(str(1.1959))
        session.tui.report.reference_values.length(str(3))
        session.tui.report.reference_values.pressure(str(102308))
        session.tui.report.reference_values.temperature(str(302.594))
        session.tui.report.reference_values.viscosity(str(1.81e-05))
        session.tui.report.reference_values.velocity(str(vel))  
        
        # Initialize and run
        session.tui.solve.initialize.set_defaults("x-velocity", str(vel))
        session.tui.solve.initialize.initialize_flow()
        session.tui.solve.set.transient_controls.time_step_size(".01")
        session.tui.solve.set.transient_controls.max_iterations_per_time_step("50")
        session.tui.solve.set.transient_controls.number_of_time_steps("10")

        session.tui.solve.dual_time_iterate()

        # Get drag report
        

        #Save results
        session.tui.file.write_data(
            fr"C:\Users\Public\Documents\test\squared_{vel}.dat"
        )
        session.tui.file.write_case(
            fr"C:\Users\Public\Documents\test\squared_{vel}.cas"
        )
        drag = session.tui.report.forces.wall_forces(
            "no", wall_zone, ",", "1", "0", "0", "yes", "drag_report", "yes"
        )

        session.exit()
except:
    session.exit()

