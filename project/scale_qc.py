import requests
import numpy as np
import pandas as pd
import scaleapi
import os
import json
from datetime import datetime
import math
import sys
from scaleapi.tasks import TaskReviewStatus, TaskStatus


def list_projects(client):
    # Input:
    #   client : scaleSDK client object
    # Returns:
    #   NOTHING - prints project name
    counter = 0
    project_map = {}
    projects = client.projects()
    for project in projects:
        counter += 1
        project_map[str(counter)] = project.name
        print(f'{counter} | {project.name} | {project.type}')
    return project_map
    
    
def select_project(project_map):
    # Input: 
    #   None
    # Returns: 
    #   project_name string
    print("------------------------------------------")
    print("Which project would you like to test?")
    print("Please input a number from the list above: ")
    project_num = input()
    if(project_num in project_map.keys()):
        project_name = project_map[project_num]
        print("Project: "+project_name+" selected.")
        return project_name
    else:
        print("Please input a valid project number.")
        return -1

def list_tasks(client, project_name="Traffic Sign Detection"):
    # Input:
    #   client : scaleSDK client object 
    #   project_name : project name string 
    # Returns:
    #   task_ids : list of task ids(strings).
    #   num_tasks : number of tasks total in the project
    # Runtime: 
    #   O(n): n = number of tasks
    tasks = client.get_tasks(
        project_name = project_name
    )
    num_tasks=0
    task_ids = []
    for task in tasks:
        num_tasks = num_tasks+1
        task_ids.append(task.task_id)

    # For retrieving results as a Task list
    task_list = list(tasks)
    print(str(num_tasks)+" tasks retrieved")
    return task_ids, num_tasks

def get_task(client, task_id='5f127f6f26831d0010e985e5'):
    # Input: 
    #   task_id : task id string
    # Returns:
    #   task_id : task id string
    #   task    : task information dict
    # Runtime: 
    #   O(1)

    task = client.get_task(task_id)
    print(task.status)  
    # Task status ("pending", "completed", "error", "canceled")
    if(task.status == "completed"):
        return task_id, task, True
    else: 
        print("Task not complete.")
        print("------------------")
        return -1, {}, False


def get_num_unique_labels(task):
    # Input: 
    #   task : task information dict
    # Returns:
    #   num_unique_labels : number of unique label types in a task int
    # Runtime: 
    #   O(m) number of labels in a given task
    #   NOTE: pd.unique is quite well optimized
    
    tasks_df = pd.DataFrame(task.response['annotations'])
    num_unique_labels = len(pd.unique(tasks_df['label']))  # O(m)
    print("Number of unique label types: "+str(num_unique_labels))
    return num_unique_labels

def create_dict(task_id, task, num_unique_labels):
    # Input:
    #   task_id : task_id string
    #   task    : task information dict
    #   num_unique_lables : number of unique label types in a task int
    # Returns:
    #   task_id : task_id string
    #   num_dict : dictionary 
    # Runtime: 
    #   O(1)
    num_dict = {
            "task_id" : task_id,
            "task" : task,
            "num_unique_labels": num_unique_labels
    }
    
    return task_id,num_dict


# Average here can be changed to median, anything really to improve this tool
def create_output_dict(task_id, task, num_unique_labels, limit):
    # Input:
    #   task_id : task_id string
    #   task    : task information dict
    #   num_unique_lables : number of unique label types in a task int
    #   limit : in this current implementation this limit is the average
    # Returns:
    #   output_dict : dictionary that contains flag information for a given task
    # Runtime: 
    #   O(1)
    
    if(num_unique_labels < limit):
        flag = True
    else:
        flag = False
    # NOTE a 'True' flag means that a flag should be triggered. 
    output_dict = {
            "task_id" : task_id,
            "average_unique_labels" : limit,
            "num_unique_labels": num_unique_labels,
            "flag": flag
    }
    return output_dict

def make_output(output_dict, project_name):
    # Input: 
    #   output_dict: dictionary to be saved as json file
    # Returns:
    #   NOTHING - saves json file to output/ folder

    # Makes new output folder
    path = os.getcwd()
    newpath = path+"/output/"
    if not os.path.exists(newpath):
        os.makedirs(newpath)

    # Makes output json file
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    json_object = json.dumps(output_dict, indent = 4) 
    print(json_object)
    filename =  "./output/variety_flags_"+project_name+".json"
    with open(filename, "w") as outfile:
        json.dump(output_dict, outfile)

# Overall complexity : O(N*M)
#   n = number of tasks
#   m = number of labels per task
def main():
    api_key="live_ed802f9607c14973a63a0b5ebefafcad" # Live one
    client = scaleapi.ScaleClient(api_key)
    
    project_map = list_projects(client)
    project_name = select_project(project_map)

    unique_labels_dict = {}
    num_unique_labels_sum = 0
    tasks, num_tasks = list_tasks(client=client, project_name=project_name)  # O(n) : n = number of tasks

    # Many ways to optimize here - either do it with moving average, median number of label types or another method 
    # like assuming normal distribution and find exptected number of label types
    # Complexity : O(n*m) where m<n 
    #               n = number of tasks
    #               m = number of labels per task 
    for task_id in tasks:
        task_id, task, done = get_task(client=client,task_id=task_id)
        if(not done):
            print("Please wait for all tasks to complete before running QC.")
            return -1
        num_unique_labels = get_num_unique_labels(task=task)  # Runtime : O(m)
        num_unique_labels_sum = num_unique_labels_sum + num_unique_labels
        task_id, value = create_dict(task_id=task_id,task=task,num_unique_labels=num_unique_labels)
        unique_labels_dict[task_id] = value
    if(num_tasks!=0):
        average_unique_labels = math.ceil(num_unique_labels_sum/num_tasks)
    else:
        average_unique_labels = 0 
    print("Average unique labels: " +str(average_unique_labels))
    
    output_dict = {}
    # Complexity : O(n) where n = number of tasks
    for task_id in tasks:
        output_dict[task_id] = create_output_dict(
            task_id = unique_labels_dict[task_id]['task_id'], 
            task=unique_labels_dict[task_id]['task'],            
            num_unique_labels=unique_labels_dict[task_id]['num_unique_labels'], 
            limit=average_unique_labels
        )
    print(output_dict.keys())

    print("A 'True' status indicates that a task needs to be reviewed.")
    # Complexity : O(n) where n = number of tasks
    # This is also just to make pretty output and is not necessary for json out
    for task_id in tasks:
        print(str(task_id)+" : "+str(output_dict[task_id]['flag']))
    make_output(output_dict, project_name)


if __name__ == "__main__":
    main()
