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



def check_path(path):
	if not os.path.exists(path):
		os.mkdir(path)


propose_prompt = '''
Problem description:
- Imagine a castle with 15 rooms. 
- Room 1 is connected to room 7, room 10, room 13, and room 11. 
- Room 2 is connected to room 5, room 8, room 11, and room 14. 
- Room 3 is connected to room 6, room 9, room 12, and room 8. 
- Room 4 is connected to room 7, room 10, room 13, and room 15. 
- Room 5 is connected to room 8, room 11, and room 14. 
- Room 6 is connected to room 9, room 12, and room 15. 
- Room 7 is connected to room 10, and room 13. 
- Room 8 is connected to room 14. 
- Room 9 is connected to room 12, and room 15. 
- Room 10 is connected to room 13. 
- Room 11 is connected to room 14. 
- Room 12 is connected to room 15. 
- There is a chest with a reward of 50 for visiting room 8 and there is a chest with a reward of 10 for visiting room 15. 
- You can collect the reward only once and only from one chest. 

Here are two examples:

Example 1:

This is the starting room:
room 1

All possible next rooms to go to from the starting room:

Possible step number 1:
Go from room 1 to room 11

Possible step number 2:
Go from room 1 to room 10

Possible step number 3:
Go from room 1 to room 13

Possible step number 4:
Go from room 1 to room 7


Example 2:

This is the starting room:
room 6

All possible next rooms to go to from the starting room:

Possible step number 1:
Go from room 6 to room 3

Possible step number 2:
Go from room 6 to room 9

Possible step number 3:
Go from room 6 to room 12

Possible step number 4:
Go from room 6 to room 15


Here is the task:

This is the starting room:
room {r}

All possible next rooms to go to from the starting room:

'''

value_prompt = '''

Problem description:
- Imagine a castle with 15 rooms. 
- Room 1 is connected to room 7, room 10, room 13, and room 11. 
- Room 2 is connected to room 5, room 8, room 11, and room 14. 
- Room 3 is connected to room 6, room 9, room 12, and room 8. 
- Room 4 is connected to room 7, room 10, room 13, and room 15. 
- Room 5 is connected to room 8, room 11, and room 14. 
- Room 6 is connected to room 9, room 12, and room 15. 
- Room 7 is connected to room 10, and room 13. 
- Room 8 is connected to room 14. 
- Room 9 is connected to room 12, and room 15. 
- Room 10 is connected to room 13. 
- Room 11 is connected to room 14. 
- Room 12 is connected to room 15. 
- There is a chest with a reward of 50 for visiting room 8 and there is a chest with a reward of 10 for visiting room 15. 
- You can collect the reward only once and only from one chest. 

Goal: The goal is to evaluate the minimum number of steps from the current room that yields the most reward.

Here are two examples:

Example 1:

This is the current room:
room 1 

Here is the sequence of steps from the current room that can help in yielding the most reward using as few steps as possible:

Go from room 1 to room 11.

Go from room 11 to room 5.

Go from room 5 to room 8.


The minimum number of steps required from the current room that yields the most reward is 3.

Example 2:

This is the current room:
room 6

Here is the sequence of steps from the current room that can help in yielding the most reward using as few steps as possible:

Go from room 6 to room 3.

Go from room 3 to room 8.


The minimum number of steps required from the current room that yields the most reward is 2.


Here is the task:

This is the current room:
room {r}


'''

value_last_step_prompt = '''

Problem description:
- Imagine a castle with 15 rooms. 
- Room 1 is connected to room 7, room 10, room 13, and room 11. 
- Room 2 is connected to room 5, room 8, room 11, and room 14. 
- Room 3 is connected to room 6, room 9, room 12, and room 8. 
- Room 4 is connected to room 7, room 10, room 13, and room 15. 
- Room 5 is connected to room 8, room 11, and room 14. 
- Room 6 is connected to room 9, room 12, and room 15. 
- Room 7 is connected to room 10, and room 13. 
- Room 8 is connected to room 14. 
- Room 9 is connected to room 12, and room 15. 
- Room 10 is connected to room 13. 
- Room 11 is connected to room 14. 
- Room 12 is connected to room 15. 
- There is a chest with a reward of 50 for visiting room 8 and there is a chest with a reward of 10 for visiting room 15. 
- You can collect the reward only once and only from one chest. 

Goal: The goal is to give a judgement (sure/impossible) if the sequence of steps from the starting room yield the most reward. Check if the steps eventually lead to the room which has a chest with the maximum reward, and for each of the steps the rooms are directly connected to each other.


Here are two examples:

Example 1:

This is the starting room:
room 1 

Here is the sequence of steps from the starting room that can help in yielding the most reward:

Go from room 1 to room 11.

Go from room 11 to room 5.

Go from room 5 to room 8.

Answer: sure


Example 2:

This is the starting room:
room 7

Here is the sequence of steps from the starting room that can help in yielding the most reward:

Go from room 7 to room 1.

Go from room 1 to room 2.

Go from room 2 to room 5.

Go from room 5 to room 8.

Answer: impossible


Here is the task:

This is the starting room:
room {r}

Here is the sequence of steps from the starting room that can help in yielding the most reward:

{step_seq}

Answer:


'''

def check_path(path):
	if not os.path.exists(path):
		os.mkdir(path)


def extract_moves_configs(response):

	all_moves = []

	possible_step_start_indices = []
	for k in range(len(response) - 19):
		sub_str = response[k:k+20]
		if 'Possible step number' in sub_str:
			possible_step_start_indices.append(k)

	
			
	for idx,ind in enumerate(possible_step_start_indices):
		if idx< len(possible_step_start_indices)-1:
			all_moves.append(response[ind:possible_step_start_indices[idx+1]].split(":")[-1].strip())
		else:
			all_moves.append(response[ind:len(response)].split(":")[-1].strip())

	return all_moves


def get_proposals(y): 
	
	
	prompt = propose_prompt.format(r= str(y[-1]))
	proposals,messages, inp_tokens, op_tokens, rp_time = gpt(prompt,empty_response=0, n=1, stop=None)
	# input_tokens.append(inp_tokens)
	# output_tokens.append(op_tokens)
	# response_time.append(rp_time)
	print("gpt proposals response>>", proposals[0])
	all_moves = extract_moves_configs(proposals[0])
		   
   
	prev_next_room=[]
	for move in all_moves:
		temp = deepcopy(y)
		temp.append(int(move.split(" ")[6]))
		
		prev_next_room.append(temp)


	return prev_next_room



def value_outputs_unwrap(value_outputs: list,last_step_flag) -> float:

	v = 0

	for output in value_outputs:
		if not last_step_flag:

			first_index = 0
			for k in range(len(output) - 29):
				if output[k:k+30] == 'that yields the most reward is':
					first_index = k
					

			second_index = 0
			for t in range(first_index, len(output)):
				if output[t] == '.' or output[t] == ',' :
					second_index = t
					break
			v+=int(output[first_index:second_index].split(" ")[-1])
		else:

			if "sure" in output:
				v+=0
			else:
				v+=100

	return v




def get_value( y, n_evaluate_sample,value_cache):
	
	if y[-1] == 8 or y[-1]==15:
		y_len = len(y)

		step_seq = ""
		for i in range(y_len-1):
			if i< y_len-2:
				step_seq+="Go from room {} to room {}.".format(str(y[i]),str(y[i+1]))+"\n\n"
			else:
				step_seq+="Go from room {} to room {}.".format(str(y[i]),str(y[i+1]))


		prompt = value_last_step_prompt.format(r=str(y[0]),step_seq=step_seq)
		
		last_step_flag = True
	else:

		prompt = value_prompt.format(r = str(y[-1]) )
		last_step_flag = False
	print("value_prompt>>>",prompt)
	if prompt in value_cache:
		return value_cache[prompt],value_cache

	
   
	value_outputs,_, inp_tokens, op_tokens, rp_time = gpt(prompt,empty_response = 0 , n=n_evaluate_sample, stop=None)

	# input_tokens.append(inp_tokens)
	# output_tokens.append(op_tokens)
	# response_time.append(rp_time)
	print("value_outputs>>>",value_outputs)
	value = value_outputs_unwrap(value_outputs,last_step_flag)
	print("value>>>",value)
	value_cache[prompt] = value
	return value, value_cache


def get_values(ys, n_evaluate_sample,value_cache):
	values = []

	for y in ys:  # each partial output
	 

		value,value_cache = get_value( y, n_evaluate_sample,value_cache)
		   
			
		values.append(value)
	return values,value_cache

global gpt
gpt = partial(gpt, temperature=0.7)
print(gpt)

parser = argparse.ArgumentParser()

parser.add_argument
parser.add_argument('--output_dir',type=str, help='directory name where output log files will be stored', required= True)
args = parser.parse_args()
print(args)

graph_info_lists = [(1,7), (1,10),(1,13),(1,11), 
(2,5), (2,8),(2,11),(2,14) ,
(3,6), (3,9),(3,12),(3,8), 
(4,7), (4,10),(4,13),(4,15), 
(5,8), (5,11),(5,14), 
(6,9), (6,12),(6,15), 
(7,10), (7,13),  
(8,14), (9,12), (9,15),
			  (10,13), (11,14),(12,15)]

A=np.zeros((15,15))

for node_tup in graph_info_lists:
	
		
			
	A[node_tup[0]-1,node_tup[1]-1] = 1
	A[node_tup[1]-1,node_tup[0]-1] = 1

for run_no in range(1,11):
	print("run number>>",run_no)

	value_cache = {}
	for start_room in range(1,16):
		if start_room!=8 and start_room!=15 and start_room!=1 and start_room!=6:
			print("length of value cache>>",len(value_cache))
			ys = [[start_room]]
			potential_solutions = []
			print("start room>>",start_room)
			for step in range(6):

				print("step>>",step)
				new_ys = [get_proposals(y) for y in ys]
			   


				new_ys = list(itertools.chain(*new_ys))
				print("after all proposals>>",new_ys)
				ids = list(range(len(new_ys)))
				# evaluation
			   
			  

				values,value_cache = get_values(new_ys, 3,value_cache)

				print("values of proposals>>>",values)

				# selection
			   
			   
				select_ids = sorted(ids, key=lambda x: values[x], reverse=False)[:5]
				print("select ids>>>",select_ids)
				select_new_ys = []
				for select_id in select_ids:
					if new_ys[select_id][-1] == 8 or new_ys[select_id][-1] == 15:
						print("reward room reached>>>")
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
			output_dir+='run{}/'.format(run_no)
			check_path(output_dir)
		   
			end_time = time.time()

			with open(output_dir+'problem{}.pkl'.format(start_room), 'wb') as f:
				pickle.dump(potential_solutions, f)

			# np.savez(output_dir+'problem{}_tokens_times.npz'.format(i+1),num_input_tokens = input_tokens, num_output_tokens = output_tokens,response_times  = response_time, total_time = [end_time - start_time])

			print("done solving problem {}".format(start_room))
		   




		





