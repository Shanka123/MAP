import openai
from copy import deepcopy
from valuepath_fewshot_examples import standard_prompt
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

def move_validator_module(source_room, target_room,detour_flag):
	if detour_flag==0:


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

	else:

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

			The door from room 1 to room 11 is locked and now room 13 is connected to room 11.


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
			time.sleep(120)
			cur_try+=1
			continue
	return move_validity,validator_response


def task_coordination_module(current_room,detour_flag):

	

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
		- There is a chest with a reward of 50 for visiting room 8 and there is a chest with a reward of 10 for visiting room 15. 
		- You can collect the reward only once and only from one chest. 

		Goal: The goal is to predict whether there is a chest with a reward in the current room or not. 

		Here are two examples:

		Example 1:

		This is the current room:
		room 1

		Answer:
		There is a chest with a reward of 50 for visiting room 8 and there is a chest with a reward of 10 for visiting room 15. I am currently in room 1 where there is no chest with a reward. Hence no. 

		Example 2:

		This is the current room:
		room 8

		Answer:
		There is a chest with a reward of 50 for visiting room 8 and there is a chest with a reward of 10 for visiting room 15. I am currently in room 8 where there is a chest with a reward. Hence yes. 

		Here is the task:

		This is the current room:
		room {}

		Answer:
		    
		    

		""".format(current_room)

	
			
			


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

			
			if 'yes' in task_coordination_response.choices[0].message.content or 'Yes' in task_coordination_response.choices[0].message.content:
				match_flag=1
			else:
				match_flag=0

			break

		except Exception as e:
			err = f"Error: {str(e)}"
			print(err)
			time.sleep(120)
			cur_try+=1
			continue

	return match_flag



		    

def state_evaluator_module(current_room,detour_flag):

	if detour_flag==0:

		state_evaluator_prompt = """
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
			- There is a chest with a reward of 50 for visiting room 8 and there is a chest with a reward of 10 for visiting room 15. 
			- You can collect the reward only once and only from one chest. 
			
			Goal: The goal is to predict the minimum number of steps from the current room that yields the most reward. 

			Here are two examples:

			Example 1:

			This is the current room:
			room 1 
		
			Answer:
			The minimum number of steps required from the current room that yields the most reward is 3.

			Example 2:

			This is the current room:
			room 6

			Answer:
			The minimum number of steps required from the current room that yields the most reward is 2.

			
			Here is the task:

			This is the current room:
			room {}

			Answer:


			""".format(current_room)

	else:
		state_evaluator_prompt = """
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
			- There is a chest with a reward of 50 for visiting room 8 and there is a chest with a reward of 10 for visiting room 15. 
			- You can collect the reward only once and only from one chest. 
			
			Goal: The goal is to predict the minimum number of steps from the current room that yields the most reward. 

			Here are two examples:

			Example 1:

			This is the current room:
			room 1 
		
			Answer:
			The minimum number of steps required from the current room that yields the most reward is 3.

			Example 2:

			This is the current room:
			room 6

			Answer:
			The minimum number of steps required from the current room that yields the most reward is 2.

			
			The door from room 1 to room 11 is locked and now room 13 is connected to room 11. You can collect the reward only once and only from one chest.


			Here is the task:

			This is the current room:
			room {}

			Answer:


			""".format(current_room)



	state_evaluator_input = [{
	"role": "system",
	"content": "you are an AI assistant",
	}]

	state_evaluator_input.append({
		"role": "user",
		"content": state_evaluator_prompt,
	})

	cur_try=0
	while cur_try<5:

		try:

			evaluator_response = openai.ChatCompletion.create(
				engine='gpt-4-32k',
				messages=state_evaluator_input,temperature=0.0,top_p=0,
					max_tokens=500)

			
		

			break

		except Exception as e:
			err = f"Error: {str(e)}"
			print(err)
			time.sleep(120)
			cur_try+=1
			continue
	print("evaluator_response>>",evaluator_response)
	first_index = 0
	for k in range(len(evaluator_response.choices[0].message.content) - 29):
		if evaluator_response.choices[0].message.content[k:k+30] == 'that yields the most reward is':
			first_index = k
			

	second_index = 0
	for t in range(first_index, len(evaluator_response.choices[0].message.content)):
		if evaluator_response.choices[0].message.content[t] == '.' or evaluator_response.choices[0].message.content[t] == ',' :
			second_index = t
			break
	return int(evaluator_response.choices[0].message.content[first_index:second_index].split(" ")[-1])



		

# def state_evaluator_module(current_room):

# 	state_evaluator_prompt = """
# 		Consider the following puzzle problem:

# 		Problem description:
# 		- Imagine a castle with 15 rooms. 
# 		- Room 1 is connected to room 7, room 10, room 13, and room 11. 
# 		- Room 2 is connected to room 5, room 8, room 11, and room 14. 
# 		- Room 3 is connected to room 6, room 9, room 12, and room 8. 
# 		- Room 4 is connected to room 7, room 10, room 13, and room 15. 
# 		- Room 5 is connected to room 8, room 11, and room 14. 
# 		- Room 6 is connected to room 9, room 12, and room 15. 
# 		- Room 7 is connected to room 10, and room 13. 
# 		- Room 8 is connected to room 14. 
# 		- Room 9 is connected to room 12, and room 15. 
# 		- Room 10 is connected to room 13. 
# 		- Room 11 is connected to room 14. 
# 		- Room 12 is connected to room 15. 
# 		- There is a chest with a reward of 50 for visiting room 8 and there is a chest with a reward of 10 for visiting room 15. 
# 		- You can collect the reward only once and only from one chest. 
		
# 		Goal: The goal is to predict the minimum number of steps from the current room that yields the most reward. 

# 		Here are two examples:

# 		Example 1:

# 		This is the current room:
# 		room 1 
	
# 		Answer:
# 		The minimum number of steps required from the current room that yields the most reward is 3.

# 		Example 2:

# 		This is the current room:
# 		room 6

# 		Answer:
# 		The minimum number of steps required from the current room that yields the most reward is 2.

# 		What heuristic function can be used to estimate the minimum number of steps that yields the most reward from a given current room? 
# 		"""


# 	state_evaluator_input = [{
# 	"role": "system",
# 	"content": "you are an AI assistant",
# 	}]

# 	state_evaluator_input.append({
# 		"role": "user",
# 		"content": state_evaluator_prompt,
# 	})

# 	state_evaluator_input.append({
#     "role": "assistant",
#     "content": """A heuristic function that can be used to estimate the minimum number of steps that yields the most reward from a given current room is the "Manhattan Distance" heuristic. This heuristic calculates the sum of the absolute differences between the current room and the target rooms (rooms with rewards) along the available connections.

# 		In this problem, the target rooms are room 8 (with a reward of 50) and room 15 (with a reward of 10). The heuristic function can be defined as:

# 		h(n) = min(abs(current_room - target_room_1), abs(current_room - target_room_2))

# 		where n is the current room, target_room_1 is room 8, and target_room_2 is room 15.

# 		For example, if the current room is room 1, the heuristic function would be:

# 		h(1) = min(abs(1 - 8), abs(1 - 15))
# 		h(1) = min(7, 14)

# 		The minimum value is 7, which means that the heuristic function estimates that the minimum number of steps required to reach the room with the most reward is 7. However, this is just an estimate, and the actual minimum number of steps might be different. In this case, the actual minimum number of steps is 3, as mentioned in the example.
# 		""",
# 			    })

# 	internal_configuration_msg = """
# 	This is the current room:
# 	room {}

# 	Use the heuristic function to predict the minimum number of steps from the current room that yields the most reward.

# 	Please provide your answer according to the heuristic function in the format as below:
# 	The minimum number of steps required from the current room that yields the most reward is <N>.

# 	""".format(current_room)
		

		
# 	state_evaluator_input.append({
# 	    "role": "user",
# 	    "content": internal_configuration_msg,
# 	    })


# 	cur_try=0
# 	while cur_try<10:

# 		try:

# 			evaluator_response = openai.ChatCompletion.create(
# 			    engine='gpt-4-32k',
# 			    messages=state_evaluator_input,temperature=0.0,top_p=0,
# 			        max_tokens=2000)

	
			
# 			break

# 		except Exception as e:
# 			err = f"Error: {str(e)}"
# 			print(err)
# 			time.sleep(120)
# 			cur_try+=1
# 			continue


	
	

# 	print("evaluator_response>>",evaluator_response)
# 	first_index = 0
# 	for k in range(len(evaluator_response.choices[0].message.content) - 29):
# 		if evaluator_response.choices[0].message.content[k:k+30] == 'that yields the most reward is' or evaluator_response.choices[0].message.content[k:k+30] == 'that yields the most reward is':
# 			first_index = k
			

# 	second_index = 0
# 	for t in range(first_index, len(evaluator_response.choices[0].message.content)):
# 		if evaluator_response.choices[0].message.content[t] == '.' or evaluator_response.choices[0].message.content[t] == ',' :
# 			second_index = t
# 			break
	
# 	if len(evaluator_response.choices[0].message.content[first_index:second_index].split(" ")[-1])<=2 and first_index!=0:

# 		return int(evaluator_response.choices[0].message.content[first_index:second_index].split(" ")[-1])
# 	else:
# 		return np.random.randint(1,7)






def actor_module_propose_two_actions(actor_input,current_room,detour_flag):

	num_tries=0
	extracted_valid_moves = []
	previous_actor_truncated_response = None
	while num_tries<10:

		cur_try=0
		check_flag =0
		one_response_flag = 0
		while cur_try <10:
			try:
				if check_flag==1 or one_response_flag==1:
					actor_response = openai.ChatCompletion.create(
					engine='gpt-4-32k',
					messages=actor_input,temperature=0.1*cur_try,
						max_tokens=200)
				else:



					actor_response = openai.ChatCompletion.create(
					engine='gpt-4-32k',
					messages=actor_input,temperature=0.0,top_p=0,
						max_tokens=200)

				print("GPT-4 full response>>>",actor_response.choices[0].message.content)
				actor_truncated_response = []

				for k in range(len(actor_response.choices[0].message.content) - 11):
					sub_str = actor_response.choices[0].message.content[k:k+12]
					if 'Go from room' in sub_str:
					   

						for t in range(k, len(actor_response.choices[0].message.content)):
							if actor_response.choices[0].message.content[t] == '.':
								
								if actor_response.choices[0].message.content[k:t] not in actor_truncated_response and '<N>' not in actor_response.choices[0].message.content[k:t] and 'Go from room' in actor_response.choices[0].message.content[k:t] and 'to room' in actor_response.choices[0].message.content[k:t] and len(actor_response.choices[0].message.content[k:t].split(" ")) ==7:
									if int(actor_response.choices[0].message.content[k:t].split(" ")[3])==current_room:


										actor_truncated_response.append(actor_response.choices[0].message.content[k:t])
									else:
										print("move from next room provided")
										print("current room>>",current_room)

									# actor_truncated_response.append(actor_response.choices[0].message.content[k:t])
									break


				

				print("GPT-4 extracted moves>>>",actor_truncated_response)
				if len(actor_truncated_response)>=2:
					previous_actor_truncated_response = actor_truncated_response

					break

				elif len(actor_truncated_response)==1:
					previous_actor_truncated_response = actor_truncated_response

					

					one_move_msg = """
					You provided just one next room to go to from the current room. However it is possible to provide two different next rooms to go to from the current room.
			
					This is the current room:
					room {}



					Please try again to give me only two different next rooms to go to from the current room that can help in yielding the most reward using as few steps as possible. Please format your answer as:
					Go from room <N> to room <N>.


					""".format(current_room)
					# else:
					# 	one_move_msg = """
					# 	You provided just one next room to go to from the current room. However it is possible to provide two different next rooms to go to from the current room.
				
					# 	This is the current room:
					# 	room {}



					# 	Please try again to give me only two different next rooms to go to from the current room that can help in yielding the most reward based on the new reward design using as few steps as possible. Please format your answer as:
					# 	Go from room <N> to room <N>.


					# 	""".format(current_room)
							
					actor_input.append({
							"role": "assistant",
							"content": actor_response.choices[0].message.content,
						})
						
					actor_input.append({
						"role": "user",
						"content": one_move_msg,
						})

					one_response_flag=1
					cur_try+=1
					continue

				else:
					cur_try+=1
					check_flag=1
					continue

			except Exception as e:
				
				err = f"Error: {str(e)}"

				

				print(err)
				
				time.sleep(120)
				cur_try+=1
				continue

		
		if len(actor_truncated_response)==0:
			actor_truncated_response = previous_actor_truncated_response



		if len(actor_truncated_response)==2:
			# proposals.append(actor_truncated_response[0])
			# proposals.append(actor_truncated_response[1])


			move_validity1, validity1_response = move_validator_module(int(actor_truncated_response[0].split(" ")[3]), int(actor_truncated_response[0].split(" ")[6]),detour_flag)
			move_validity2, validity2_response = move_validator_module(int(actor_truncated_response[1].split(" ")[3]), int(actor_truncated_response[1].split(" ")[6]),detour_flag)
				
			if move_validity1 =='yes' and move_validity2 =='yes':
				# break
				if actor_truncated_response[0] not in extracted_valid_moves:

					extracted_valid_moves.append(actor_truncated_response[0])

				if len(extracted_valid_moves)==2:
					
					break

				if actor_truncated_response[1] not in extracted_valid_moves:

					extracted_valid_moves.append(actor_truncated_response[1])

				if len(extracted_valid_moves)==2:
					
					break
				
				
			elif move_validity1 =='yes' and move_validity2 =='no':
				if actor_truncated_response[0] not in extracted_valid_moves:

					extracted_valid_moves.append(actor_truncated_response[0])
				
				# if reval_flag==0:

				internal_configuration_msg = """
				{}

				This is the current room:
				room {}
					
				
				Please try again to give me only two different next rooms to go to from the current room that can help in yielding the most reward using as few steps as possible. Please format your answer as:
				Go from room <N> to room <N>.

				""".format(validity2_response,current_room)
				# else:
				# 	internal_configuration_msg = """
				# 	{}

				# 	This is the current room:
				# 	room {}
						
					
				# 	Please try again to give me only two different next rooms to go to from the current room that can help in yielding the most reward based on the new reward design using as few steps as possible. Please format your answer as:
				# 	Go from room <N> to room <N>.

				# 	""".format(validity2_response,current_room)


				num_tries+=1

			elif move_validity1 =='no' and move_validity2 =='yes':
				if actor_truncated_response[1] not in extracted_valid_moves:

					extracted_valid_moves.append(actor_truncated_response[1])
				
				
				# if reval_flag==0:

				internal_configuration_msg = """
				{}

				This is the current room:
				room {}
					
				
				Please try again to give me only two different next rooms to go to from the current room that can help in yielding the most reward using as few steps as possible. Please format your answer as:
				Go from room <N> to room <N>.

				""".format(validity1_response,current_room)
				# else:
				# 	internal_configuration_msg = """
				# 	{}

				# 	This is the current room:
				# 	room {}
						
					
				# 	Please try again to give me only two different next rooms to go to from the current room that can help in yielding the most reward based on the new reward design using as few steps as possible. Please format your answer as:
				# 	Go from room <N> to room <N>.

				# 	""".format(validity1_response,current_room)


				num_tries+=1
			else:
				# if reval_flag==0:

				internal_configuration_msg = """
				{}

				{}

				This is the current room:
				room {}
					
				
				Please try again to give me only two different next rooms to go to from the current room that can help in yielding the most reward using as few steps as possible. Please format your answer as:
				Go from room <N> to room <N>.

				""".format(validity1_response,validity2_response,current_room)
				# else:
				# 	internal_configuration_msg = """
				# 	{}

				# 	{}

				# 	This is the current room:
				# 	room {}
						
					
				# 	Please try again to give me only two different next rooms to go to from the current room that can help in yielding the most reward based on the new reward design using as few steps as possible. Please format your answer as:
				# 	Go from room <N> to room <N>.

				# 	""".format(validity1_response,validity2_response,current_room)



				num_tries+=1
		else:
			# proposals.append(actor_truncated_response[0])
			# proposals.append(actor_truncated_response[0])

			move_validity1, validity1_response = move_validator_module(int(actor_truncated_response[0].split(" ")[3]), int(actor_truncated_response[0].split(" ")[6]),detour_flag)
			if move_validity1 =='yes':
				# break
				if actor_truncated_response[0] not in extracted_valid_moves:

					extracted_valid_moves.append(actor_truncated_response[0])

				break
				
				
			else:
				# if reval_flag==0:


				internal_configuration_msg = """
				{}


				This is the current room:
				room {}
					
				
				Please try again to give me only two different next rooms to go to from the current room that can help in yielding the most reward using as few steps as possible. Please format your answer as:
				Go from room <N> to room <N>.

				""".format(validity1_response,current_room)
				# else:
				# 	internal_configuration_msg = """
				# 	{}


				# 	This is the current room:
				# 	room {}
						
					
				# 	Please try again to give me only two different next rooms to go to from the current room that can help in yielding the most reward based on the new reward design using as few steps as possible. Please format your answer as:
				# 	Go from room <N> to room <N>.

				# 	""".format(validity1_response,current_room)


				
				num_tries+=1
				




		actor_input.append({
		"role": "assistant",
		"content": actor_response.choices[0].message.content,
		})
		
		actor_input.append({
		"role": "user",
		"content": internal_configuration_msg,
		})

		if len(extracted_valid_moves)==2:
			two_moves_flag =1
			break
			


	if len(extracted_valid_moves)==2:
		proposals=extracted_valid_moves
	else:
		if len(extracted_valid_moves)==1:
			proposals=[]
			proposals.append(extracted_valid_moves[0])
			proposals.append(extracted_valid_moves[0])
		else:
			proposals=[]
			if len(actor_truncated_response)==2:

				proposals.append(actor_truncated_response[0])
				proposals.append(actor_truncated_response[1])
			else:
				proposals.append(actor_truncated_response[0])
				proposals.append(actor_truncated_response[0])


	return proposals



def rollout_from_2nodes(current_room1,current_room2,start_prompt,proposals,detour_flag):
	if task_coordination_module(current_room1,detour_flag) or task_coordination_module(current_room2,detour_flag):

		moves_from_current_room1 = state_evaluator_module(current_room1,detour_flag)
		moves_from_current_room2 = state_evaluator_module(current_room2,detour_flag)
		if moves_from_current_room1 < moves_from_current_room2:
			next_move_chosen_for_system = proposals[0]
			next_states = None
			next_next_moves = None
		elif moves_from_current_room2 < moves_from_current_room1:
			next_move_chosen_for_system = proposals[1]
			next_states = None
			next_next_moves = None
		else:
			next_move_chosen_for_system = proposals[np.random.randint(0,2)]
			next_states = None
			next_next_moves = None

		print("reward location reached at first rollout and move chosen>>>",next_move_chosen_for_system)
		return next_move_chosen_for_system, next_states,next_next_moves


	else:
		# if reval_flag==0:



		internal_configuration_msg = """
		This is the current room:
		{}
		
	
		Give me only two different next rooms to go to from the current room that can help in yielding the most reward using as few steps as possible. Please format your answer as:
		Go from room <N> to room <N>.

		""" .format(current_room1)
		# else:

		# 	internal_configuration_msg = """
		# 	This is the current room:
		# 	{}
			
		
		# 	Give me only two different next rooms to go to from the current room that can help in yielding the most reward based on the new reward design using as few steps as possible. Please format your answer as:
		# 	Go from room <N> to room <N>.

		# 	""" .format(current_room1)

		prompt_state1= start_prompt+ "\n"+proposals[0]+ "." +"\n"+internal_configuration_msg
		

		input = [{
			"role": "system",
			"content": "you are an AI assistant",
		}]

		input.append({
			"role": "user",
			"content": prompt_state1,
		})


		

		
		next_move_proposals1 = actor_module_propose_two_actions(input,current_room1,detour_flag)
		print("move proposals from config 1>>",next_move_proposals1)

		
		# if reval_flag==0:


		internal_configuration_msg = """
		This is the current room:
		{}
		
	
		Give me only two different next rooms to go to from the current room that can help in yielding the most reward using as few steps as possible. Please format your answer as:
		Go from room <N> to room <N>.

		""" .format(current_room2)
		# else:
		# 	internal_configuration_msg = """
		# 	This is the current room:
		# 	{}
			
		
		# 	Give me only two different next rooms to go to from the current room that can help in yielding the most reward based on the new reward design using as few steps as possible. Please format your answer as:
		# 	Go from room <N> to room <N>.

		# 	""" .format(current_room2)



		prompt_state2= start_prompt+ "\n"+proposals[1]+ "." +"\n"+internal_configuration_msg
		

		input = [{
			"role": "system",
			"content": "you are an AI assistant",
		}]

		input.append({
			"role": "user",
			"content": prompt_state2,
		})


		next_move_proposals2 = actor_module_propose_two_actions(input,current_room2,detour_flag)
		
		print("move proposals from config 2>>",next_move_proposals2)

		
		current_room1_1 = int(next_move_proposals1[0].split(" ")[6])
		current_room1_2 = int(next_move_proposals1[1].split(" ")[6])
		current_room2_1 = int(next_move_proposals2[0].split(" ")[6])
		current_room2_2 = int(next_move_proposals2[1].split(" ")[6])
	
		print("next next config 1_1>>",current_room1_1)
		print("next next config 1_2>>",current_room1_2)

		print("next next config 2_1>>",current_room2_1)
		print("next next config 2_2>>",current_room2_2)


		moves_from_current_room1_1 = state_evaluator_module(current_room1_1,detour_flag)
		moves_from_current_room1_2 = state_evaluator_module(current_room1_2,detour_flag)
		moves_from_current_room2_1 = state_evaluator_module(current_room2_1,detour_flag)
		moves_from_current_room2_2 = state_evaluator_module(current_room2_2,detour_flag)
	
		four_configs_moves = []
		four_configs_moves.append(moves_from_current_room1_1)
		four_configs_moves.append(moves_from_current_room1_2)
		four_configs_moves.append(moves_from_current_room2_1)
		four_configs_moves.append(moves_from_current_room2_2)

		min_moves = min(moves_from_current_room1_1, moves_from_current_room1_2, moves_from_current_room2_1,moves_from_current_room2_2)

		index_min_moves = []
		for idx,config_moves in enumerate(four_configs_moves):
			if config_moves == min_moves:
				index_min_moves.append(idx)

		min_move_index_chosen = np.random.choice(index_min_moves)
		if min_move_index_chosen>1:
			next_move_chosen_for_system = proposals[1]
			next_states = [current_room2_1,current_room2_2]
			next_next_moves = next_move_proposals2
		else:
			next_move_chosen_for_system = proposals[0]
			next_states = [current_room1_1,current_room1_2]
			next_next_moves = next_move_proposals1


		print("num moves from 4 configs, move chosen>>>",moves_from_current_room1_1,moves_from_current_room1_2,moves_from_current_room2_1,moves_from_current_room2_2,next_move_chosen_for_system)

		return next_move_chosen_for_system, next_states,next_next_moves


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

for run_no in range(1,2):
	print("run number>>",run_no)

	for start_room in range(1,16):
		if start_room!=8 and start_room!=15:
		
			rooms_visited_before = []
			rooms_visited_after = []

			rooms_visited_before.append(start_room)
			rooms_visited_after.append(start_room)


			root_prompt = """
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
			- There is a chest with a reward of 50 for visiting room 8 and there is a chest with a reward of 10 for visiting room 15. 
			- You can collect the reward only once and only from one chest. 

			Goal: The goal is to find the shortest path from the starting room that yields the most reward.

			Here are two examples:
			{}

			Here is the task:

			This is the starting room:
			room {}

			Give me only two different next rooms to go to from the starting room that can help in yielding the most reward using as few steps as possible. Please format your answer as:
			Go from room <N> to room <N>.

			""".format(standard_prompt,start_room)

			input = [{
				"role": "system",
				"content": "you are an AI assistant",
			}]

			input.append({
				"role": "user",
				"content": root_prompt,
			})

			current_room = start_room
			# reward_rooms = [8,15]
			# reward_values = [50,10]
			flag=0
			total_reward = 0
			next_states = None
			detour_flag = 0 
			step = 0 
			while step < 10:
				

				print("step>>",step)
				if step ==0 or next_states is None:
					proposals = actor_module_propose_two_actions(input,current_room,detour_flag)
					print("move proposals>>",proposals)
					
					source_room1 = int(proposals[0].split(" ")[3])
					target_room1 = int(proposals[0].split(" ")[6])
					
					current_room1 = target_room1

					source_room2 = int(proposals[1].split(" ")[3])
					target_room2 = int(proposals[1].split(" ")[6])
					current_room2 = target_room2
					print("next config 1>>",current_room1)
					print("next config 2>>",current_room2)
					next_move_chosen_for_system, next_states, next_next_moves = rollout_from_2nodes(current_room1,current_room2,root_prompt,proposals,detour_flag)

				else:
					next_move_chosen_for_system, next_states, next_next_moves = rollout_from_2nodes(next_states[0],next_states[1],root_prompt,next_next_moves,detour_flag)



				source_room = int(next_move_chosen_for_system.split(" ")[3])
				target_room = int(next_move_chosen_for_system.split(" ")[6])
				
				current_room = target_room
				if detour_flag==0:
					rooms_visited_before.append(target_room)
				else:
					rooms_visited_after.append(target_room)
			

				

				# if reval_flag==0:

				configuration_msg = """This is the current room:
					room {}
					
				
					Give me only two different next rooms to go to from the current room that can help in yielding the most reward using as few steps as possible. Please format your answer as:
					Go from room <N> to room <N>.


					""".format(current_room)
				# else:
				# 	configuration_msg = """This is the current room:
				# 		room {}
						
					
				# 		Give me only two different next rooms to go to from the current room that can help in yielding the most reward based on the new reward design using as few steps as possible. Please format your answer as:
				# 		Go from room <N> to room <N>.


				# 		""".format(current_room)


				root_prompt+="\n"+next_move_chosen_for_system+"."

				

				
				step+=1
				if task_coordination_module(current_room,detour_flag):

					if detour_flag==1:
						flag=1
						test_dir = './logs/'
						check_path(test_dir)
						output_dir = test_dir + args.output_dir + '/'
						check_path(output_dir)

						with open(output_dir+'problem{}.log'.format(start_room), 'a') as w:
							w.write(root_prompt +'\n'+"List of rooms visited before detour = {}".format(rooms_visited_before))
							w.write('\n'+"List of rooms visited after detour = {}".format(rooms_visited_after))

						break
					else:
						print("starting detour evaluation>>>>")

						detour_prompt = """
						The door from room 1 to room 11 is locked and now room 13 is connected to room 11. You can collect the reward only once and only from one chest.

						Goal: The goal is to find the shortest path from the starting room that yields the most reward. 

						This is the starting room:
						room {}

						Give me only two different next rooms to go to from the starting room that can help in yielding the most reward using as few steps as possible. Please format your answer as:
						Go from room <N> to room <N>.

						""".format(start_room)

						current_room = start_room
						detour_flag=1

						root_prompt+="\n"+detour_prompt

						input = [{
						"role": "system",
						"content": "you are an AI assistant",
					}]

						input.append({
							"role": "user",
							"content": root_prompt,
							})

						step=0


				else:
					root_prompt+="\n"+configuration_msg

					input = [{
						"role": "system",
						"content": "you are an AI assistant",
					}]

					input.append({
						"role": "user",
						"content": root_prompt,
						})



			if flag==0:
				test_dir = './logs/'
				check_path(test_dir)
				output_dir = test_dir + args.output_dir + '/'
				check_path(output_dir)
				
				# output_dir+='run{}/'.format(run_no)
				# check_path(output_dir)
				with open(output_dir+'problem{}.log'.format(start_room), 'a') as w:
					w.write(root_prompt +'\n'+"List of rooms visited before detour = {}".format(rooms_visited_before))
					w.write('\n'+"List of rooms visited after detour = {}".format(rooms_visited_after))

					

			print("List of rooms visited before detour = {}".format(rooms_visited_before))
			print("List of rooms visited after detour = {}".format(rooms_visited_after))
			
			print("done solving problem {}".format(start_room))
					





