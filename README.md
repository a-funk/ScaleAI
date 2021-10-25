# ScaleAI - Data Annotation Flag
### Label Variety Check
This tool leverages ScaleSDK to flag tasks that lack a variety of label types.  
---
First step is to make a folder called 'key' inside of 'project' folder

From ScaleAI directory type 'mkdir project/key' into your terminal 

Then enter 'touch project/key/key.json'

Then edit the json so it is of the form:

{"api_key" : "YOUR_KEY_HERE"}

Save the file and you should be good to go.


You have two options to run this project:

    1. Run the .py file  
    2. Run the jupyter notebook


Instructions for 1:
This project has the following dependencies that need to be installed for it to work. 
    
    - requests
    
    - numpy 
    
    - pandas 
    
    - scaleapi
    
    - os
    
    - json
    
    - datetime 
    
    - math
    
    - sys
Once these are installed (pip installer recommended), use 'python3 scale_qc.py' to run the project.

Instructions for 2:
Launch the jupyter notebook found in the project folder.  If you do not have Jupyter, install information can be found [here](https://jupyter.org/install).
