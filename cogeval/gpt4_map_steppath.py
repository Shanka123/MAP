import openai
from copy import deepcopy
from steppath_fewshot_examples import standard_prompt
import time
import re
import json
import numpy as np
import os
import argparse
openai.api_type = "azure"
openai.api_base = "https://gcrgpt4aoai3.openai.azure.com/"
openai.api_version = "2023-03-15-preview" # can use the older api version openai.api_version = "2022-12-01"



def check_path(path):
	if not os.path.exists(path):
		os.mkdir(path)

parser = argparse.ArgumentParser()

parser.add_argument
parser.add_argument('--openai_api_key', type = str, help='openai key', required= True)
parser.add_argument('--output_dir',type=str, help='directory name where output log files will be stored', required= True)

args = parser.parse_args()
print(args)

openai.api_key = args.openai_api_key

def task_coordination_module(current_room,target_room):

	task_coordination_prompt = """Consider the following puzzle problem:

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

		Goal: The goal is to predict whether the current room matches the target room or not. 

		Here are two examples:

		Example 1:

		This is the current room:
		room 9

		This is the target room:
		room 4

		Answer:
		The current room doesn't match the target room. Hence no. 

		Example 2:

		This is the current room:
		room 9

		This is the target room:
		room 9

		Answer:
		The current room matches the target room. Hence yes.


		Here is the task:

		This is the current room:
		room {}

		This is the target room:
		room {}

		Answer:
		    
		    

		""".format(current_room,target_room)

	task_coordination_input = [{
	"role": "system",
	"content": "you are an AI assistant",
	}]

	task_coordination_input.append({
		"role": "user",
		"content": task_coordination_prompt,
	})

	cur_try=0
	while cur_try<5:

		try:

			task_coordination_response = openai.ChatCompletion.create(
				engine='gpt-4-32k',
				messages=task_coordination_input,temperature=0.0,top_p=0,
					max_tokens=500)

			global num_coordinator_calls
			global num_coordinator_input_tokens
			global num_coordinator_output_tokens

			num_coordinator_calls+=1
			num_coordinator_input_tokens+=task_coordination_response["usage"]["prompt_tokens"]
			num_coordinator_output_tokens+=task_coordination_response["usage"]["completion_tokens"]

			
			if 'yes' in task_coordination_response.choices[0].message.content or 'Yes' in task_coordination_response.choices[0].message.content:
				match_flag=1
			else:
				match_flag=0

			break

		except Exception as e:
			err = f"Error: {str(e)}"
			print(err)
			time.sleep(60)
			cur_try+=1
			continue

	return match_flag

def move_validator_module(source_room, target_room):

	move_validator_prompt = """
		Consider the following puzzle problem:

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

		Goal: The goal is to check whether the proposed step between the two rooms exists or not, and based on that if it is a valid or invalid step.

		Here are two examples:

		Example 1:

		Proposed step: 
		Go from room 1 to room 11. 

		Answer:
		First check the rooms, room 1 is connected to. Room 1 is connected to room 7, room 10, room 13, and room 11.
		Next check the rooms, room 11 is connected to. Room 11 is connected to room 1, room 2, room 5, and room 14.
		Since room 1 and room 11 are connected to each other, the proposed step exists and is valid.

		Example 2:

		Proposed step: 
		Go from room 4 to room 5.

		Answer:
		First check the rooms, room 4 is connected to. Room 4 is connected to room 7, room 10, room 13, and room 15.
		Next check the rooms, room 5 is connected to. Room 5 is connected to room 8, room 11, room 14, and room 2.
		Since room 4 and room 5 aren't connected to each other, the proposed step doesn't exist and is invalid.

		Here is the task:

		Proposed step:
		Go from room {} to room {}.

		Answer:


		""".format(source_room,target_room)


	move_validator_input = [{
    "role": "system",
    "content": "you are an AI assistant",
	}]

	move_validator_input.append({
	    "role": "user",
	    "content": move_validator_prompt,
	})

	cur_try=0
	while cur_try<5:

		try:

			validator_response = openai.ChatCompletion.create(
			    engine='gpt-4-32k',
			    messages=move_validator_input,temperature=0.0,top_p=0,
			        max_tokens=500)

			global num_validator_calls
			global num_validator_input_tokens
			global num_validator_output_tokens
			num_validator_calls+=1
			num_validator_input_tokens+=validator_response["usage"]["prompt_tokens"]
			num_validator_output_tokens+=validator_response["usage"]["completion_tokens"]
			print("validator response>>>", validator_response)
			char_list_response = validator_response.choices[0].message.content.split('\n')[-1].replace(".","").split(" ")
			if 'invalid' in char_list_response:
				move_validity = 'no'
			else:
				move_validity = 'yes'

			print("move_validity>>",move_validity)

			break

		except Exception as e:
			err = f"Error: {str(e)}"
			print(err)
			time.sleep(60)
			cur_try+=1
			continue
	return move_validity,validator_response


def actor_module_propose_action(actor_input,current_room,goal_room):

	num_tries=0
	while num_tries<10:

		cur_try=0
		check_flag =0
		while cur_try <10:
			try:
				if check_flag==1:
					actor_response = openai.ChatCompletion.create(
				    engine='gpt-4-32k',
				    messages=actor_input,temperature=0.1*cur_try,
				        max_tokens=200)
				else:



					actor_response = openai.ChatCompletion.create(
				    engine='gpt-4-32k',
				    messages=actor_input,temperature=0.0,top_p=0,
				        max_tokens=200)

				
				global num_actor_calls
				global num_actor_input_tokens
				global num_actor_output_tokens
				num_actor_calls+=1
				num_actor_input_tokens+=actor_response["usage"]["prompt_tokens"]
				num_actor_output_tokens+=actor_response["usage"]["completion_tokens"]

				print("GPT-4 full response>>>",actor_response.choices[0].message.content)
				actor_truncated_response = None

				for k in range(len(actor_response.choices[0].message.content) - 11):
				    sub_str = actor_response.choices[0].message.content[k:k+12]
				    if 'Go from room' in sub_str:
				        break

				for t in range(k, len(actor_response.choices[0].message.content)):
				    if actor_response.choices[0].message.content[t] == '.':
				        break
				actor_truncated_response = actor_response.choices[0].message.content[k:t]


				

				if 'Go from room' in actor_truncated_response and 'to room' in actor_truncated_response and len(actor_truncated_response.split(" ")) ==7:
					break
				else:
					cur_try+=1
					check_flag=1
					continue

			except Exception as e:
				
				err = f"Error: {str(e)}"

				

				print(err)
				
				time.sleep(60)
				cur_try+=1
				continue

		print("GPT-4 truncated response>>",actor_truncated_response)
		source_room = int(actor_truncated_response.split(" ")[3])
		target_room = int(actor_truncated_response.split(" ")[6])
		
		move_validity, move_validator_response = move_validator_module(source_room,target_room)

		if move_validity == "yes":
			break
		else:

			actor_input.append({
				"role": "assistant",
				"content": actor_response.choices[0].message.content,
			})

			internal_configuration_msg = """
			{}

			This is the current room:
			room {}
				
			This is the target room:
			room {}
			
			Please try again to give me the next room to go to from the current room that can help in reaching the target room using as few steps as possible. Please format your answer as:
			Go from room <N> to room <N>.

			""".format(move_validator_response,current_room,goal_room)


			actor_input.append({
			"role": "user",
			"content": internal_configuration_msg,
		})
			
			num_tries+=1



	return actor_truncated_response



	


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


step2_paths = [(9,4),(6,4),(12,4),(3,2),(8,11),(2,1),(11,10),(1,4),(13,15),(7,15)] 
step3_paths = [(9,13),(6,13),(12,13),(3,11),(8,1),(14,10),(2,10),(5,10),(5,13),(14,13)]
step4_paths = [(9,1),(9,11),(12,1),(6,1),(6,11),(12,11),(3,13),(8,13),(2,4),(3,7)]
icl_examples = [(9,4),(2,10),(7,3)]
all_step_paths = step2_paths + step3_paths + step4_paths


num_validator_calls = 0 
	 
num_coordinator_calls = 0 
num_actor_calls = 0
num_validator_input_tokens = 0
num_validator_output_tokens = 0
	
num_coordinator_input_tokens = 0
num_coordinator_output_tokens = 0
num_actor_input_tokens = 0
num_actor_output_tokens = 0

for start_target_tup in all_step_paths:
	if start_target_tup in step2_paths:
		optimal_num_steps = 2
		optimal_reward = 8
	elif start_target_tup in step3_paths:
		optimal_num_steps = 3
		optimal_reward = 7
	else:

		optimal_num_steps = 4
		optimal_reward = 6

	for count in range(2):
		if count==0:
			start_room = start_target_tup[0]
			final_target_room = start_target_tup[1]
		else:
			start_room = start_target_tup[1]
			final_target_room = start_target_tup[0]


		if (start_room,final_target_room) not in icl_examples:

			rooms_visited = []
			rooms_visited.append(start_room)


			prompt = """
			Consider the following puzzle problem:
			
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
			 

			Goal: The goal is to find the shortest path from the starting room to the target room.

			Here are three examples:
			{}

			Here is the task:

			This is the starting room:
			room {}

			This is the target room:
			room {}

			Give me the next room to go to from the starting room that can help in reaching the target room using as few steps as possible. Please format your answer as:
			Go from room <N> to room <N>.

			""".format(standard_prompt,start_room,final_target_room)


			input = [{
			    "role": "system",
			    "content": "you are an AI assistant",
			}]

			input.append({
			    "role": "user",
			    "content": prompt,
			})

			current_room = start_room
			
			flag=0
			total_reward = 0
			for step in range(6):
				


				truncated_response = actor_module_propose_action(input,current_room,final_target_room)
				source_room = int(truncated_response.split(" ")[3])
				target_room = int(truncated_response.split(" ")[6])

				rooms_visited.append(target_room)
				current_room = target_room

				

				configuration_msg = """This is the current room:
					room {}

					This is the target room:
					room {}

				
					Give me the next room to go to from the current room that can help in reaching the target room using as few steps as possible. Please format your answer as:
					Go from room <N> to room <N>.

					""".format(current_room,final_target_room)

				prompt+="\n"+truncated_response+"."+"\n"+configuration_msg

			

				input = [{
						"role": "system",
						"content": "you are an AI assistant",
					}]

				input.append({
					"role": "user",
					"content": prompt,
					})
				if task_coordination_module(current_room,final_target_room):
					flag=1
					test_dir = './logs/'
					check_path(test_dir)
					output_dir = test_dir + args.output_dir + '/'
					check_path(output_dir)
					
					with open(output_dir+'problem{}_{}_optimal_steps_{}_reward_{}.log'.format(start_room,final_target_room,optimal_num_steps,optimal_reward), 'a') as w:
						w.write(prompt +'\n'+"List of rooms visited = {}".format(rooms_visited))


					
					break

			if flag==0:
				test_dir = './logs/'
				check_path(test_dir)
				output_dir = test_dir + args.output_dir + '/'
				check_path(output_dir)
				with open(output_dir+'problem{}_{}_optimal_steps_{}_reward_{}.log'.format(start_room,final_target_room,optimal_num_steps,optimal_reward), 'a') as w:
					w.write(prompt +'\n'+"List of rooms visited = {}".format(rooms_visited))


			print("number of validator calls till now>>",num_validator_calls)
		
			print("number of actor calls till now>>",num_actor_calls)
			print("number of coordinator calls till now>>",num_coordinator_calls)
			

			print("number of validator input and output tokens till now>>",num_validator_input_tokens,num_validator_output_tokens)
		
			print("number of actor input and output tokens till now>>",num_actor_input_tokens,num_actor_output_tokens)
			print("number of coordinator input and output tokens till now>>",num_coordinator_input_tokens,num_coordinator_output_tokens)
		
				
			print("done solving problem {} to {}".format(start_room,final_target_room))
					





