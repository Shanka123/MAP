import openai
from copy import deepcopy
import time
import argparse
import os
import re
import json
import numpy as np
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

agents = 2
rounds = 3

def generate_answer(answer_context):
    try:
        completion = openai.ChatCompletion.create(
                engine='gpt-4-32k',
                messages=answer_context,
                    max_tokens=1000, n=1)
       
    except:
        print("retrying due to an error......")
        time.sleep(60)
        return generate_answer(answer_context)

    return completion

def construct_assistant_message(completion):
    content = completion["choices"][0]["message"]["content"]
    return {"role": "assistant", "content": content}


def construct_message(agents, idx,start_room,final_target_room):

    
    prefix_string = "These are the recent/updated opinions from other agents: "

    for agent in agents:
        agent_response = agent[idx]["content"]
        response = "\n\n One agent response: ```{}```".format(agent_response)

        prefix_string = prefix_string + response

    query_string = """\n\n Use these opinions carefully as additional advice, can you provide an updated answer?
    This is the starting room:
	room {}

	This is the target room:
	room {}

	Starting from room {}, please list the room numbers in order, including {}, separated by commas. Please limit your answer to a maximum path length of 6.
		 
	Your answer should only be in the format as below:
	The shortest path from room {} to room {}: {}, 


    """.format(start_room, final_target_room, start_room, start_room, start_room,final_target_room,start_room)  
    prefix_string = prefix_string + query_string
    return {"role": "user", "content": prefix_string}


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

			The shortest path from room 9 to room 4: 9, 15, 4

			Example 2:

			This is the starting room:
			room 2

			This is the target room:
			room 10

			The shortest path from room 2 to room 10: 2, 11, 1, 10

			Example 3:

			This is the starting room:
			room 7

			This is the target room:
			room 3

			The shortest path from room 7 to room 3: 7, 4, 15, 6, 3

			Here is the task:

			This is the starting room:
			room {}

			This is the target room:
			room {}

			Starting from room {}, please list the room numbers in order, including {}, separated by commas. Please limit your answer to a maximum path length of 6.
			 
			Your answer should only be in the format as below:
			The shortest path from room {} to room {}: {}, 

			""".format(start_room,final_target_room, start_room, start_room,start_room,final_target_room,start_room)

			test_dir = './logs/'
			check_path(test_dir)
			output_dir = test_dir + args.output_dir + '/'
			check_path(output_dir)

			with open(output_dir+'problem{}_{}_optimal_steps_{}_reward_{}.log'.format(start_room,final_target_room,optimal_num_steps,optimal_reward), 'a') as w:
				w.write(prompt +'\n')

			
			agent_contexts = [[{"role": "user", "content":prompt}] for agent in range(agents)]



			for round in range(rounds):
			    for agent_i, agent_context in enumerate(agent_contexts):
			       
			        
			        if round != 0:
			            agent_contexts_other = agent_contexts[:agent_i] + agent_contexts[agent_i+1:]
			            message = construct_message(agent_contexts_other, 2*round - 1, start_room,final_target_room)
			            agent_context.append(message)

			            print("message: ", message)

			        completion = generate_answer(agent_context)

			        assistant_message = construct_assistant_message(completion)
			        agent_context.append(assistant_message)
			        
			        print("Round {}, agent number {}, response {}".format(round+1, agent_i+1,completion))


			with open(output_dir+'problem{}_{}_optimal_steps_{}_reward_{}.log'.format(start_room,final_target_room,optimal_num_steps,optimal_reward), 'a') as w:
				w.write("\nGPT-4 Agent1 Response>>>>>>>\n"+agent_contexts[0][-1]["content"])

			with open(output_dir+'problem{}_{}_optimal_steps_{}_reward_{}.log'.format(start_room,final_target_room,optimal_num_steps,optimal_reward), 'a') as w:
				w.write("\nGPT-4 Agent2 Response>>>>>>>\n"+agent_contexts[1][-1]["content"])
			

			
			print("done solving problem {} to {}".format(start_room,final_target_room))
			