import openai
from copy import deepcopy
import random
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




def move_validator_module(room1,room2,source_room, target_room):

	move_validator_prompt = """

		Problem description:

		You are exploring a zoo. You enter zone 1 and you see two passages one on the right and one on the left. You choose the passage on the right and enter zone 3. You see two passages in zone 3. You can choose the passage on the left or the passage on the right. You choose the passage on the right, and your enter zone 7 and there's a cage. You open it and find $50 but remember you're only exploring so you don't take any money. Then you go back to zone 3, and this time you go to the passage on the left to zone 6. You find another cage; you open it and there's $10 (but you don't take any money). You go back to zone 1. This time you choose the passage on the left and you go to zone 2. Again, you see two passages, one on the left and one on the right. You enter the passage on the right, and you find yourself in zone 5. There's a cage in zone 5. You open it and find $22. Then you go back to zone 2, and this time you go to the passage on the left, and you find yourself in zone 4. You find a cage; you open it and there's $56 (you still don't take any money). You go back to zone 1. 
		
		Goal: The goal is to check whether the proposed step between the two zones exists or not, and based on that if it is a valid or invalid step.

		Here are two examples:

		Example 1:

		Proposed step:
		Go from zone 1 to zone 2.

		Answer:
		Check whether zone 1 and zone 2 are directly connected. From zone 1 there is a passage on the left, which takes you to zone 2, and there is a passage on the right, which takes you to zone 3. From zone 2 you can either go back to zone 1, or take the passage on the left, which takes you to zone 4, or take the passage on the right, which takes you to zone 5. Since zone 1 and zone 2 directly connected to each other, the proposed step exists and is valid.
	
		Example 2:

		Proposed step:
		Go from zone 3 to zone 5.

		Answer:
		Check whether zone 3 and zone 5 are directly connected. From zone 3 you can either go to zone 6 or zone 7. From zone 5 you can go back to zone 2. Since zone 3 and zone 5 aren't directly connected to each other, the proposed step doesn't exist and is invalid.
	
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
		- There is a chest with a reward of 50 for visiting room {} and there is a chest with a reward of 10 for visiting room {}. 
		- You can collect the reward only once and only from one chest. 
		- If you enter a room with a chest, then you must collect the reward from that chest, and you cannot collect anymore rewards.
		
	
		
		Goal: The goal is to check whether the proposed step between the two rooms exists or not, and based on that if it is a valid or invalid step.

		

		Proposed step:
		Go from room {} to room {}.

		Answer:


		""".format(room1,room2,source_room,target_room)


	move_validator_input = [{
	"role": "system",
	"content": "you are an AI assistant",
	}]

	move_validator_input.append({
		"role": "user",
		"content": move_validator_prompt,
	})

	cur_try=0
	while cur_try<20:

		try:

			

			validator_response= client.chat.completions.create(model=deployment_name, messages=move_validator_input,temperature=0.0,top_p = 0,max_tokens=500)
			

			# global num_validator_calls
			# global num_validator_input_tokens
			# global num_validator_output_tokens
			# num_validator_calls+=1
			# num_validator_input_tokens+=validator_response["usage"]["prompt_tokens"]
			# num_validator_output_tokens+=validator_response["usage"]["completion_tokens"]

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


def task_coordination_module(current_room,room1,room2):

	task_coordination_prompt = """

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
		- There is a chest with a reward of 50 for visiting room {} and there is a chest with a reward of 10 for visiting room {}. 
		- You can collect the reward only once and only from one chest. 
		- If you enter a room with a chest, then you must collect the reward from that chest, and you cannot collect anymore rewards.

		Goal: The goal is to predict whether there is a chest with a reward in the current room or not. If there is a chest with a reward in the current room say "yes" otherwise "no".

	
		This is the current room:
		room {}

	
			
			

		""".format(room1,room2,current_room)

	task_coordination_input = [{
	"role": "system",
	"content": "you are an AI assistant",
	}]

	task_coordination_input.append({
		"role": "user",
		"content": task_coordination_prompt,
	})

	cur_try=0
	while cur_try<20:

		try:

		

			task_coordination_response= client.chat.completions.create(model=deployment_name, messages=task_coordination_input,temperature=0.0,top_p = 0,max_tokens=500)
			

			# global num_coordinator_calls
			# global num_coordinator_input_tokens
			# global num_coordinator_output_tokens

			# num_coordinator_calls+=1
			# num_coordinator_input_tokens+=task_coordination_response["usage"]["prompt_tokens"]
			# num_coordinator_output_tokens+=task_coordination_response["usage"]["completion_tokens"]
			

			
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


	


def state_evaluator_module(current_room,decomposer_output,room1,room2):

	state_evaluator_prompt = """
		
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
		- There is a chest with a reward of 50 for visiting room {} and there is a chest with a reward of 10 for visiting room {}. 
		- You can collect the reward only once and only from one chest. 
		- If you enter a room with a chest, then you must collect the reward from that chest, and you cannot collect anymore rewards.


		
		What is the minimum number of steps from the room {} to the room with a chest with the highest reward?

		Identify the room with the highest reward chest, analyze the room connections, and compute the fewest steps required from the given current room to that room, keeping reward collection rules in mind.


		""".format(room1,room2,current_room)


	state_evaluator_input = [{
	"role": "system",
	"content": "you are an AI assistant",
	}]

	state_evaluator_input.append({
		"role": "user",
		"content": state_evaluator_prompt,
	})

	cur_try=0
	while cur_try<20:

		try:

		

			evaluator_response= client.chat.completions.create(model=deployment_name, messages=state_evaluator_input,temperature=0.0,top_p = 0,max_tokens=1000)
			

			
			# global num_evaluator_calls
			# global num_evaluator_input_tokens
			# global num_evaluator_output_tokens
			# num_evaluator_calls+=1
			# num_evaluator_input_tokens+=evaluator_response["usage"]["prompt_tokens"]
			# num_evaluator_output_tokens+=evaluator_response["usage"]["completion_tokens"]
			

			break

		except Exception as e:
			err = f"Error: {str(e)}"
			print(err)
			time.sleep(120)
			cur_try+=1
			continue
	print("evaluator_response>>",evaluator_response.choices[0].message.content)

	state_evaluator_input.append({
	"role": "assistant",
	"content": evaluator_response.choices[0].message.content,
	})

	query_msg = """
	Please parse your above response to provide the minimum number of steps from the current room to the room with a chest with the highest reward.


	Please provide only a single integer number after "Answer = "

	"""
	
	state_evaluator_input.append({
	"role": "user",
	"content": query_msg,
	})


	cur_try=0
	while cur_try<10:

		try:
			time1=time.time()
			evaluator_parse_response = client.chat.completions.create(model=deployment_name, messages=state_evaluator_input,temperature=0.0, top_p= 0 ,max_tokens=500)
			

			
			time2=time.time()

			# global num_evaluator_calls
			# global num_evaluator_input_tokens
			# global num_evaluator_output_tokens
			# global evaluator_response_time
			# num_evaluator_calls+=1
			# num_evaluator_input_tokens.append(evaluator_parse_response.usage.prompt_tokens)
			# num_evaluator_output_tokens.append(evaluator_parse_response.usage.completion_tokens)
			# evaluator_response_time.append(time2-time1)

			break

		except Exception as e:
			err = f"Error: {str(e)}"
			print(err)
			time.sleep(120)
			cur_try+=1
			continue
	print("evaluator parse response>>",evaluator_parse_response.choices[0].message.content)
	try:

		return int(evaluator_parse_response.choices[0].message.content.split("Answer = ")[-1])
	except Exception as e:
		err = f"Error: {str(e)}"
		print(err)
		print("random sampling>>>>")
		return np.random.randint(1,7)

	# first_index = 0
	# for k in range(len(evaluator_response.choices[0].message.content) - 29):
	# 	if evaluator_response.choices[0].message.content[k:k+30] == 'that yields the most reward is':
	# 		first_index = k
			

	# second_index = 0
	# for t in range(first_index, len(evaluator_response.choices[0].message.content)):
	# 	if evaluator_response.choices[0].message.content[t] == '.' or evaluator_response.choices[0].message.content[t] == ',' :
	# 		second_index = t
	# 		break
	# return int(evaluator_response.choices[0].message.content[first_index:second_index].split(" ")[-1])







def actor_module_propose_two_actions(actor_input,current_room,room1,room2):

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

					

					actor_response = client.chat.completions.create(model=deployment_name, messages=actor_input,temperature=0.1*cur_try,max_tokens=1000)
			

				else:

					actor_response = client.chat.completions.create(model=deployment_name, messages=actor_input,temperature=0.0,top_p=0,max_tokens=1000)
			



				

				# global num_actor_calls
				# global num_actor_input_tokens
				# global num_actor_output_tokens
				# num_actor_calls+=1
				# num_actor_input_tokens+=actor_response["usage"]["prompt_tokens"]
				# num_actor_output_tokens+=actor_response["usage"]["completion_tokens"]

				actor_input.append({
				"role": "assistant",
				"content": actor_response.choices[0].message.content,
				})

				query_msg = """
				Please parse your above response to provide the two different next rooms you can go to from room {} that can help in reaching the room with a chest with the highest reward using as few steps as possible.

				Please provide the room numbers only as integers seperated by commas after "Answer = "

				""".format(current_room)
				
				actor_input.append({
				"role": "user",
				"content": query_msg,
				})


				another_cur_try=0
				while another_cur_try<10:

					try:
						time1=time.time()
						actor_parse_response = client.chat.completions.create(model=deployment_name, messages=actor_input,temperature=0.0, top_p= 0 ,max_tokens=500)
						

						
						time2=time.time()

						# global num_evaluator_calls
						# global num_evaluator_input_tokens
						# global num_evaluator_output_tokens
						# global evaluator_response_time
						# num_evaluator_calls+=1
						# num_evaluator_input_tokens.append(evaluator_parse_response.usage.prompt_tokens)
						# num_evaluator_output_tokens.append(evaluator_parse_response.usage.completion_tokens)
						# evaluator_response_time.append(time2-time1)

						break

					except Exception as e:
						err = f"Error: {str(e)}"
						print(err)
						time.sleep(120)
						another_cur_try+=1
						continue


				print("GPT-4 full response>>>",actor_response.choices[0].message.content)
				print("actor parse response>>>",actor_parse_response.choices[0].message.content)


				actor_truncated_response = []

				rooms_list = actor_parse_response.choices[0].message.content.split("Answer = ")[-1].split("\n")[0].replace(".","").strip().split(",")
				for room in rooms_list:
					try:
						integer_room = int(room)
						if "Go from room {} to room {}".format(current_room,integer_room) not in actor_truncated_response:

							actor_truncated_response.append("Go from room {} to room {}".format(current_room,integer_room))

					except Exception as e:
						print("actor parse response and rooms list>>",actor_parse_response.choices[0].message.content, rooms_list)
						err = f"Error: {str(e)}"
						print(err)

				

				

				print("GPT-4 extracted moves>>>",actor_truncated_response)
				if len(actor_truncated_response)>=2:
					previous_actor_truncated_response = actor_truncated_response

					break

				elif len(actor_truncated_response)==1:
					previous_actor_truncated_response = actor_truncated_response

					one_move_msg = """
					You provided just one next room to go to from the current room. However it is possible to provide two different next rooms to go to from the current room.
			
					What are the two different next rooms I can go to from room {} that can help in reaching the room with a chest with the highest reward using as few steps as possible?


					First list all the rooms directly connected to your current room, and then select the ones leading to the highest-reward chest, minimizing steps and bypassing rooms containing lower-value rewards.
			

					""".format(current_room)
						
					actor_input.append({
							"role": "assistant",
							"content": actor_parse_response.choices[0].message.content,
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


			move_validity1, validity1_response = move_validator_module(room1,room2,int(actor_truncated_response[0].split(" ")[3]), int(actor_truncated_response[0].split(" ")[6]))
			move_validity2, validity2_response = move_validator_module(room1,room2,int(actor_truncated_response[1].split(" ")[3]), int(actor_truncated_response[1].split(" ")[6]))
				
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
				
				internal_configuration_msg = """
				{}

				What are the two different next rooms I can go to from room {} that can help in reaching the room with a chest with the highest reward using as few steps as possible?


				First list all the rooms directly connected to your current room, and then select the ones leading to the highest-reward chest, minimizing steps and bypassing rooms containing lower-value rewards.
			

				""".format(validity2_response,current_room)


				num_tries+=1

			elif move_validity1 =='no' and move_validity2 =='yes':
				if actor_truncated_response[1] not in extracted_valid_moves:

					extracted_valid_moves.append(actor_truncated_response[1])
				
				
				internal_configuration_msg = """
				{}

				What are the two different next rooms I can go to from room {} that can help in reaching the room with a chest with the highest reward using as few steps as possible?


				First list all the rooms directly connected to your current room, and then select the ones leading to the highest-reward chest, minimizing steps and bypassing rooms containing lower-value rewards.
			

				""".format(validity1_response,current_room)

				num_tries+=1
			else:
				
				internal_configuration_msg = """
				{}

				{}

				What are the two different next rooms I can go to from room {} that can help in reaching the room with a chest with the highest reward using as few steps as possible?


				First list all the rooms directly connected to your current room, and then select the ones leading to the highest-reward chest, minimizing steps and bypassing rooms containing lower-value rewards.
			

				""".format(validity1_response,validity2_response,current_room)



				num_tries+=1
		else:
			# proposals.append(actor_truncated_response[0])
			# proposals.append(actor_truncated_response[0])

			move_validity1, validity1_response = move_validator_module(room1,room2,int(actor_truncated_response[0].split(" ")[3]), int(actor_truncated_response[0].split(" ")[6]))
			if move_validity1 =='yes':
				# break
				if actor_truncated_response[0] not in extracted_valid_moves:

					extracted_valid_moves.append(actor_truncated_response[0])

				break
				
				
			else:

				internal_configuration_msg = """
				{}


				What are the two different next rooms I can go to from room {} that can help in reaching the room with a chest with the highest reward using as few steps as possible?


				First list all the rooms directly connected to your current room, and then select the ones leading to the highest-reward chest, minimizing steps and bypassing rooms containing lower-value rewards.
			

				""".format(validity1_response,current_room)

				
				num_tries+=1
				




		actor_input.append({
		"role": "assistant",
		"content": actor_parse_response.choices[0].message.content,
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





def rollout_from_2nodes(current_room1,current_room2,start_prompt,decomposer_output,proposals,room1,room2):
	if task_coordination_module(current_room1,room1,room2) or task_coordination_module(current_room2,room1,room2):

		moves_from_current_room1 = state_evaluator_module(current_room1,decomposer_output,room1,room2)
		moves_from_current_room2 = state_evaluator_module(current_room2,decomposer_output,room1,room2)
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


		
	

		input = [{
			"role": "system",
			"content": "you are an AI assistant",
		}]

		input.append({
			"role": "user",
			"content": start_prompt.format(room1 = room1, room2= room2,goal= decomposer_output,r = current_room1),
		})
		

		
		next_move_proposals1 = actor_module_propose_two_actions(input,current_room1,room1,room2)
		print("move proposals from config 1>>",next_move_proposals1)

		


		
		input = [{
			"role": "system",
			"content": "you are an AI assistant",
		}]

		input.append({
			"role": "user",
			"content": start_prompt.format(room1= room1,room2 = room2,goal=decomposer_output,r = current_room2),
		})

		next_move_proposals2 = actor_module_propose_two_actions(input, current_room2,room1,room2)
		
		print("move proposals from config 2>>",next_move_proposals2)

		
		current_room1_1 = int(next_move_proposals1[0].split(" ")[6])
		current_room1_2 = int(next_move_proposals1[1].split(" ")[6])
		current_room2_1 = int(next_move_proposals2[0].split(" ")[6])
		current_room2_2 = int(next_move_proposals2[1].split(" ")[6])
	
		print("next next config 1_1>>",current_room1_1)
		print("next next config 1_2>>",current_room1_2)

		print("next next config 2_1>>",current_room2_1)
		print("next next config 2_2>>",current_room2_2)


		moves_from_current_room1_1 = state_evaluator_module(current_room1_1,decomposer_output,room1,room2)
		moves_from_current_room1_2 = state_evaluator_module(current_room1_2,decomposer_output,room1,room2)
		moves_from_current_room2_1 = state_evaluator_module(current_room2_1,decomposer_output,room1,room2)
		moves_from_current_room2_2 = state_evaluator_module(current_room2_2,decomposer_output,room1,room2)
	
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


def decomposer_module(room1,room2):
	decomposer_prompt = """
	Imagine a castle with 15 rooms. 
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
	- There is a chest with a reward of 50 for visiting room {} and there is a chest with a reward of 10 for visiting room {}. 
	- You can collect the reward only once and only from one chest. 
	- If you enter a room with a chest, then you must collect the reward from that chest, and you cannot collect anymore rewards.

   
	Can you describe your goal, mentioning the room where you should go to and the room which you should avoid?
	""".format(room1, room2)

	decomposer_input = [{
	"role": "system",
	"content": "you are an AI assistant",
	}]

	decomposer_input.append({
		"role": "user",
		"content": decomposer_prompt,
	})

	cur_try=0
	while cur_try<20:

		try:

		

			decomposer_response= client.chat.completions.create(model=deployment_name, messages=decomposer_input,temperature=0.0,top_p = 0,max_tokens=1000)
			

			
			# global num_evaluator_calls
			# global num_evaluator_input_tokens
			# global num_evaluator_output_tokens
			# num_evaluator_calls+=1
			# num_evaluator_input_tokens+=evaluator_response["usage"]["prompt_tokens"]
			# num_evaluator_output_tokens+=evaluator_response["usage"]["completion_tokens"]
			

			break

		except Exception as e:
			err = f"Error: {str(e)}"
			print(err)
			time.sleep(120)
			cur_try+=1
			continue
	print("decomposer_response>>",decomposer_response.choices[0].message.content)
	return decomposer_response.choices[0].message.content

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





for run_no in range(1,4):
	print("run number>>",run_no)
	num_validator_calls = 0 
	num_evaluator_calls = 0 

	num_coordinator_calls = 0 
	num_actor_calls = 0
	num_validator_input_tokens = 0
	num_validator_output_tokens = 0
	num_evaluator_input_tokens = 0
	num_evaluator_output_tokens = 0
	
	num_coordinator_input_tokens = 0
	num_coordinator_output_tokens = 0
	num_actor_input_tokens = 0
	num_actor_output_tokens = 0
	

	for room1,room2 in reward_rooms:

		for start_room in range(1,16):

			if start_room!=room1 and start_room!=room2:
		
				rooms_visited = []
				rooms_visited.append(start_room)

				decomposer_output = decomposer_module(room1,room2)


				root_prompt = """
				Imagine a castle with 15 rooms. 
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

				
				{goal}

				What are the two different next rooms I can go to from room {r} that can help in reaching the room with a chest with the highest reward using as few steps as possible?


				First list all the rooms directly connected to your current room, and then select the ones leading to the highest-reward chest, minimizing steps and bypassing rooms containing lower-value rewards.
				

				"""


				
				

				input = [{
					"role": "system",
					"content": "you are an AI assistant",
				}]

				input.append({
					"role": "user",
					"content": root_prompt.format(room1=room1,room2=room2,goal= decomposer_output,r = start_room),
				})

				current_room = start_room
				# reward_rooms = [8,15]
				# reward_values = [50,10]
				flag=0
				total_reward = 0
				next_states = None
				for step in range(6):
					

					print("step>>",step)
					if step ==0 or next_states is None:
						proposals = actor_module_propose_two_actions(input,current_room,room1,room2)
						print("move proposals>>",proposals)
						
						source_room1 = int(proposals[0].split(" ")[3])
						target_room1 = int(proposals[0].split(" ")[6])
						
						current_room1 = target_room1

						source_room2 = int(proposals[1].split(" ")[3])
						target_room2 = int(proposals[1].split(" ")[6])
						current_room2 = target_room2
						print("next config 1>>",current_room1)
						print("next config 2>>",current_room2)
						next_move_chosen_for_system, next_states, next_next_moves = rollout_from_2nodes(current_room1,current_room2,root_prompt,decomposer_output,proposals,room1,room2)

					else:
						next_move_chosen_for_system, next_states, next_next_moves = rollout_from_2nodes(next_states[0],next_states[1],root_prompt,decomposer_output,next_next_moves,room1,room2)



					source_room = int(next_move_chosen_for_system.split(" ")[3])
					target_room = int(next_move_chosen_for_system.split(" ")[6])
					
					current_room = target_room
					rooms_visited.append(target_room)
				

					

					# configuration_msg = """This is the current room:
					# 	room {}
						
					
					# 	Give me only two different next rooms to go to from the current room that can help in reaching the room with a chest with the highest reward using as few steps as possible. Please format your answer as:
					# 	Go from room <N> to room <N>.


					# 	""".format(current_room)

					# # root_prompt+="\n"+next_move_chosen_for_system+"."+"\n"+configuration_msg
					# root_prompt=reduced_prompt+"\n"+configuration_msg

					

					input = [{
							"role": "system",
							"content": "you are an AI assistant",
						}]

					input.append({
						"role": "user",
						"content": root_prompt.format(room1=room1,room2=room2,goal= decomposer_output,r = current_room),
						})
					if task_coordination_module(current_room,room1,room2):
						flag=1
						test_dir = './logs/'
						check_path(test_dir)
						output_dir = test_dir + args.output_dir + '/'
						check_path(output_dir)

						
						output_dir+='run{}/'.format(run_no)
						check_path(output_dir)
						with open(output_dir + 'problem_start_{}_higherreward_{}_lowerreward_{}.log'.format(start_room,room1,room2), 'a') as w:
							w.write(root_prompt +'\n'+"List of rooms visited = {}".format(rooms_visited))

						break

				if flag==0:
					test_dir = './logs/'
					check_path(test_dir)
					output_dir = test_dir + args.output_dir + '/'
					check_path(output_dir)

					output_dir+='run{}/'.format(run_no)
					check_path(output_dir)
					with open(output_dir+'problem_start_{}_higherreward_{}_lowerreward_{}.log'.format(start_room,room1,room2), 'a') as w:
						w.write(root_prompt +'\n'+"List of rooms visited = {}".format(rooms_visited))

				
				# print("number of validator calls till now>>",num_validator_calls)
				# print("number of evaluator calls till now>>",num_evaluator_calls)
				
				# print("number of actor calls till now>>",num_actor_calls)
				# print("number of coordinator calls till now>>",num_coordinator_calls)
				

				# print("number of validator input and output tokens till now>>",num_validator_input_tokens,num_validator_output_tokens)
				# print("number of evaluator input and output tokens till now>>",num_evaluator_input_tokens,num_evaluator_output_tokens)
				
				# print("number of actor input and output tokens till now>>",num_actor_input_tokens,num_actor_output_tokens)
				# print("number of coordinator input and output tokens till now>>",num_coordinator_input_tokens,num_coordinator_output_tokens)
				
				


				print("List of rooms visited = {}".format(rooms_visited))
				print("done solving problem with start room {}, higher reward {}, lower reward {}".format(start_room,room1, room2))
						




