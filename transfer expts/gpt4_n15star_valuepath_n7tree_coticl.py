import openai
from copy import deepcopy
import time
import re
import json
import numpy as np
import os
import argparse

from openai import AzureOpenAI


reward_rooms = [(11,8),(8,11),(8,15),(15,8),(1,8),(8,1)]

def check_path(path):
	if not os.path.exists(path):
		os.mkdir(path)

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


for room1,room2 in reward_rooms:

	for start_room in range(1,16):
		if start_room!=room1 and start_room!=room2:
			num_input_tokens=0
			num_output_tokens=0


			prompt = """

			Problem description:
			You are exploring a zoo. You enter zone 1 and you see two passages one on the right and one on the left. You choose the passage on the right and enter zone 3. You see two passages in zone 3. You can choose the passage on the left or the passage on the right. You choose the passage on the right, and your enter zone 7 and there's a cage. You open it and find $50 but remember you're only exploring so you don't take any money. Then you go back to zone 3, and this time you go to the passage on the left to zone 6. You find another cage; you open it and there's $10 (but you don't take any money). You go back to zone 1. This time you choose the passage on the left and you go to zone 2. Again, you see two passages, one on the left and one on the right. You enter the passage on the right, and you find yourself in zone 5. There's a cage in zone 5. You open it and find $22. Then you go back to zone 2, and this time you go to the passage on the left, and you find yourself in zone 4. You find a cage; you open it and there's $56 (you still don't take any money). You go back to zone 1. Given you didn't take any money during exploration, assume you can pick one path to collect money. 
				
			 

			Goal: The goal is to find the shortest path from the starting zone to the zone with the highest money.

			Here are two examples:

			Example 1:

			This is the starting zone:
			zone 1

			The zone with the highest money is zone 4. To go to zone 4 from zone 1, first I need to take the passage on the left which leads to zone 2. From zone 2, I can directly go to zone 4.
			
			Hence, the shortest path from zone 1 to the zone with the highest money is: 1, 2, 4 
			



			Example 2:

			This is the starting zone:
			zone 3
			
			The zone with the highest money is zone 4. To go to zone 4 from zone 3, first I need to get back to zone 1. From zone 1, I can take the passage on the left which leads to zone 2. From zone 2, I can directly go to zone 4.
			
			Hence, the shortest path from zone 3 to the zone with the highest money is: 3, 1, 2, 4

			
			Here is the task:

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
			- There is a chest with a reward of 50 for visiting room {room1} and there is a chest with a reward of 10 for visiting room {room2}. 
			- You can collect the reward only once and only from one chest. 
			- If you enter a room with a chest, then you must collect the reward from that chest, and you cannot collect anymore rewards.

			Goal: The goal is to find the shortest path from the starting room to the room with a chest with the highest reward.

			
			This is the starting room:
			room {r}

			Starting from room {r}, use a step by step thinking to find the shortest path to the room with a chest with the highest reward. First list all the rooms directly connected to your current room, and then select the ones leading to the highest-reward chest, minimizing steps and bypassing rooms containing lower-value rewards.
			Please limit your shortest path answer to a maximum path length of 6.
			  

			

			"""

			input = [{
			    "role": "system",
			    "content": "you are an AI assistant",
			}]

			input.append({
			    "role": "user",
			    "content": prompt.format(room1=room1,room2=room2,r=start_room),
			})

			test_dir = './logs/'
			check_path(test_dir)
			output_dir = test_dir + args.output_dir + '/'
			check_path(output_dir)


			with open(output_dir+'problem{}_reward_rooms_{}_{}.log'.format(start_room,room1,room2), 'a') as w:
				w.write(prompt.format(room1=room1,room2=room2,r=start_room) +'\n')

			
			cur_try=0
			
			while cur_try <30:
				try:
					


					response= client.chat.completions.create(model=deployment_name, messages=input,temperature=0.0,top_p = 0,max_tokens=1000)
					

				

				
					break

						
				except Exception as e:
					
					err = f"Error: {str(e)}"

					

					print(err)
					
					time.sleep(120)
					cur_try+=1
					continue


				
			
			with open(output_dir+'problem{}_reward_rooms_{}_{}.log'.format(start_room,room1,room2), 'a') as w:
				w.write("GPT-4 Response for valuepath >>>>>>>\n"+response.choices[0].message.content)


			
			
		
			print("done solving problem with start room {}, reward room1 {}, and reward room2 {}".format(start_room,room1,room2))
					



