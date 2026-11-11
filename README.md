Welcome to our repository for interfacing with RocketPy for our own custom simulations! I'll first walk you through how to set it up, then talk aobut here all the important things are located.

<h1> Project Setup </h1>

First, you ahve to 'clone' this repository onto your local machine. To do that, first install git on your machine if you don't have it already, which you can do here: https://git-scm.com/install/windows.

Then, you can use git from your terminal to basically retrieve the code on Github. To do that, you can follow the following steps to git clone onto your computer: https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository.

Next, make sure you have python installed on your machine. I use Python 3.13.12, which I'd recommend installing as well. Any version about python 3.12 should work just fine though. You can install python here: https://www.python.org/downloads/. If you see a chechmakr like 'add to path', make sure to select that.

Next, you almost have the setup done! Next, you'll have to set up a python "virtual environment" - this is where basically any python libraires you install only apply to this reposiotory and not all projects you have on your computer. To do this, from a computer terminal, you want to first do "python -m venv .venv" while making sure you type this command in the same place where your project is. If you get an error saying it doesn't recognize python, check if you added the python folder to the PATH environment variable.

Next if the virtual environment is created successfully, you can do "source .venv/bin/activate" on linux/mac machines, or ".venv/Scripts/activate" on windows machines. This should activate the virtual environment and show it visually - if it doesn't, ur probalby still fine so long as it didn't error. Whenever you want to work in this project, you should make sure the virtual environment is activated whenever u run python files. Also, you should try to only install python libraries while the virtual environment's active.

Next, all you really need to do now is just install all the python libraries. To do this, you should just be able to type "pip install -r requirements.txt", which will read the 'requirements.txt' file and automatically install the libraires there. Once again make sure to do this while the virtual environment's activated. If it gives an error saying something like how it doesn't know what pip is, make sure the virtual environment's activated.

Now to actually run files, you may first want to make sure you have the project open in an IDE - i'd recommend using VS Code, which you can install here: https://code.visualstudio.com/. You can either use the 'run' button that VS code has, or you can run a file from the terminal, although only if it's a .py file (you can't easily do this for Jupyter notebooks as far as I'm aware, which are the files ending in .ipynb). To run it from the terminal, you just do "python {path to file}/file.py".

Mainly though the general workflow will be:
- pass in an Openrocket file into InputFiles
- then, go to OpenRocketToRocketPy and make sure it points to the right openrocket file, then run it.
- Next, go into FlightParams.py, IterationManager.py, and MonteCarloManager.py to set the values as needed for however you wanna run it
- Finally, go to SimNotebook.ipynb to actually run the file


<h1> Project Structure Explanation </h1>

Here i'll explain a bit more about what all the folders do first, and then all the important files and where they're located.

<h2> Folders Explanation </h2>

Ansys folder:
- folder containing python files we used to run our Ansys Fluent sims. Kinda outdated and I didn't touch it during the refactor since I didn't know exactly what they did.

AvionicsAnalysis folder:
- folder containing notebooks and other files that we'll use for basically analyzing the avionic flight data for useful things, such as the true motor thrust curve.

Helpers folder:
- folder containing all the helper files and libraries that we use for our main sim notebook.

Helpers/FredScript folder:
- this was a project our former chief engineer (shoutout Fred) made to parse an OpenRocket file into python. we then just expanded it to parse the relevant values from that file directly into RocketPy.

InputFiles folder: 
- this is where all files that are used for input to the rocket simulations should go, including things like the motor file, parsed openrocket json file, cd on/off file, and so on.

LegacyFiles folder: 
- contains any files we no longer use, that I still thougth was useful to keep for the future.

Output folder: 
- this is where any files that are generaed by the simulation should go, so say monte carlo outputs and any generated graphs.

rocketpy_repo folder: 
- this is where we have the RocketPy library that we use. More specifically though, we have actually forked (created a copy) of the rocketpy repository, and the rocketpy_repo folder points to our copy. We made a copy for whenever we want to make our own changes to the library.

SimulationNotebooks folder: 
- this is where we store all the notebooks that actually begin the running of simulations, by using some of the important files like FlightParams.py or ConcurrentFunctions.py.

<h2> Important Files Explanation </h2>

Here I'll talk about all the important files you should pay attention to. Most of them are in the helpers folder.

SimulationNotebooks/SimNotebook.ipynb: 
- this is the file that actually runs the sims, collects the results, and writes them to a file / displays them. Ideally wee want to keep it as one singular file, and whenever we want to change things we do that in the helper files like FlightParams.py.

Helpers/Airbrakes.py:
- this makes an airbrake 'superclass', that then all other airbrake implementations should 'inherit' from to define how they work.

Helpers/ConcurrentFunctions.py:
- this is the fctual file that takes in the data from SimNotebook.ipynb to construct the rocket and fly it, with the ability to do monte carlo simulations and run a bunch of flights with slightly different values.

Helpers/FlightParams.py:
- this is where we actually define data about the rocket such as its length, motor data, if we're using monte carlo simulations, and all that. So one of the most important files.

Helpers/IterationManager.py:
- this is basically where we can set if we're going to be doing flights hwere one value will change iteratively each flight, going from one end of a specified range to another, and seeing at different values of that parameter, how it affects the flight output such as its apogee. So for instance we can set the fin position to vary iteratively from 2.6 meters from the nose cone to 3 meters from the nose cone at 0.1 meter increments. This will then run a flight with fin_pos = 2.6, then one at fin_pos = 2.7, and so on until we reach fin_poss = 3.0. Then we'll check at each fin position what data such as the apogee was. We may lowkey never end up using this again, but its good to keep just in case.

Helpers/LookupTable.py:
- One implementation (and currently the only one) of a airbrake controller, that's a subclass of the Airbrakes class. This basically had a 3d matrix filled with deployment values where the first index is the altitude, second index is the velocity, and third index is angle from vertical. Then, we can look up an exact table value using these 3 rocket parameters.

Helpers/MonteCarloManager.py:
- This one manages what parameter values will vary when doing a monte carlo flight, and by how much. For instance, if we don't know the rocket mass but we know it's around 20 kg with a standard deviation of 1 kg, we can run a monte carlo simulation to account for this uncertainty where each flight, we'll randomly sample that rocket mass according to the 20 kg mean and std dev of 1 kg. 

Helpers/OpenRocketToRocketPy.ipynb:
- This one takes in the openrocket file as input, and basically parses it for all the values that RocketPy needs, and saves those into InputFiles/RelevantOpenRocket.json. Some of the values in there aren't necessary tho.

Helpers/SimVisualizers.py:
- This is just a file that holds all the functions to display graphs and plots to the screen, jut put here for cleaner modularity.