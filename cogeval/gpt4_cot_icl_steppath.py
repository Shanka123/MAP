import openai
from copy import deepcopy
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

			Example 1:

			This is the starting room:
			room 9

			This is the target room:
			room 4

			Room 9 isn't connected to room 4. But room 9 is connected to room 15 which is directly connected to room 4.
			Hence, the shortest path from room 9 to room 4: 9, 15, 4


			Example 2:

			This is the starting room:
			room 2

			This is the target room:
			room 10

			Room 2 isn't connected to room 10. But room 2 is connected to room 11, and room 10 is connected to room 1. Room 11 is connected to room 1.
			Hence, the shortest path from room 2 to room 10: 2, 11, 1, 10


			Example 3:

			This is the starting room:
			room 7

			This is the target room:
			room 3

			Room 7 isn't connected to room 3. Room 7 is connected to room 4, and room 3 is connected to room 6. Room 4 and room 6 aren't connected but both are connected to room 15.
			Hence, the shortest path from room 7 to room 3: 7, 4, 15, 6, 3



			Here is the task:

			This is the starting room:
			room {}

			This is the target room:
			room {}

			Starting from room {}, use a step by step thinking to find the shortest path from room {} to room {}. Please limit your shortest path answer to a maximum path length of 6.
		 

			 
			

			""".format(start_room,final_target_room, start_room, start_room,final_target_room)

			input = [{
			    "role": "system",
			    "content": "you are an AI assistant",
			}]

			input.append({
			    "role": "user",
			    "content": prompt,
			})

			
			test_dir = './logs/'
			check_path(test_dir)
			output_dir = test_dir + args.output_dir + '/'
			check_path(output_dir)

			with open(output_dir+'problem{}_{}_optimal_steps_{}_reward_{}.log'.format(start_room,final_target_room,optimal_num_steps,optimal_reward), 'a') as w:
				w.write(prompt +'\n')

			
			cur_try=0
			
			while cur_try <10:
				try:
					



					response = openai.ChatCompletion.create(
				    engine='gpt-4-32k',
				    messages=input,temperature=0.0,top_p=0,
				        max_tokens=1000)

					num_input_tokens= response["usage"]["prompt_tokens"]
					num_output_tokens= response["usage"]["completion_tokens"]
					break

						
				except Exception as e:
					
					err = f"Error: {str(e)}"

					

					print(err)
					
					time.sleep(60)
					cur_try+=1
					continue


				
			
			with open(output_dir+'problem{}_{}_optimal_steps_{}_reward_{}.log'.format(start_room,final_target_room,optimal_num_steps,optimal_reward), 'a') as w:
				w.write("GPT-4 Response>>>>>>>\n"+response.choices[0].message.content)


			with open(output_dir+'problem{}_{}_optimal_steps_{}_reward_{}.log'.format(start_room,final_target_room,optimal_num_steps,optimal_reward), 'a') as w:
				w.write("\n\n Number of input tokens = {} \n Number of output tokens = {}".format(num_input_tokens,num_output_tokens))
		
		
			print("done solving problem {} to {}".format(start_room,final_target_room))
					

					


							
						

						


				
			

			

			
					
					



