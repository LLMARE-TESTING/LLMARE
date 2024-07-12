# LLMARE
Reproducing User-Described Scenarios in App Reviews with LLM
# LLMARE

## About

This repository contains the code for the system for the paper: 

LLMARE is a LLM-based system for reproducing user-described scenarios in app reviews. It can automatically reproduce the scenarios described in user reviews, and save screenshots of the reproduction process along with records of the executed actions and other related information.

## About the project

Organization of the Dataset:

```
/LLMARE
├── /app
│   ├── photos_activity
│   │   ├── activity
│   │   |   ├── .create.CreateActivity
│   │   |   ├── ...
│   │   |   └── .envelope.AlbumActivity
│   │   ├── output
│   │   |   ├── record
│   │   |   └── screenshot
│   │   ├── comments.xlsx
│   │   ├── activity_function.json
│   │   ├── page_html.json
│   │   ├── activity_task.json
│   │   ├── state_task.json
│   │   ├── utg.js
│   │   └── utg_add.js
│   ├── pinterest_activity
│   │   ├── activity
│   │   ├── ...
│   │   └── utg_add.js
│   ├── ...
│   │   ├── activity
│   │   ├── ...
│   │   └── utg_add.js
├── /gpt
│   └── gpt.py
├── /scripts
│   ├── commands.py
│   ├── comment.py
│   ├── explore.py
│   ├── tools.py
│   └── generate_comments.py

```

- LLMARE: Project Directory
- app: Save the test application data.
  - activity: Classify the application's **state files(xml or json)** according to the activity to which the application state belongs.
  - comment.xlsx: Save user comments for testing.
  - activity_function.json: A functional summary of the activity based on a list of its subtasks.
  - page_html.json: Save the HTML representation of each page obtained during the exploration phase.
  - activity_task.json: Save a list of subtasks for each activity.
  - state_task.json: Save a list of subtasks for each state.
  - utg.js: The transition relationship information between states obtained by DroidBot during the exploration phase.
  - utg_add.js: Artificially supplemented state and state transition relationship information.
  - output: Save the test results file. 
    - record: The information about the actions executed, the selected target activities and the target status during the test of each comment is saved in this directory.
    - screenshot: Screenshots of each comment during testing is saved in this folder. 
- gpt: gpt.py stores functions for interacting with the large language model.
- scripts:
  - commands.py: This file saves some instructions and examples needed to interact with the large language model during the test.
  - comment.py: This file is a script file that implements the entire process of reproducing the user-described scenario, corresponding to the functions of LLMARE in the target identfication stage and scenario reproduction stage.
  - explore.py: This script summarizes each state and activity based on the viewtree file of the page, corresponding to the functions of LLMARE in the pre-exploration stage. The output files after the script is executed include activity_function.json,page_html.json,activity_task.json,state_task.json.
  - tools.py: This file holds functions such as converting the viewtree into HTML representation, comparing page similarities, and taking screenshots etc.
  - generate_comments.py: This script is used to determine whether the scenario described in the user's comment is reproducible and extract the corresponding key information. Its output files is comment.xlsx. 

## Prerequisite

**Environmental Requirements:**

1.Python:  install the corresponding software library "pip install -e ."

2.Android SDK

3.Appium

## How to use

**Usage Steps**:

**1.Upload data:** save the user comments you want to test in the "**comment.xlsx**" file. 

**2.Modify parameters:**

- change the "app_name" in comment.py to the corresponding file directory in the app folder. 
- You can ensure that the target application is started by modifying the key value in the capabilities variable in comment.py.

**3.Start Appium**

**4.Run comment.py**

