# fus-mesh-challenge
SRI FUS interview technical challenge submission.

## Repo Tour
There are 3 main files in this repo:
1. mesh_model.py \
This is the model for all mesh creation and manipulation. 
2. app.py \
The GUI! This creates the view and connects the user input to the mesh operations provided by the model. 
3. test_MeshModel.py \
Unit tests. These only test the functions requested by the assignment, test coverage does not extend to the additional functions I added to make the GUI a little more interesting. 

## Getting it Running
1. Set up a virtual environment, source it, and install the project dependencies.
```
python -m venv /path/to/new/virtual/environment
source /path/to/new/virtual/environment/bin/activate
pip install -Ir requirements.txt
```
2. For Part A and B, launch the GUI.
```
python app.py
```
3. For Part D, run pytest tool to launch the tests.
```
pytest
```

## Linux vs. Windows
I created this program using Ubuntu 22.04, however I have tested on a Windows machine and the program works as intended. If you want to run this on Windows, just beware that to activate your virtual environment you will have to run the following command instead of sourcing /path/to/new/virtual/environment/bin/activate.
```
cd /path/to/new/virtual/environment/Scripts && activate
```

## Assignment Function Map
Not all code included here is answering the assignment questions. If you want to jump straight to the assignment answers, see map below:

Part A --> See mesh_model.py, functions setSphereSource (line 38) and setConeSource (line 57).\
Part B --> See mesh_model.py, function scaleMesh (line 157).\
Part C --> See mesh_model.py, function compareMeshes(line 218).\
Part D --> See test_MeshModel.py for all unit tests.
