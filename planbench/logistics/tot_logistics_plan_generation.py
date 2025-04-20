import itertools
import numpy as np
from functools import partial
from models import gpt

import argparse
from copy import deepcopy
import time
import re
import json
import os
import pickle
from tqdm import tqdm

value_cache = {}


propose_prompt = '''

I have to plan logistics to transport packages within cities via trucks and between cities via airplanes. Locations within a city are directly connected (trucks can move between any two such locations), and so are the cities. In each city there is exactly one truck and each city has one location that serves as an airport.
Here are the actions that can be performed:

Load a package into a truck. For example, load package_1 into truck_1 at location_1_1.
Load a package into an airplane. For example, load package_1 into airplane_1 at location_1_1.
Unload a package from a truck. For example, unload package_1 from truck_1 at location_1_1.
Unload a package from an airplane. For example, unload package_1 from airplane_1 at location_1_1.
Drive a truck from one location to another location. For example, drive truck_1 from location_1_1 to location_1_2 in city_1.
Fly an airplane from one city to another city. For example, fly airplane_1 from location_1_1 to location_2_1. Here location_1_1 is the airport in city_1 and location_2_1 is the airport in city_2.

The following are the restrictions on the actions:
A package can be loaded into a truck only if the package and the truck are in the same location.
Once a package is loaded into a truck, the package is not at the location and is in the truck.   
A package can be loaded into an airplane only if the package and the airplane are in the same location.
Once a package is loaded into an airplane, the package is not at the location and is in the airplane.
A package can be unloaded from a truck only if the package is in the truck.
Once a package is unloaded from a truck, the package is not in the truck and is at the location of the truck.
A package can be unloaded from an airplane only if the package in the airplane.
Once a package is unloaded from an airplane, the package is not in the airplane and is at the location of the airplane.   
A truck can be driven from one location to another if the truck is at the from-location and both from-location and to-location are locations in the same city.
Once a truck is driven from one location to another, it is not at the from-location and is at the to-location.
An airplane can be flown from one city to another if the from-location and the to-location are airports and the airplane is at the from-location.
Once an airplane is flown from one city to another the airplane is not at the from-location and is at the to-location.


Here are two examples:

Example 1:

Starting state: As initial conditions I have that, location_0_0 is an airport, location_1_0 is an airport, airplane_0 is at location_0_0, airplane_1 is at location_0_0, package_0 is at location_1_0, truck_0 is at location_0_0, truck_1 is at location_1_0, location_0_0 is in the city city_0 and location_1_0 is in the city city_1.
    
All possible next actions from the starting state:

Possible action number 1:
[START] fly airplane_1 from location_0_0 to location_1_0 [END]
Next state: As initial conditions I have that, location_0_0 is an airport, location_1_0 is an airport, airplane_0 is at location_0_0, airplane_1 is at location_1_0, package_0 is at location_1_0, truck_0 is at location_0_0, truck_1 is at location_1_0, location_0_0 is in the city city_0 and location_1_0 is in the city city_1.
    

Possible action number 2:
[START] fly airplane_0 from location_0_0 to location_1_0 [END]
Next state: As initial conditions I have that, location_0_0 is an airport, location_1_0 is an airport, airplane_0 is at location_1_0, airplane_1 is at location_0_0, package_0 is at location_1_0, truck_0 is at location_0_0, truck_1 is at location_1_0, location_0_0 is in the city city_0 and location_1_0 is in the city city_1.
   

Possible action number 3:
[START] load package_0 into truck_1 at location 1_0 [END]
Next state: As initial conditions I have that, location_0_0 is an airport, location_1_0 is an airport, airplane_0 is at location_0_0, airplane_1 is at location_0_0, package_0 is in truck_1, truck_0 is at location_0_0, truck_1 is at location_1_0, location_0_0 is in the city city_0 and location_1_0 is in the city city_1.
   

Example 2:

Starting state: As initial conditions I have that, location_0_0 is an airport, location_1_0 is an airport, airplane_0 is at location_0_0, package_0 is at location_0_1, truck_0 is at location_0_0, truck_1 is at location_1_1, location_0_0 is in the city city_0, location_0_1 is in the city city_0, location_1_0 is in the city city_1 and location_1_1 is in the city city_1.

All possible next actions from the starting state:

Possible action number 1:
[START] drive truck_0 from location_0_0 to location_0_1 in city_0 [END]
Next state: As initial conditions I have that, location_0_0 is an airport, location_1_0 is an airport, airplane_0 is at location_0_0, package_0 is at location_0_1, truck_0 is at location_0_1, truck_1 is at location_1_1, location_0_0 is in the city city_0, location_0_1 is in the city city_0, location_1_0 is in the city city_1 and location_1_1 is in the city city_1.

Possible action number 2:
[START] drive truck_1 from location_1_1 to location_1_0 in city_1 [END]
Next state: As initial conditions I have that, location_0_0 is an airport, location_1_0 is an airport, airplane_0 is at location_0_0, package_0 is at location_0_1, truck_0 is at location_0_0, truck_1 is at location_1_0, location_0_0 is in the city city_0, location_0_1 is in the city city_0, location_1_0 is in the city city_1 and location_1_1 is in the city city_1.

Possible action number 3:
[START] fly airplane_0 from location_0_0 to location_1_0 [END]
Next state: As initial conditions I have that, location_0_0 is an airport, location_1_0 is an airport, airplane_0 is at location_1_0, package_0 is at location_0_1, truck_0 is at location_0_0, truck_1 is at location_1_1, location_0_0 is in the city city_0, location_0_1 is in the city city_0, location_1_0 is in the city city_1 and location_1_1 is in the city city_1.

   


Here is the task:

Starting state: {s}
All possible next actions from the starting state:

Please note that just because a package is in a truck at location A doesn’t mean the package is at location A, the package needs to be unloaded before it’s at location A.
    
First provide each possible next action from the starting state in between a [START] and a [END] token. Then please provide your answer for the next state that results after taking each action at the starting state in the following format only: “Next state: < >”.


            
'''


value_prompt = '''

I have to plan logistics to transport packages within cities via trucks and between cities via airplanes. Locations within a city are directly connected (trucks can move between any two such locations), and so are the cities. In each city there is exactly one truck and each city has one location that serves as an airport.
Here are the actions that can be performed:

Load a package into a truck. For example, load package_1 into truck_1 at location_1_1.
Load a package into an airplane. For example, load package_1 into airplane_1 at location_1_1.
Unload a package from a truck. For example, unload package_1 from truck_1 at location_1_1.
Unload a package from an airplane. For example, unload package_1 from airplane_1 at location_1_1.
Drive a truck from one location to another location. For example, drive truck_1 from location_1_1 to location_1_2 in city_1.
Fly an airplane from one city to another city. For example, fly airplane_1 from location_1_1 to location_2_1. Here location_1_1 is the airport in city_1 and location_2_1 is the airport in city_2.

The following are the restrictions on the actions:
A package can be loaded into a truck only if the package and the truck are in the same location.
Once a package is loaded into a truck, the package is not at the location and is in the truck.   
A package can be loaded into an airplane only if the package and the airplane are in the same location.
Once a package is loaded into an airplane, the package is not at the location and is in the airplane.
A package can be unloaded from a truck only if the package is in the truck.
Once a package is unloaded from a truck, the package is not in the truck and is at the location of the truck.
A package can be unloaded from an airplane only if the package in the airplane.
Once a package is unloaded from an airplane, the package is not in the airplane and is at the location of the airplane.   
A truck can be driven from one location to another if the truck is at the from-location and both from-location and to-location are locations in the same city.
Once a truck is driven from one location to another, it is not at the from-location and is at the to-location.
An airplane can be flown from one city to another if the from-location and the to-location are airports and the airplane is at the from-location.
Once an airplane is flown from one city to another the airplane is not at the from-location and is at the to-location.


Goal: The goal is to predict the minimum number of actions required to achieve the goal from the current state. 


Here are three examples:

Example 1:

Current state:
As initial conditions I have that, location_0_0 is an airport, location_1_0 is an airport, airplane_0 is at location_0_0, airplane_1 is at location_0_0, package_0 is at location_1_0, truck_0 is at location_0_0, truck_1 is at location_1_0, location_0_0 is in the city city_0 and location_1_0 is in the city city_1.

Goal:
My goal is to have that package_0 is at location_0_0.

My actions to achieve the goal from the current state:

[START] fly airplane_1 from location_0_0 to location_1_0 [END]
[START] load package_0 into airplane_1 at location_1_0 [END]
[START] fly airplane_1 from location_1_0 to location_0_0 [END]
[START] unload package_0 from airplane_1 at location_0_0 [END]

The minimum number of actions required to achieve the goal from the current state is 4.

Answer = 4

Example 2:

Current state:
As initial conditions I have that, location_0_0 is an airport, location_1_0 is an airport, airplane_0 is at location_1_0, package_0 is at location_1_0, truck_0 is at location_0_0, truck_1 is at location_1_0, location_0_0 is in the city city_0, location_0_1 is in the city city_0, location_1_0 is in the city city_1 and location_1_1 is in the city city_1.

Goal:
My goal is to have that package_0 is at location_1_1.

My actions to achieve the goal from the current state:

[START] load package_0 into truck_1 at location_1_0 [END]
[START] drive truck_1 from location_1_0 to location_1_1 in city_1 [END]
[START] unload package_0 from truck_1 at location_1_1 [END]

The minimum number of actions required to achieve the goal from the current state is 3.

Answer = 3

Example 3:

Current state:
As initial conditions I have that, location_0_0 is an airport, location_1_0 is an airport, airplane_0 is at location_0_0, package_0 is at location_0_1, truck_0 is at location_0_0, truck_1 is at location_1_1, location_0_0 is in the city city_0, location_0_1 is in the city city_0, location_1_0 is in the city city_1 and location_1_1 is in the city city_1.

Goal:
My goal is to have that package_0 is at location_1_0.

My actions to achieve the goal from the current state:

[START] drive truck_0 from location_0_0 to location_0_1 in city_0 [END]
[START] load package_0 into truck_0 at location_0_1 [END]
[START] drive truck_0 from location_0_1 to location_0_0 in city_0 [END]
[START] unload package_0 from truck_0 at location_0_0 [END]
[START] load package_0 into airplane_0 at location_0_0 [END]
[START] fly airplane_0 from location_0_0 to location_1_0 [END]
[START] unload package_0 from airplane_0 at location_1_0 [END]

The minimum number of actions required to achieve the goal from the current state is 7.

Answer = 7



Here is the task:

Current state: 
{s}
Goal:
{g}

My actions to achieve the goal from the current state:

First give the actions to achieve the goal from the current state. Then give the minimum number of actions required to achieve the goal from the current state as a single integer after "Answer = "

'''

value_last_step_prompt = '''

I have to plan logistics to transport packages within cities via trucks and between cities via airplanes. Locations within a city are directly connected (trucks can move between any two such locations), and so are the cities. In each city there is exactly one truck and each city has one location that serves as an airport.
Here are the actions that can be performed:

Load a package into a truck. For example, load package_1 into truck_1 at location_1_1.
Load a package into an airplane. For example, load package_1 into airplane_1 at location_1_1.
Unload a package from a truck. For example, unload package_1 from truck_1 at location_1_1.
Unload a package from an airplane. For example, unload package_1 from airplane_1 at location_1_1.
Drive a truck from one location to another location. For example, drive truck_1 from location_1_1 to location_1_2 in city_1.
Fly an airplane from one city to another city. For example, fly airplane_1 from location_1_1 to location_2_1. Here location_1_1 is the airport in city_1 and location_2_1 is the airport in city_2.

The following are the restrictions on the actions:
A package can be loaded into a truck only if the package and the truck are in the same location.
Once a package is loaded into a truck, the package is not at the location and is in the truck.   
A package can be loaded into an airplane only if the package and the airplane are in the same location.
Once a package is loaded into an airplane, the package is not at the location and is in the airplane.
A package can be unloaded from a truck only if the package is in the truck.
Once a package is unloaded from a truck, the package is not in the truck and is at the location of the truck.
A package can be unloaded from an airplane only if the package in the airplane.
Once a package is unloaded from an airplane, the package is not in the airplane and is at the location of the airplane.   
A truck can be driven from one location to another if the truck is at the from-location and both from-location and to-location are locations in the same city.
Once a truck is driven from one location to another, it is not at the from-location and is at the to-location.
An airplane can be flown from one city to another if the from-location and the to-location are airports and the airplane is at the from-location.
Once an airplane is flown from one city to another the airplane is not at the from-location and is at the to-location.

Goal: The goal is to give a judgement (sure/impossible) if the sequence of actions achieve the goal from the starting state without violating any of the restrictions.

Here are two examples:

Example 1:

Starting state:
As initial conditions I have that, location_0_0 is an airport, location_1_0 is an airport, airplane_0 is at location_0_0, airplane_1 is at location_0_0, package_0 is at location_1_0, truck_0 is at location_0_0, truck_1 is at location_1_0, location_0_0 is in the city city_0 and location_1_0 is in the city city_1.

Goal:
My goal is to have that package_0 is at location_0_0.

My actions to achieve the goal from the starting state:

[START] fly airplane_1 from location_0_0 to location_1_0 [END]
[START] load package_0 into airplane_1 at location_1_0 [END]
[START] fly airplane_1 from location_1_0 to location_0_0 [END]
[START] unload package_0 from airplane_1 at location_0_0 [END]

Answer: sure

Example 2:

Starting state:
As initial conditions I have that, location_0_0 is an airport, location_1_0 is an airport, airplane_0 is at location_1_0, package_0 is at location_1_0, package_1 is at location_0_0, truck_0 is at location_0_0, truck_1 is at location_1_0, location_0_0 is in the city city_0 and location_1_0 is in the city city_1.

Goal:
My goal is to have that package_0 is at location_1_0 and package_1 is at location_1_0.


My actions to achieve the goal from the starting state:

[START] load package_1 into airplane_0 at location_0_0 [END]
[START] fly airplane_0 from location_0_0 to location_1_0 [END]
[START] unload package_1 from airplane_0 at location_1_0 [END]


Answer: impossible

Here is the task:

Starting state:
{s}

Goal:
{g}


My actions to achieve the goal from the starting state:

{move_seq}

Answer:

'''
def check_path(path):
    if not os.path.exists(path):
        os.mkdir(path)


def value_outputs_unwrap(value_outputs: list,last_step_flag) -> float:
    v = 0 
    for output in value_outputs:

        if not last_step_flag:
            if "impossible" in output or "not possible" in output:
                v+=50
            else:




       


                # first_index = 0
                # for k in range(len(output) - 83):
                #     if output[k:k+84] == 'The minimum number of actions required to achieve the goal from the current state is' or output[k:k+84] == 'the minimum number of actions required to achieve the goal from the current state is':
                #         first_index = k
                            

                # second_index = 0
                # for t in range(first_index, len(output)):
                #     if output[t] == '.' or output[t] == ',' :
                #         second_index = t
                #         break

                # if len(output[first_index:second_index].split(" ")[-1])<=2 and first_index!=0 and ")" not in output[first_index:second_index].split(" ")[-1] and "A" not in output[first_index:second_index].split(" ")[-1] and "B" not in output[first_index:second_index].split(" ")[-1] and "C" not in output[first_index:second_index].split(" ")[-1] :

                   
                try:
                    if "**" in output.split("Answer = ")[-1]:
                        v+= int(output.split("Answer = ")[-1].split('\n')[0].split("**")[0])
                    
                    else:


                        v+= int(output.split("Answer = ")[-1].split('\n')[0])
                    # if "**" in output[first_index:second_index]:
                    #     v+=int(output[first_index:second_index].split(" ")[-1].split("**")[1])

                    # else:
                        
                        
                    #     v+=int(output[first_index:second_index].split(" ")[-1])

                
                  
                    
                except Exception as e:
                    err = f"Error: {str(e)}"
                    print(err)
                    print("error in getting minimum number of actions, hence assuming can't be solved")

                    v+=50
        
        else:

            if "sure" in output:
                v+=0
            else:
                v+=100

           


            

   
   
    return v

def get_value( y,goal, n_evaluate_sample):
    global input_tokens
    global output_tokens
    global response_time
    goal_extracted = goal.split("My goal is to have that")[-1]
    goal_indices = [m.start() for m in re.finditer('is at', goal_extracted)]
    match_flag=1
    for ind in goal_indices:
        if goal_extracted[ind-10:ind+18] not in y[-1]:
            match_flag=0
    if match_flag==1:
        y_len = len(y)
        move_seq = ""
        for i in range(1,y_len,2):
            move_seq+="[START] "+y[i]+ " [END]"+ "\n"
           
            
        prompt = value_last_step_prompt.format(s = str(y[-y_len]) , g = str(goal), move_seq= move_seq)
        last_step_flag = True
    else:

        prompt = value_prompt.format(s = str(y[-1]), g=str(goal) )
        last_step_flag = False
    print("value_prompt>>>",prompt)
    if prompt in value_cache:
        return value_cache[prompt]

    
   
    value_outputs,_, inp_tokens, op_tokens, rp_time = gpt(prompt,empty_response = 0 , n=n_evaluate_sample, stop=None)

    input_tokens.append(inp_tokens)
    output_tokens.append(op_tokens)
    response_time.append(rp_time)
    print("value_outputs>>>",value_outputs)
    value = value_outputs_unwrap(value_outputs,last_step_flag)
    print("value>>>",value)
    value_cache[prompt] = value
    return value

def get_values(ys,goal, n_evaluate_sample):
    values = []

    for y in ys:  # each partial output
     

        value = get_value( y,goal, n_evaluate_sample)
           
            
        values.append(value)
    return values

def extract_moves_configs(response):
    all_moves = []
    all_states = []

    start_indices = []
    end_indices = []
    next_state_indices = []
    for i in range(len(response)-7):
        if response[i:i+7] =="[START]":
            start_indices.append(i)
    for i in range(len(response)-5):
        if response[i:i+5] =="[END]":
            end_indices.append(i)

    for i in range(len(response)-10):
        if response[i:i+10] =="Next state":
            next_state_indices.append(i)

    
                
                    
    for start,end in zip(start_indices,end_indices):
        actor_truncated_response = response[start + len( "[START]" ) :end].replace('.','').strip()
        if len(actor_truncated_response)==43 or len(actor_truncated_response)==45 or len(actor_truncated_response)==46 or len(actor_truncated_response)==48 or len(actor_truncated_response)==57:

            all_moves.append(actor_truncated_response)
    next_state_indices.append(len(response))
    for k in range(len(next_state_indices)-1):
        all_states.append(response[next_state_indices[k]:next_state_indices[k+1]].split("Next state:")[-1].split(".")[0]+".")
    
    return all_moves, all_states
                

def get_proposals( y): 
    global input_tokens
    global output_tokens
    global response_time
    
    prompt = propose_prompt.format(s= str(y[-1]))
    proposals,messages, inp_tokens, op_tokens, rp_time = gpt(prompt,empty_response=0, n=1, stop=None)
    input_tokens.append(inp_tokens)
    output_tokens.append(op_tokens)
    response_time.append(rp_time)
    print("gpt proposals response>>", proposals[0])
    all_moves, all_states = extract_moves_configs(proposals[0])
    while not(len(all_moves)==len(all_states) and len(all_moves)>0):
        proposals,messages, inp_tokens, op_tokens, rp_time = gpt(prompt,empty_response=0, n=1, stop=None)
        input_tokens.append(inp_tokens)
        output_tokens.append(op_tokens)
        response_time.append(rp_time)
        print("gpt proposals response>>", proposals[0])
        all_moves, all_states = extract_moves_configs(proposals[0])

           
    state_move_state=[]
    for move,state in zip(all_moves,all_states):
        temp = deepcopy(y)
        temp.append(move)
        temp.append(state)
        state_move_state.append(temp)


    return state_move_state




global gpt
gpt = partial(gpt, temperature=0.7)
print(gpt)

# ys = ['']  # current output candidates
parser = argparse.ArgumentParser()

parser.add_argument
parser.add_argument('--output_dir',type=str, help='directory name where output log files will be stored', required= True)
args = parser.parse_args()
print(args)

with open('task_1_plan_generation.json') as f:
    data = json.load(f)
i=0
for instance in tqdm(data["instances"]):
    if i<100:

        max_steps = len(instance['ground_truth_plan'].split("\n"))+3

        s0 = deepcopy(instance['query'].split("[STATEMENT]")[2].split("My goal is to")[0])
        goal = deepcopy(instance['query'].split("[STATEMENT]")[2].split("My plan is as follows:")[0].split("\n")[-3])
        goal_extracted = goal.split("My goal is to have that")[-1]
        goal_indices = [m.start() for m in re.finditer('is at', goal_extracted)]
        

            
       
        ys = [[s0]]
        potential_solutions = []
        input_tokens = [] 
        output_tokens = []
        response_time = [] 
        start_time = time.time()

        print("start state>>>",ys)
        for step in range(max_steps):
            # generation
            print("step>>",step)
            new_ys = [get_proposals(y) for y in ys]
           


            new_ys = list(itertools.chain(*new_ys))
            print("after all proposals>>",new_ys)
            ids = list(range(len(new_ys)))
            # evaluation
           
          

            values = get_values(new_ys,goal, 3)

            print("values of proposals>>>",values)

            # selection
           
           
            select_ids = sorted(ids, key=lambda x: values[x], reverse=False)[:5]
            print("select ids>>>",select_ids)
            select_new_ys = []
            for select_id in select_ids:
                match_flag=1
                for ind in goal_indices:
                    if goal_extracted[ind-10:ind+18] not in new_ys[select_id][-1]:
                        match_flag=0
                if match_flag==1:
                    print("goal state reached>>>")
                    potential_solutions.append(new_ys[select_id])
                else:
                    select_new_ys.append(new_ys[select_id])

            # select_new_ys = [new_ys[select_id] if  for select_id in select_ids]
        
            print("selected proposals>>",select_new_ys)

            # log
            
            ys = select_new_ys
        
        potential_solutions+= ys
         
        print("all potential solutions>>>",potential_solutions)

        test_dir = './logs/'
        check_path(test_dir)
        output_dir = test_dir + args.output_dir + '/'
        check_path(output_dir)
       
        end_time = time.time()

        with open(output_dir+'problem{}.pkl'.format(i+1), 'wb') as f:
            pickle.dump(potential_solutions, f)

        np.savez(output_dir+'problem{}_tokens_times.npz'.format(i+1),num_input_tokens = input_tokens, num_output_tokens = output_tokens,response_times  = response_time, total_time = [end_time - start_time])

        print("done solving problem {}".format(i+1))
        i=i+1
   
# if __name__ == '__main__':

#     solve()