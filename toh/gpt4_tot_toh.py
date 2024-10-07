import itertools
import numpy as np
from functools import partial
from models import gpt
from gen_start_config import *
import argparse
from copy import deepcopy
import time
import re
import json
import os
import pickle
all_As, all_Bs, all_Cs = generate_all_start_config()

value_cache = {}


propose_prompt = '''
Problem description:
- There are three lists labeled A, B, and C.
- There is a set of numbers distributed among those three lists.
- You can only move numbers from the rightmost end of one list to the rightmost end of another list.

Rule #1: You can only move a number if it is at the rightmost end of its current list.
Rule #2: You can only move a number to the rightmost end of a list if it is larger than the other numbers in that list.

A move is valid if it satisfies both Rule #1 and Rule #2.
A move is invalid if it violates either Rule #1 or Rule #2.


Here are two examples:

Example 1:

Starting configuration: A = [0, 1], B = [2], C = []
All possible valid next moves from the starting configuration:

Possible move number 1:
Starting configuration:
A = [0, 1]
B = [2]
C = []
Move 2 from B to C 
Current configuration: 
A = [0, 1]
B = []
C = [2]

Possible move number 2:
Starting configuration:
A = [0, 1]
B = [2]
C = []
Move 1 from A to C 
Current configuration: 
A = [0]
B = [2]
C = [1]

Possible move number 3:
Starting configuration:
A = [0, 1]
B = [2]
C = []
Move 2 from B to A 
Current configuration: 
A = [0, 1, 2]
B = []
C = []

Example 2:

Starting configuration: A = [1], B = [0], C = [2]
All possible valid next moves from the starting configuration:

Possible move number 1:
Starting configuration:
A = [1]
B = [0]
C = [2]
Move 2 from C to A 
Current configuration: 
A = [1, 2]
B = [0]
C = []

Possible move number 2:
Starting configuration:
A = [1]
B = [0]
C = [2]
Move 2 from C to B 
Current configuration: 
A = [1]
B = [0, 2]
C = []

Possible move number 3:
Starting configuration:
A = [1]
B = [0]
C = [2]
Move 1 from A to B 
Current configuration: 
A = []
B = [0, 1]
C = [2]

Here is the task:

Starting configuration: A = {a}, B = {b}, C = {c}
All possible valid next moves from the starting configuration:

            
'''


value_prompt = '''

Problem description:
- There are three lists labeled A, B, and C.
- There is a set of numbers distributed among those three lists.
- You can only move numbers from the rightmost end of one list to the rightmost end of another list.
Rule #1: You can only move a number if it is at the rightmost end of its current list.
Rule #2: You can only move a number to the rightmost end of a list if it is larger than the other numbers in that list.
A move is valid if it satisfies both Rule #1 and Rule #2.
A move is invalid if it violates either Rule #1 or Rule #2.

Goal: The goal is to evaluate the minimum number of valid moves required to reach the goal configuration from the current configuration. If any of the lists in the current configuration contains numbers not arranged in ascending order your answer should be "impossible". 

Here are two examples:

Example 1:

This is the current configuration:
A = [0, 1]
B = [2]
C = []
This is the goal configuration:
A = []
B = []
C = [0, 1, 2]

Here is the sequence of minimum number of valid moves required to reach the goal configuration from the current configuration:

Move 2 from B to C.
A = [0, 1]
B = []
C = [2]

Move 1 from A to B.
A = [0]
B = [1]
C = [2]

Move 2 from C to B.
A = [0]
B = [1, 2]
C = []

Move 0 from A to C.
A = []
B = [1, 2]
C = [0]

Move 2 from B to A.
A = [2]
B = [1]
C = [0]

Move 1 from B to C.
A = [2]
B = []
C = [0, 1]

Move 2 from A to C.
A = []
B = []
C = [0, 1, 2]

The minimum number of valid moves required to reach the goal configuration from the current configuration is 7.

Example 2:

This is the current configuration:
A = [1]
B = [0]
C = [2]
This is the goal configuration:
A = []
B = []
C = [0, 1, 2]

Here is the sequence of minimum number of valid moves required to reach the goal configuration from the current configuration:

Move 2 from C to A.
A = [1, 2]
B = [0]
C = []

Move 0 from B to C.
A = [1, 2]
B = []
C = [0]

Move 2 from A to B.
A = [1]
B = [2]
C = [0]

Move 1 from A to C.
A = []
B = [2]
C = [0, 1]

Move 2 from B to C.
A = []
B = []
C = [0, 1, 2]

The minimum number of valid moves required to reach the goal configuration from the current configuration is 5.

Here is the task:

This is the current configuration:
A = {a1}
B = {b1}
C = {c1}
This is the goal configuration:
A = []
B = []
C = [0, 1, 2]


'''

value_last_step_prompt = '''

Problem description:
- There are three lists labeled A, B, and C.
- There is a set of numbers distributed among those three lists.
- You can only move numbers from the rightmost end of one list to the rightmost end of another list.
Rule #1: You can only move a number if it is at the rightmost end of its current list.
Rule #2: You can only move a number to the rightmost end of a list if it is larger than the other numbers in that list.
A move is valid if it satisfies both Rule #1 and Rule #2.
A move is invalid if it violates either Rule #1 or Rule #2.

Goal: The goal is to give a judgement (sure/impossible) if the sequence of moves reach the goal configuration from the starting configuration without violating any of the rules.

Here are two examples:

Example 1:

This is the starting configuration:
A = [0, 1]
B = [2]
C = []
This is the goal configuration:
A = []
B = []
C = [0, 1, 2]

Here is the sequence of moves to reach the goal configuration from the starting configuration:

Move 2 from B to C.
A = [0, 1]
B = []
C = [2]

Move 1 from A to B.
A = [0]
B = [1]
C = [2]

Move 2 from C to B.
A = [0]
B = [1, 2]
C = []

Move 0 from A to C.
A = []
B = [1, 2]
C = [0]

Move 2 from B to A.
A = [2]
B = [1]
C = [0]

Move 1 from B to C.
A = [2]
B = []
C = [0, 1]

Move 2 from A to C.
A = []
B = []
C = [0, 1, 2]

Answer: sure

Example 2:

This is the starting configuration:
A = [2]
B = [0]
C = [1]
This is the goal configuration:
A = []
B = []
C = [0, 1, 2]

Here is the sequence of moves to reach the goal configuration from the starting configuration:


Move 1 from C to A.
A = [2, 1]
B = [0]
C = []

Move 0 from B to C.
A = [2, 1]
B = []
C = [0]

Move 1 from A to B.
A = [2]
B = [1]
C = [0]

Move 2 from A to C.
A = []
B = [1]
C = [0, 2]

Move 1 from B to C.
A = []
B = []
C = [0, 1, 2]

Answer: impossible

Here is the task:

This is the starting configuration:
A = {a1}
B = {b1}
C = {c1}
This is the goal configuration:
A = []
B = []
C = [0, 1, 2]


Here is the sequence of moves to reach the goal configuration from the starting configuration:

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


       


                first_index = 0
                for k in range(len(output) - 107):
                    if output[k:k+108] == 'The minimum number of valid moves required to reach the goal configuration from the current configuration is' or output[k:k+108] == 'the minimum number of valid moves required to reach the goal configuration from the current configuration is':
                        first_index = k
                            

                second_index = 0
                for t in range(first_index, len(output)):
                    if output[t] == '.' or output[t] == ',' :
                        second_index = t
                        break

                # if len(output[first_index:second_index].split(" ")[-1])<=2 and first_index!=0 and ")" not in output[first_index:second_index].split(" ")[-1] and "A" not in output[first_index:second_index].split(" ")[-1] and "B" not in output[first_index:second_index].split(" ")[-1] and "C" not in output[first_index:second_index].split(" ")[-1] :

                   
                try:

                
                  
                    v+=int(output[first_index:second_index].split(" ")[-1])
                except Exception as e:
                    err = f"Error: {str(e)}"
                    print(err)
                    print("random sampling>>>>>")

                    v+=np.random.randint(1,8)
        
        else:

            if "sure" in output:
                v+=0
            else:
                v+=100

           


            

   
   
    return v

def get_value( y, n_evaluate_sample):
    global input_tokens
    global output_tokens
    global response_time
    if [y[-1][0],y[-1][1],y[-1][2]] == [[],[],[0,1,2]]:
        y_len = len(y)
        move_seq = ""
        for i in range(1,y_len,2):
            move_seq+=y[i]+"."+"\n"
            a = "A = {}".format(str(y[i+1][0]))
            b = "B = {}".format(str(y[i+1][1]))
            c = "C = {}".format(str(y[i+1][2]))
            move_seq+=a+'\n'+b+'\n'+c+'\n\n'
        prompt = value_last_step_prompt.format(a1 = str(y[-y_len][0]) , b1=str(y[-y_len][1]) , c1= str(y[-y_len][2]), move_seq= move_seq)
        last_step_flag = True
    else:

        prompt = value_prompt.format(a1 = str(y[-1][0]), b1 = str(y[-1][1]), c1 = str(y[-1][2]) )
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

def get_values(ys, n_evaluate_sample):
    values = []

    for y in ys:  # each partial output
     

        value = get_value( y, n_evaluate_sample)
           
            
        values.append(value)
    return values

def extract_moves_configs(response):
    all_moves = []
    all_states = []
    for k in range(len(response) - 17):
        sub_str = response[k:k+18]
        if 'Move' in sub_str and '.' not in sub_str and 'from' in sub_str and 'to' in sub_str and (('A' in sub_str and 'B' in sub_str ) or ('C' in sub_str and 'B' in sub_str ) or ('A' in sub_str and 'C' in sub_str )) :


            if sub_str not in all_moves:

                all_moves.append(sub_str)
                states = []
                start_idx = 0
                end_idx = 0
                
                for l in range(k+18, len(response)):
                    if response[l]=="A":
                        start_idx = l
                        break
                c_flag = 0
                for l in range(start_idx, len(response)):
                    if response[l]=="C":
                        c_flag = 1
                    if c_flag==1 and response[l]=="]":
                        end_idx = l
                        break
                    
                splits = response[start_idx:end_idx+1].split("=")
                for sp in splits:

                    if '[' in sp and ']' in sp:

                        states.append(json.loads(sp[sp.index('['):sp.index(']')+1]))
                
                all_states.append(states)
    return all_moves, all_states
                

def get_proposals( y): 
    global input_tokens
    global output_tokens
    global response_time
    
    prompt = propose_prompt.format(a= str(y[-1][0]), b= str(y[-1][1]), c=str(y[-1][2]))
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

icl_examples = [ 3, 22]
for i in range(26):
    if (i+1) not in icl_examples:
        
        A=all_As[i] 

        B=all_Bs[i]

        C=all_Cs[i]
        ys = [[[A,B,C]]]
        potential_solutions = []
        input_tokens = [] 
        output_tokens = []
        response_time = [] 
        start_time = time.time()

        print("start state>>>",ys)
        for step in range(10):
            # generation
            print("step>>",step)
            new_ys = [get_proposals(y) for y in ys]
           


            new_ys = list(itertools.chain(*new_ys))
            print("after all proposals>>",new_ys)
            ids = list(range(len(new_ys)))
            # evaluation
           
          

            values = get_values(new_ys, 3)

            print("values of proposals>>>",values)

            # selection
           
           
            select_ids = sorted(ids, key=lambda x: values[x], reverse=False)[:5]
            print("select ids>>>",select_ids)
            select_new_ys = []
            for select_id in select_ids:
                if new_ys[select_id][-1] == [[],[],[0,1,2]]:
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
       
# if __name__ == '__main__':
   
#     solve()
