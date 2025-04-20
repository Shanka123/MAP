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
I am playing with a set of objects. Here are the actions I can do:

Attack object
Feast object from another object
Succumb object
Overcome object from another object

I have the following restrictions on my actions:
To perform Attack action, the following facts need to be true: Province object, Planet object, Harmony.
Once Attack action is performed the following facts will be true: Pain object.
Once Attack action is performed the following facts will be false: Province object, Planet object, Harmony.
To perform Succumb action, the following facts need to be true: Pain object.
Once Succumb action is performed the following facts will be true: Province object, Planet object, Harmony.    
Once Succumb action is performed the following facts will be false: Pain object.
To perform Overcome action, the following needs to be true: Province other object, Pain object.
Once Overcome action is performed the following will be true: Harmony, Province object, Object Craves other object.
Once Overcome action is performed the following will be false: Province other object, Pain object.
To perform Feast action, the following needs to be true: Object Craves other object, Province object, Harmony.
Once Feast action is performed the following will be true: Pain object, Province other object.
Once Feast action is performed the following will be false:, Object Craves other object, Province object, Harmony.


Here are two examples:

Example 1:

Starting state: As initial conditions I have that, object b craves object c, harmony, planet object a, planet object c, planet object d, province object a, province object b and province object d.
    
All possible next actions from the starting state:

Possible action number 1:
[START] feast object b from object c [END]
Once feast object b from object c is performed the following will be true: pain object b, province object c.
Once feast object b from object c is performed the following will be false: object b craves object c, province object b, harmony.
Next state: As initial conditions I have that, pain object b, planet object a, planet object c, planet object d, province object a, province object c and province object d.


Possible action number 2:
[START] attack object a [END]
Once attack object a is performed the following will be true: pain object a
Once attack object a is performed the following will be false: province object a, planet object a, harmony.
Next state: As initial conditions I have that, pain object a, object b craves object c, planet object c, planet object d, province object b and province object d.



Example 2:

Starting state: As initial conditions I have that, pain object b, planet object a, planet object c, planet object d, province object a, province object c and province object d.

All possible next actions from the starting state:

Possible action number 1:
[START] succumb object b [END]
Once succumb object b is performed the following will be true: province object b, planet object b, harmony.
Once succumb object b is performed the following will be false: pain object b.
Next state: As initial conditions I have that, harmony, planet object a, planet object b, planet object c, planet object d, province object a, province object b, province object c and province object d.

Possible action number 2:
[START] overcome object b from object a [END]
Once overcome object b from object a is performed the following will be true: harmony, province object b, object b craves object a.
Once overcome object b from object a is performed the following will be false: province object a, pain object b.
Next state: As initial conditions I have that, object b craves object a, harmony, planet object a, planet object c, planet object d, province object b, province object c and province object d.

Possible action number 3:
[START] overcome object b from object c [END]
Once overcome object b from object c is performed the following will be true: harmony, province object b, object b craves object c.
Once overcome object b from object c is performed the following will be false: province object c, pain object b.
Next state: As initial conditions I have that, object b craves object c, harmony, planet object a, planet object c, planet object d, province object a, province object b and province object d.


Possible action number 4:
[START] overcome object b from object d [END]
Once overcome object b from object d is performed the following will be true: harmony, province object b, object b craves object d.
Once overcome object b from object d is performed the following will be false: province object d, pain object b.
Next state: As initial conditions I have that, object b craves object d, harmony, planet object a, planet object c, planet object d, province object a, province object b and province object c.



Here is the task:

Starting state: {s}
All possible next actions from the starting state:

First provide each possible next action from the starting state in between a [START] and a [END] token. Then analyse the facts that will be true and false once each action is performed. Finally provide the next state that results after taking each action at the starting state after adding the facts that will be true and removing the facts that will be false in the following format only: “Next state: < >”.


            
'''


value_prompt = '''

I am playing with a set of objects. Here are the actions I can do:

Attack object
Feast object from another object
Succumb object
Overcome object from another object

I have the following restrictions on my actions:
To perform Attack action, the following facts need to be true: Province object, Planet object, Harmony.
Once Attack action is performed the following facts will be true: Pain object.
Once Attack action is performed the following facts will be false: Province object, Planet object, Harmony.
To perform Succumb action, the following facts need to be true: Pain object.
Once Succumb action is performed the following facts will be true: Province object, Planet object, Harmony.    
Once Succumb action is performed the following facts will be false: Pain object.
To perform Overcome action, the following needs to be true: Province other object, Pain object.
Once Overcome action is performed the following will be true: Harmony, Province object, Object Craves other object.
Once Overcome action is performed the following will be false: Province other object, Pain object.
To perform Feast action, the following needs to be true: Object Craves other object, Province object, Harmony.
Once Feast action is performed the following will be true: Pain object, Province other object.
Once Feast action is performed the following will be false:, Object Craves other object, Province object, Harmony.

Goal: The goal is to predict the minimum number of actions required to achieve the goal from the current state. 



Here are three examples:

Example 1:

Current state:
As initial conditions I have that, object b craves object c, harmony, planet object a, planet object c, planet object d, province object a, province object b and province object d.

Goal:
My goal is to have that object c craves object b.

My actions to achieve the goal from the current state:

feast object b from object c 
succumb object b 
attack object c 
overcome object c from object b 


The minimum number of actions required to achieve the goal from the current state is 4.

Answer= 4

Example 2:

Current state:
As initial conditions I have that, object a craves object b, object d craves object c, harmony, planet object b, planet object c, province object a and province object d.

Goal:
My goal is to have that object c craves object a.

My actions to achieve the goal from the current state:

feast object d from object c 
succumb object d 
attack object c
overcome object c from object a 

The minimum number of actions required to achieve the goal from the current state is 4.

Answer = 4

Example 3:

Current state:
As initial conditions I have that, object b craves object c, object c craves object d, object d craves object a, harmony, planet object a and province object b.

Goal:
My goal is to have that object a craves object c and object d craves object a.

My actions to achieve the goal from the current state:

feast object b from object c 
succumb object b 
feast object c from object d 
succumb object c 
feast object d from object a 
overcome object d from object b 
attack object a 
overcome object a from object c 
feast object d from object b 
overcome object d from object a 

The minimum number of actions required to achieve the goal from the current state is 10.

Answer = 10


Here is the task:

Current state: 
{s}
Goal:
{g}

My actions to achieve the goal from the current state:

First give the actions to achieve the goal from the current state. Then give the minimum number of actions required to achieve the goal from the current state as a single integer after "Answer = "

'''

value_last_step_prompt = '''

I am playing with a set of objects. Here are the actions I can do:

Attack object
Feast object from another object
Succumb object
Overcome object from another object

I have the following restrictions on my actions:
To perform Attack action, the following facts need to be true: Province object, Planet object, Harmony.
Once Attack action is performed the following facts will be true: Pain object.
Once Attack action is performed the following facts will be false: Province object, Planet object, Harmony.
To perform Succumb action, the following facts need to be true: Pain object.
Once Succumb action is performed the following facts will be true: Province object, Planet object, Harmony.    
Once Succumb action is performed the following facts will be false: Pain object.
To perform Overcome action, the following needs to be true: Province other object, Pain object.
Once Overcome action is performed the following will be true: Harmony, Province object, Object Craves other object.
Once Overcome action is performed the following will be false: Province other object, Pain object.
To perform Feast action, the following needs to be true: Object Craves other object, Province object, Harmony.
Once Feast action is performed the following will be true: Pain object, Province other object.
Once Feast action is performed the following will be false:, Object Craves other object, Province object, Harmony.

Goal: The goal is to give a judgement (sure/impossible) if the sequence of actions achieve the goal from the starting state without violating any of the restrictions.

Here are two examples:

Example 1:

Starting state:
As initial conditions I have that, object b craves object c, harmony, planet object a, planet object c, planet object d, province object a, province object b and province object d.

Goal:
My goal is to have that object c craves object b.

My actions to achieve the goal from the starting state:

feast object b from object c 
succumb object b 
attack object c 
overcome object c from object b 

Answer: sure

Example 2:

Starting state:
As initial conditions I have that, object a craves object c, object c craves object b, object d craves object a, harmony, planet object b and province object d.

Goal:
My goal is to have that object a craves object d and object d craves object b.

My actions to achieve the goal from the starting state:

feast object c from object b 
succumb object c 
feast object d from object a 
succumb object d 
attack object b 
overcome object b from object d 
attack object a 
overcome object a from object d 


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
    goal_indices = [m.start() for m in re.finditer('craves', goal_extracted)]
    match_flag=1
    for ind in goal_indices:
        if goal_extracted[ind-9:ind+15] not in y[-1]:
            match_flag=0
    if match_flag==1:
        y_len = len(y)
        move_seq = ""
        for i in range(1,y_len,2):
            move_seq+=y[i]+"\n"
           
            
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
        if len(actor_truncated_response)==28 or len(actor_truncated_response)==16 or len(actor_truncated_response)==15 or len(actor_truncated_response)==31:

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

with open('mystery_blocksworld_task_1_plan_generation.json') as f:
    data = json.load(f)
i=0
for instance in tqdm(data["instances"]):
    if i<100:

        max_steps = len(instance['ground_truth_plan'].split("\n"))+3

        s0 = deepcopy(instance['query'].split("[STATEMENT]")[2].split("My goal is to")[0])
        goal = deepcopy(instance['query'].split("[STATEMENT]")[2].split("My plan is as follows:")[0].split("\n")[-3])
        goal_extracted = goal.split("My goal is to have that")[-1]
        goal_indices = [m.start() for m in re.finditer('craves', goal_extracted)]
        

            
       
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
                    if goal_extracted[ind-9:ind+15] not in new_ys[select_id][-1]:
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