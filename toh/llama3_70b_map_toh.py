import openai
from gen_start_config import *
from toh_two_shot_examples import standard_prompt
from copy import deepcopy
import time
import re
import json
import os
from openai import AzureOpenAI
import transformers
import torch

model_id = "models--meta-llama--Meta-Llama-3-70B-Instruct/snapshots/7129260dd854a80eb10ace5f61c20324b472b31c"

pipeline = transformers.pipeline(
	"text-generation",
	model=model_id,
	model_kwargs={"torch_dtype": torch.float16},
	device_map="auto",
)



all_As, all_Bs, all_Cs = generate_all_start_config()

number_message_mapping = {3:"three numbers -- 0, 1, and 2 --", 4:"four numbers -- 0, 1, 2, and 3 --",5:"five numbers -- 0, 1, 2, 3, and 4 --"}
number_target_mapping = {3:"C = [0, 1, 2]", 4:"C = [0, 1, 2, 3]",5:"C = [0, 1, 2, 3, 4]"}
char_int_mapping = {'A':0,'B':1,'C':2}

evaluator_cache = {}
monitor_cache = {}
predictor_cache = {}
coordinator_cache = {}

def check_path(path):
	if not os.path.exists(path):
		os.mkdir(path)

def move_validator_module(state_A, state_B, state_C, gpt_truncated_move_proposal):

	move_validator_prompt = """

		Problem description:
		- There are three lists labeled A, B, and C.
		- There is a set of numbers distributed among those three lists.
		- You can only move numbers from the rightmost end of one list to the rightmost end of another list.
		Rule #1: You can only move a number if it is at the rightmost end of its current list.
		Rule #2: You can only move a number to the rightmost end of a list if it is larger than the other numbers in that list.
		A move is valid if it satisfies both Rule #1 and Rule #2.
		A move is invalid if it violates either Rule #1 or Rule #2.

		Goal: Your task is to check if the proposed move satisfies or violates Rule #1 and Rule #2 and based on that if it is a valid or invalid move.

		Here are two examples:
		
		Example 1:

		This is the initial configuration:
		A = []
		B = [1]
		C = [0, 2]

		Proposed move:
		Move 0 from C to B.

		Answer:
		First check whether the move satisfies or violates Rule #1. Index of 0 in list C is 0. Length of list C is 2. The difference in length of list C and index of 0 in list C is 2, which is not equal to 1. Hence 0 is not at the rightmost end of list C, and the move violates Rule #1.
		Next check whether the move satisfies or violates Rule #2. For that compute the maximum of list B, to which 0 is moved. Maximum of list B is 1. 0 is not larger than 1. Hence the move violates Rule #2.
		Since the Move 0 from list C to list B violates both Rule #1 and Rule #2, it is invalid.

		Example 2:

		This is the initial configuration:
		A = []
		B = [1]
		C = [0, 2]

		Proposed move:
		Move 2 from C to B.

		Answer:
		First check whether the move satisfies or violates Rule #1. Index of 2 in list C is 1. Length of list C is 2. The difference in length of list C and index of 2 in list C is 1. Hence 2 is at the rightmost end of list C, and the move satisfies Rule #1.
		Next check whether the move satisfies or violates Rule #2. For that compute the maximum of list B, to which 2 is moved. Maximum of list B is 1. 2 is larger than 1. Hence the move satisfies Rule #2.
		Since the Move 2 from list C to list B satisfies both Rule #1 and Rule #2, it is valid.

		
		Here is the task:

		This is the initial configuration:
		{}
		{}
		{}

		Proposed move:
		{}.

		Answer:

		""".format("A = "+str(state_A),"B = "+str(state_B),"C = "+str(state_C),gpt_truncated_move_proposal)


	if move_validator_prompt in monitor_cache:
		return monitor_cache[move_validator_prompt][0], monitor_cache[move_validator_prompt][1]
	move_validator_input = [{
			"role": "system",
			"content": "you are an AI assistant",
		}]

	move_validator_input.append({
		"role": "user",
		"content": move_validator_prompt,
	})

	time1 = time.time()

	prompt = pipeline.tokenizer.apply_chat_template(
			move_validator_input, 
			tokenize=False, 
			add_generation_prompt=True
	)

	terminators = [
		pipeline.tokenizer.eos_token_id,
		pipeline.tokenizer.convert_tokens_to_ids("<|eot_id|>")
	]

	outputs = pipeline(
		prompt,
		max_new_tokens=500,
		eos_token_id=terminators,
		do_sample=False
	)

	
	print("validator response>>>",outputs[0]["generated_text"][len(prompt):])
	

	time2 = time.time()
	
	
	global num_validator_input_tokens
	global num_validator_output_tokens
	global validator_response_time
	# num_validator_calls+=1
	# num_validator_input_tokens.append(validator_response.usage.prompt_tokens)
	# num_validator_output_tokens.append(validator_response.usage.completion_tokens)
	validator_response_time.append(time2-time1)

	# if "Conclusion" in validator_response.choices[0].message.content:
	# 	final_response = validator_response.choices[0].message.content.split('Conclusion')[-1]
	# else:
	# 	final_response = validator_response.choices[0].message.content.split('Answer')[-1]

	char_list_response = outputs[0]["generated_text"][len(prompt):].split('\n')[-1]#.replace(".","").split(" ")

	if 'invalid' in char_list_response or 'Invalid' in char_list_response or 'not valid' in char_list_response or 'not a valid' in char_list_response:
		move_validity = 'no'
	else:
		move_validity = 'yes'

			

					
			# if 'Move' in gpt_truncated_response and 'from list' in gpt_truncated_response and 'to list' in gpt_truncated_response and (('A' in gpt_truncated_response and 'B' in gpt_truncated_response ) or ('C' in gpt_truncated_response and 'B' in gpt_truncated_response ) or ('A' in gpt_truncated_response and 'C' in gpt_truncated_response )) :

			

		
	monitor_cache[move_validator_prompt] = (move_validity, outputs[0]["generated_text"][len(prompt):])
	return move_validity, outputs[0]["generated_text"][len(prompt):]

def task_coordination_module(predicted_state, goal_configuration):

	task_coordination_prompt = """
	In this task, you will be presented with three lists labeled A, B, and C. There is a set of numbers distributed among those three lists. You will be presented with two configurations, one labelled 'current configuration', and one labelled 'goal configuration'. 
	Your task is simply to indicate whether the current configuration matches the goal configuration or not.

	Here are two examples:
	
	Example 1:
	
	This is the current configuration:
	A = []
	B = []
	C = [0, 1, 2]

	This is the goal configuration:
	A = []
	B = []
	C = [0, 1, 2]
	
	Answer: 
	The current configuraton matches the goal configuration. Hence yes.
	
	
	Example 2:
	
	This is the current configuration:
	A = [0, 1]
	B = [2]
	C = []

	This is the goal configuration:
	A = []
	B = []
	C = [0, 1, 2]
	
	Answer: 
	The current configuraton doesn't match the goal configuration. Hence no.
	
	
	Here is the task:
	
	This is the current configuration:
	{}
	{}
	{}

	This is the goal configuration:
	{}
	{}
	{}
	
	Answer: 

	""".format("A = "+str(predicted_state[0]),"B = "+str(predicted_state[1]),"C = "+str(predicted_state[2]), "A = "+str(goal_configuration[0]),"B = "+str(goal_configuration[1]),"C = "+str(goal_configuration[2]))
	
	if task_coordination_prompt in coordinator_cache:
		return coordinator_cache[task_coordination_prompt]

	task_coordination_input = [{
				"role": "system",
				"content": "you are an AI assistant",
			}]

	task_coordination_input.append({
		"role": "user",
		"content": task_coordination_prompt,
	})

	prompt = pipeline.tokenizer.apply_chat_template(
			task_coordination_input, 
			tokenize=False, 
			add_generation_prompt=True
	)

	terminators = [
		pipeline.tokenizer.eos_token_id,
		pipeline.tokenizer.convert_tokens_to_ids("<|eot_id|>")
	]

	outputs = pipeline(
		prompt,
		max_new_tokens=200,
		eos_token_id=terminators,
		do_sample=False
	)


			
	print("coordinator response>>>",outputs[0]["generated_text"][len(prompt):])
			
	time2=time.time()

	# global num_coordinator_calls
	global num_coordinator_input_tokens
	global num_coordinator_output_tokens
	global coordinator_response_time

			# num_coordinator_calls+=1

			# num_coordinator_input_tokens.append(task_coordination_response.usage.prompt_tokens)
			# num_coordinator_output_tokens.append(task_coordination_response.usage.completion_tokens)
			# coordinator_response_time.append(time2-time1)
			
	if "yes" in outputs[0]["generated_text"][len(prompt):] or "Yes" in outputs[0]["generated_text"][len(prompt):]:
		match_flag=1
	else:
		match_flag=0
		
		

	coordinator_cache[task_coordination_prompt] = match_flag
	return match_flag


def actor_module_propose_two_actions(actor_input,temp_current_configuration,goal_config,step,max_content_limit_exceed_count):

	extracted_valid_moves = []
	num_tries = 0
	previous_actor_truncated_response = None
	while num_tries < 10:
		# proposals = []
		cur_try = 0
		check_flag = 0
		one_response_flag = 0
		while cur_try <10:
			try:

				if check_flag == 1 or one_response_flag==1:
					time1=time.time()

					# actor_response = client.chat.completions.create(model=deployment_name, messages=actor_input,temperature=0.1*cur_try,max_tokens=500)
			

					prompt = pipeline.tokenizer.apply_chat_template(
					actor_input, 
					tokenize=False, 
					add_generation_prompt=True
					)

					terminators = [
						pipeline.tokenizer.eos_token_id,
						pipeline.tokenizer.convert_tokens_to_ids("<|eot_id|>")
					]

					outputs = pipeline(
						prompt,
						max_new_tokens=500,
						eos_token_id=terminators,
						do_sample=True,temperature=0.1*cur_try
					)
					# actor_response = client.chat.completions.create(model=deployment_name, messages=actor_input,temperature=0.1*cur_try,max_tokens=500)
			
					
					time2=time.time()

				else:
					time1=time.time()

					# actor_response = client.chat.completions.create(model=deployment_name, messages=actor_input,temperature=0.0, top_p= 0 ,max_tokens=500)
			

					prompt = pipeline.tokenizer.apply_chat_template(
					actor_input, 
					tokenize=False, 
					add_generation_prompt=True
					)

					terminators = [
						pipeline.tokenizer.eos_token_id,
						pipeline.tokenizer.convert_tokens_to_ids("<|eot_id|>")
					]

					outputs = pipeline(
						prompt,
						max_new_tokens=500,
						eos_token_id=terminators,
						do_sample=False
					)
					
					# actor_response = client.chat.completions.create(model=deployment_name, messages=actor_input,temperature=0.0, top_p= 0 ,max_tokens=500)
			
				
					time2=time.time()

					# actor_response = openai.ChatCompletion.create(
					# 	engine='gpt-4-32k',
					# 	messages=actor_input,temperature=0.1*num_tries,
					# 		max_tokens=500)

				# global num_actor_calls
				global num_actor_input_tokens
				global num_actor_output_tokens
				global actor_response_time
				# num_actor_calls+=1
				# num_actor_input_tokens.append(actor_response.usage.prompt_tokens)
				# num_actor_output_tokens.append(actor_response.usage.completion_tokens)
				actor_response_time.append(time2-time1)
				
				
				actor_truncated_response = []
				for k in range(len(outputs[0]["generated_text"][len(prompt):]) - 17):
					sub_str = outputs[0]["generated_text"][len(prompt):][k:k+18]
					if 'Move' in sub_str and '.' not in sub_str and 'from' in sub_str and 'to' in sub_str and (('A' in sub_str and 'B' in sub_str ) or ('C' in sub_str and 'B' in sub_str ) or ('A' in sub_str and 'C' in sub_str )) :


						# if sub_str not in actor_truncated_response:

						actor_truncated_response.append(sub_str)
					



				# if 'Move' in gpt_truncated_response and 'from list' in gpt_truncated_response and 'to list' in gpt_truncated_response and (('A' in gpt_truncated_response and 'B' in gpt_truncated_response ) or ('C' in gpt_truncated_response and 'B' in gpt_truncated_response ) or ('A' in gpt_truncated_response and 'C' in gpt_truncated_response )) :
				print("actor_response>>",outputs[0]["generated_text"][len(prompt):])
				print("all extracted moves>>>",actor_truncated_response)
				if len(actor_truncated_response)>2:
					actor_truncated_response = actor_truncated_response[-2:]
				print("last 2 extracted moves>>>",actor_truncated_response)
				
				if len(actor_truncated_response)>=2:
					previous_actor_truncated_response = actor_truncated_response

					break
				elif len(actor_truncated_response)==1:
					previous_actor_truncated_response = actor_truncated_response

					one_move_msg = """
					You provided just one valid next move. However it is possible to provide two valid next moves from the current configuration.
			
					This is the current configuration:
					{}
					{}
					{}
					
					This is the goal configuration:
					{}
					{}
					{}



					Please try again to give me only two different valid next moves possible from only the current configuration that would help in reaching the goal configuration using as few moves as possible.
					Your answer should only be in the format as below:
					1. Move <N> from <src> to <trg>.


					""".format("A = "+str(temp_current_configuration[0]),"B = "+str(temp_current_configuration[1]),"C = "+str(temp_current_configuration[2]), "A = "+str(goal_config[0]),"B = "+str(goal_config[1]),"C = "+str(goal_config[2]))
						
					actor_input.append({
							"role": "assistant",
							"content": outputs[0]["generated_text"][len(prompt):],
						})
						
					actor_input.append({
						"role": "user",
						"content": one_move_msg,
						})

					one_response_flag=1
					cur_try+=1
					continue

				else:

					hallucination_msg = """
					Current configuration doesn't match the goal configuration, so the puzzle is not solved yet.
			
					This is the current configuration:
					{}
					{}
					{}
					
					This is the goal configuration:
					{}
					{}
					{}



					Please try again to give me only two different valid next moves possible from only the current configuration that would help in reaching the goal configuration using as few moves as possible.
					Your answer should only be in the format as below:
					1. Move <N> from <src> to <trg>.



					""".format("A = "+str(temp_current_configuration[0]),"B = "+str(temp_current_configuration[1]),"C = "+str(temp_current_configuration[2]), "A = "+str(goal_config[0]),"B = "+str(goal_config[1]),"C = "+str(goal_config[2]))
						

					actor_input.append({
							"role": "assistant",
							"content": outputs[0]["generated_text"][len(prompt):],
						})
						
					actor_input.append({
						"role": "user",
						"content": hallucination_msg,
						})
							
							

					cur_try+=1
					check_flag=1
					continue

			except Exception as e:
				err = f"Error: {str(e)}"

				# if "This model's maximum context length is 32768 tokens" in err:
				# 	print("length of input before and step number>>",len(actor_input),step)
				# 	if max_content_limit_exceed_count==0:
				# 		print("first time for an example")

				# 		actor_input = [{"role": "system","content": "you are an AI assistant",}] +[{"role": "user","content": reduced_prompt,}]  + actor_input[101:] # skip first 50 conversations between user and assistant
				# 	else:
				# 		print("not first time for an example")
				# 		actor_input = [{"role": "system","content": "you are an AI assistant",}] +[{"role": "user","content": reduced_prompt,}]  + actor_input[102:]

				# 	max_content_limit_exceed_count+=1


				print(err)
				# print("Length of input now>>",len(actor_input))
				# time.sleep(120)
				cur_try+=1
				continue

		if len(actor_truncated_response)==0:
			actor_truncated_response = previous_actor_truncated_response




		if len(actor_truncated_response)==2:
			# proposals.append(actor_truncated_response[0])
			# proposals.append(actor_truncated_response[1])


			move_validity1, validity1_response = move_validator_module(temp_current_configuration[0],temp_current_configuration[1],temp_current_configuration[2],actor_truncated_response[0])
			move_validity2, validity2_response = move_validator_module(temp_current_configuration[0],temp_current_configuration[1],temp_current_configuration[2],actor_truncated_response[1])
				
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
				
				This is the current configuration:
				{}
				{}
				{}
				
				This is the goal configuration:
				{}
				{}
				{}

				Please try again to give me only two different valid next moves possible from only the current configuration that would help in reaching the goal configuration using as few moves as possible.
				Your answer should only be in the format as below:
				1. Move <N> from <src> to <trg>.

				""".format(validity2_response,"A = "+str(temp_current_configuration[0]),"B = "+str(temp_current_configuration[1]),"C = "+str(temp_current_configuration[2]), "A = "+str(goal_config[0]),"B = "+str(goal_config[1]),"C = "+str(goal_config[2]))
				num_tries+=1

			elif move_validity1 =='no' and move_validity2 =='yes':
				if actor_truncated_response[1] not in extracted_valid_moves:

					extracted_valid_moves.append(actor_truncated_response[1])
				
				internal_configuration_msg = """
				{} 
				
				This is the current configuration:
				{}
				{}
				{}

				This is the goal configuration:
				{}
				{}
				{}
				

				Please try again to give me only two different valid next moves possible from only the current configuration that would help in reaching the goal configuration using as few moves as possible.
				Your answer should only be in the format as below:
				1. Move <N> from <src> to <trg>.

				""".format(validity1_response,"A = "+str(temp_current_configuration[0]),"B = "+str(temp_current_configuration[1]),"C = "+str(temp_current_configuration[2]), "A = "+str(goal_config[0]),"B = "+str(goal_config[1]),"C = "+str(goal_config[2]))
				num_tries+=1
			else:
				
				
				internal_configuration_msg = """
				{}

				{}
				
				This is the current configuration:
				{}
				{}
				{}
				
				This is the goal configuration:
				{}
				{}
				{}



				Please try again to give me only two different valid next moves possible from only the current configuration that would help in reaching the goal configuration using as few moves as possible.
				Your answer should only be in the format as below:
				1. Move <N> from <src> to <trg>.


				""".format(validity1_response,validity2_response,"A = "+str(temp_current_configuration[0]),"B = "+str(temp_current_configuration[1]),"C = "+str(temp_current_configuration[2]), "A = "+str(goal_config[0]),"B = "+str(goal_config[1]),"C = "+str(goal_config[2]))

				num_tries+=1
		else:
			# proposals.append(actor_truncated_response[0])
			# proposals.append(actor_truncated_response[0])

			move_validity1, validity1_response = move_validator_module(temp_current_configuration[0],temp_current_configuration[1],temp_current_configuration[2],actor_truncated_response[0])
			if move_validity1 =='yes':
				# break
				if actor_truncated_response[0] not in extracted_valid_moves:

					extracted_valid_moves.append(actor_truncated_response[0])

				break
				
				
			else:
				
				internal_configuration_msg = """
				{} 
				
				This is the current configuration:
				{}
				{}
				{}
				

				This is the goal configuration:
				{}
				{}
				{}

				Please try again to give me only two different valid next moves possible from only the current configuration that would help in reaching the goal configuration using as few moves as possible.
				Your answer should only be in the format as below:
				1. Move <N> from <src> to <trg>.

				""".format(validity1_response,"A = "+str(temp_current_configuration[0]),"B = "+str(temp_current_configuration[1]),"C = "+str(temp_current_configuration[2]), "A = "+str(goal_config[0]),"B = "+str(goal_config[1]),"C = "+str(goal_config[2]))
				num_tries+=1
				




		actor_input.append({
		"role": "assistant",
		"content":  outputs[0]["generated_text"][len(prompt):],
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


	return proposals, max_content_limit_exceed_count




def state_predictor_module(state_A,state_B,state_C,move_msg):

	state_predictor_prompt = """

			In this task, you will be presented with three lists labelled A, B, and C. There is a set of numbers distributed among those three lists. You will also be presented with a proposal to move one of the numbers to another list. 
			Your task is to state the configuration that will result from this proposed move. When numbers are moved to a new list, they will always be moved to the rightmost end of that list.


			Here are two examples:
			
			Example 1:

			
			This is the current configuration:
			A = []
			B = [1]
			C = [0, 2]
			
			Proposed move:
			Move 2 from list C to list B.

			Answer:
			A = []
			B = [1, 2]
			C = [0]


			Example 2:

			
			This is the current configuration:
			A = []
			B = [1]
			C = [0, 2]
			
			Proposed move:
			Move 1 from list B to list A.

			Answer:
			A = [1]
			B = []
			C = [0, 2]
			


			Here is the task:

			
			This is the current configuration:
			{}
			{}
			{}
			Proposed move:
			{}.

			Answer:

			""".format("A = "+str(state_A),"B = "+str(state_B),"C = "+str(state_C),move_msg)


	if state_predictor_prompt in predictor_cache:
		return predictor_cache[state_predictor_prompt]


	state_predictor_input = [{
		"role": "system",
		"content": "you are an AI assistant",
	}]

	state_predictor_input.append({
		"role": "user",
		"content": state_predictor_prompt,
	})

	prompt = pipeline.tokenizer.apply_chat_template(
			state_predictor_input, 
			tokenize=False, 
			add_generation_prompt=True
	)

	terminators = [
		pipeline.tokenizer.eos_token_id,
		pipeline.tokenizer.convert_tokens_to_ids("<|eot_id|>")
	]

	outputs = pipeline(
		prompt,
		max_new_tokens=200,
		eos_token_id=terminators,
		do_sample=False
	)
	
	
	print("predictor_response>>>",outputs[0]["generated_text"][len(prompt):])
 
	# print("predictor_response>>",predictor_response.choices[0].message.content)
	
	state_predictor_output = []
	splits = outputs[0]["generated_text"][len(prompt):].split("=")
	for sp in splits:

		if '[' in sp and ']' in sp:

			state_predictor_output.append(json.loads(sp[sp.index('['):sp.index(']')+1]))

	
	# state_predictor_output.append(json.loads(predictor_response.choices[0].message.content.split("\n")[0].split("=")[-1]))
	# state_predictor_output.append(json.loads(predictor_response.choices[0].message.content.split("\n")[1].split("=")[-1]))
	# state_predictor_output.append(json.loads(predictor_response.choices[0].message.content.split("\n")[2].split("=")[-1]))
	# if len(state_predictor_output)==0:
	# 	num_tries+=1
	# 	continue
	if len(state_predictor_output)>3:
		state_predictor_output = state_predictor_output[-3:]
	elif len(state_predictor_output)<3:
		state_predictor_output = [state_A,state_B,state_C]
	
	predictor_cache[state_predictor_prompt]=state_predictor_output
	return state_predictor_output



def state_evaluator_module(state_A,state_B,state_C,goal_config,num_disks):

	state_evaluator_prompt = """Consider the following puzzle problem:

	Problem description:
	- There are three lists labeled A, B, and C.
	- There is a set of numbers distributed among those three lists.
	- You can only move numbers from the rightmost end of one list to the rightmost end of another list.
	Rule #1: You can only move a number if it is at the rightmost end of its current list.
	Rule #2: You can only move a number to the rightmost end of a list if it is larger than the other numbers in that list.
	A move is valid if it satisfies both Rule #1 and Rule #2.
	A move is invalid if it violates either Rule #1 or Rule #2.

	Goal: The goal is to predict the minimum number of valid moves required to reach the goal configuration from the current configuration.


	Here are two examples:

	Example 1:

	This is the current configuration:
	A = [0, 1, 2]
	B = []
	C = []

	This is the goal configuration:
	A = []
	B = []
	C = [0, 1, 2]

	Answer:
	The minimum number of valid moves required to reach the goal configuration from the current configuration is 7.


	Example 2:

	This is the current configuration:
	A = [1, 2]
	B = [0]
	C = []

	This is the goal configuration:
	A = []
	B = []
	C = [0, 1, 2]

	Answer:
	The minimum number of valid moves required to reach the goal configuration from the current configuration is 4.

	What heuristic function can be used to estimate the minimum number of valid moves required to reach the goal configuration from a given current configuration?
	"""

	state_evaluator_input = [{
		"role": "system",
		"content": "you are an AI assistant",
	}]

	state_evaluator_input.append({
		"role": "user",
		"content": state_evaluator_prompt,
	})

	state_evaluator_input.append({
	"role": "assistant",
	"content": """What a fascinating puzzle problem!

	After analyzing the problem, I propose a heuristic function to estimate the minimum number of valid moves required to reach the goal configuration from a given current configuration.

	**Heuristic Function:**

	Let's define a heuristic function `h` that estimates the minimum number of valid moves required to reach the goal configuration. This function will consider the following factors:

	1. **Number of elements out of order**: Count the number of elements in the current configuration that are not in their final position in the goal configuration.
	2. **Maximum number of moves required to move an element to its final position**: For each element, calculate the maximum number of moves required to move it to its final position in the goal configuration.

	The heuristic function `h` can be defined as:

	`h = (number of elements out of order) + (sum of maximum moves required for each element)`

	**Rationale:**

	1. **Number of elements out of order**: This factor encourages the algorithm to focus on moving elements to their final positions. The more elements out of order, the more moves are likely required to reach the goal configuration.
	2. **Maximum number of moves required to move an element to its final position**: This factor takes into account the difficulty of moving each element to its final position. If an element is far from its final position, it will require more moves to reach it.

	**Example Calculations:**

	Let's apply this heuristic function to the two examples:

	**Example 1:**

	Current configuration: A = [0, 1, 2], B = [], C = []
	Goal configuration: A = [], B = [], C = [0, 1, 2]

	* Number of elements out of order: 3 (all elements are out of order)
	* Maximum moves required for each element:
		+ 0: 3 moves (A -> B -> C)
		+ 1: 2 moves (A -> C)
		+ 2: 1 move (A -> C)
	* `h = 3 + (3 + 2 + 1) = 9`

	**Example 2:**

	Current configuration: A = [1, 2], B = [0], C = []
	Goal configuration: A = [], B = [], C = [0, 1, 2]

	* Number of elements out of order: 3 (all elements are out of order)
	* Maximum moves required for each element:
		+ 0: 2 moves (B -> C)
		+ 1: 2 moves (A -> C)
		+ 2: 1 move (A -> C)
	* `h = 3 + (2 + 2 + 1) = 8`

	**Note:** These heuristic values are not exact, but they provide a reasonable estimate of the minimum number of valid moves required to reach the goal configuration. The actual number of moves may be higher or lower, depending on the specific sequence of moves.

	By using this heuristic function, a search algorithm (e.g., A\* search) can efficiently explore the state space and find a near-optimal solution to the puzzle problem.
		"""
		})
	
	internal_configuration_msg = """
	This is the current configuration:
	{}
	{}
	{}
	This is the goal configuration:
	{}
	{}
	{}

	Use the heuristic function to predict the minimum number of valid moves required to reach the goal configuration from the current configuration.


	""".format("A = "+str(state_A),"B = "+str(state_B),"C = "+str(state_C),"A = "+str(goal_config[0]),"B = "+str(goal_config[1]),"C = "+str(goal_config[2]))
	
	if internal_configuration_msg in evaluator_cache:
		return evaluator_cache[internal_configuration_msg]


	state_evaluator_input.append({
		"role": "user",
		"content": internal_configuration_msg,
		})

	

	


	prompt = pipeline.tokenizer.apply_chat_template(
			state_evaluator_input, 
			tokenize=False, 
			add_generation_prompt=True
	)

	terminators = [
		pipeline.tokenizer.eos_token_id,
		pipeline.tokenizer.convert_tokens_to_ids("<|eot_id|>")
	]

	outputs = pipeline(
		prompt,
		max_new_tokens=2000,
		eos_token_id=terminators,
		do_sample=False
	)

	print("evaluator_response>>",outputs[0]["generated_text"][len(prompt):])

	query_msg = """
		Please parse your above response to provide the minimum number of valid moves required to reach the goal configuration from the current configuration according to the heuristic function.

		Please provide only a single integer number after "Answer = "

		"""

	state_evaluator_input.append({
	"role": "assistant",
	"content": outputs[0]["generated_text"][len(prompt):],
	})

	state_evaluator_input.append({
	"role": "user",
	"content": query_msg,
	})


	prompt = pipeline.tokenizer.apply_chat_template(
			state_evaluator_input, 
			tokenize=False, 
			add_generation_prompt=True
	)

	terminators = [
		pipeline.tokenizer.eos_token_id,
		pipeline.tokenizer.convert_tokens_to_ids("<|eot_id|>")
	]

	outputs = pipeline(
		prompt,
		max_new_tokens=200,
		eos_token_id=terminators,
		do_sample=False
	)

	# if 'Move' in gpt_truncated_response and 'from list' in gpt_truncated_response and 'to list' in gpt_truncated_response and (('A' in gpt_truncated_response and 'B' in gpt_truncated_response ) or ('C' in gpt_truncated_response and 'B' in gpt_truncated_response ) or ('A' in gpt_truncated_response and 'C' in gpt_truncated_response )) :
	print("evaluator_parse_response>>",outputs[0]["generated_text"][len(prompt):])


	

		
	
	
	
	
	if "Answer = " in outputs[0]["generated_text"][len(prompt):]:
		evaluator_cache[internal_configuration_msg] = int(outputs[0]["generated_text"][len(prompt):].split("Answer = ")[-1])
		return int(outputs[0]["generated_text"][len(prompt):].split("Answer = ")[-1])
	else:
		if num_disks==3:
			print("random sampling>>>>>")

			rand_value = np.random.randint(1,8)
			evaluator_cache[internal_configuration_msg] = rand_value
			return rand_value

		else:
			print("random sampling>>>>>")
			rand_value = np.random.randint(1,16)
			evaluator_cache[internal_configuration_msg] = rand_value
			return rand_value


	


def rollout_from_2nodes(node1,node2,start_prompt,move_proposals,goal_configuration,max_content_limit_exceed_count,num_disks):


		

	if task_coordination_module(node1,goal_configuration) or task_coordination_module(node2,goal_configuration):

		moves_from_node1 = state_evaluator_module(node1[0],node1[1],node1[2],goal_configuration,num_disks)
		moves_from_node2 = state_evaluator_module(node2[0],node2[1],node2[2],goal_configuration,num_disks)

		if moves_from_node1 < moves_from_node2:
			next_move_chosen_for_system = move_proposals[0]
			next_states = None
			next_next_moves = None
		elif moves_from_node2 < moves_from_node1:
			next_move_chosen_for_system = move_proposals[1]
			next_states = None
			next_next_moves = None
		else:
			next_move_chosen_for_system = move_proposals[np.random.randint(0,2)]
			next_states = None
			next_next_moves = None

		print("target reached at first rollout and move chosen>>>",next_move_chosen_for_system)
		return next_move_chosen_for_system, next_states,next_next_moves

	else:

		internal_configuration_msg = """
		This is the current configuration:
		{}
		{}
		{}

		This is the goal configuration:
		{}
		{}
		{}
		

		Give me only two different valid next moves possible from only the current configuration that would help in reaching the goal configuration using as few moves as possible.
		Your answer should only be in the format as below:
		1. Move <N> from <src> to <trg>.

		""".format("A = "+str(node1[0]),"B = "+str(node1[1]),"C = "+str(node1[2]), "A = "+str(goal_configuration[0]),"B = "+str(goal_configuration[1]),"C = "+str(goal_configuration[2]))


		prompt_state1= start_prompt+ "\n"+move_proposals[0]+ "." +"\n"+internal_configuration_msg
		
		# print("prompt_state1>>>",prompt_state1)

		input = [{
			"role": "system",
			"content": "you are an AI assistant",
		}]

		input.append({
			"role": "user",
			"content": prompt_state1,
		})


		

		
		next_move_proposals1, max_content_limit_exceed_count = actor_module_propose_two_actions(input,node1,goal_configuration,step,max_content_limit_exceed_count)
		print("move proposals from config 1>>",next_move_proposals1)

		


		internal_configuration_msg = """
		This is the current configuration:
		{}
		{}
		{}

		This is the goal configuration:
		{}
		{}
		{}
		
		
		Give me only two different valid next moves possible from only the current configuration that would help in reaching the goal configuration using as few moves as possible.
		Your answer should only be in the format as below:
		1. Move <N> from <src> to <trg>.

		""".format("A = "+str(node2[0]),"B = "+str(node2[1]),"C = "+str(node2[2]), "A = "+str(goal_configuration[0]),"B = "+str(goal_configuration[1]),"C = "+str(goal_configuration[2]))


		prompt_state2= start_prompt+ "\n"+move_proposals[1]+ "." +"\n"+internal_configuration_msg
		
		# print("prompt_state2>>>",prompt_state2)

		input = [{
			"role": "system",
			"content": "you are an AI assistant",
		}]

		input.append({
			"role": "user",
			"content": prompt_state2,
		})


		next_move_proposals2, max_content_limit_exceed_count = actor_module_propose_two_actions(input,node2,goal_configuration,step,max_content_limit_exceed_count)
		
		print("move proposals from config 2>>",next_move_proposals2)

		# print("input now>>>",input)

		node1_1 = state_predictor_module(node1[0], node1[1], node1[2] ,next_move_proposals1[0])
		
		node1_2 = state_predictor_module(node1[0], node1[1], node1[2] ,next_move_proposals1[1])

		print("next next config 1_1>>",node1_1)
		print("next next config 1_2>>",node1_2)


		node2_1 = state_predictor_module(node2[0], node2[1], node2[2] ,next_move_proposals2[0])
		
		node2_2 = state_predictor_module(node2[0], node2[1], node2[2] ,next_move_proposals2[1])

		print("next next config 2_1>>",node2_1)
		print("next next config 2_2>>",node2_2)


		moves_from_node1_1 = state_evaluator_module(node1_1[0],node1_1[1],node1_1[2],goal_configuration,num_disks)
		moves_from_node1_2 = state_evaluator_module(node1_2[0],node1_2[1],node1_2[2],goal_configuration,num_disks)
		
		moves_from_node2_1 = state_evaluator_module(node2_1[0],node2_1[1],node2_1[2],goal_configuration,num_disks)
		moves_from_node2_2 = state_evaluator_module(node2_2[0],node2_2[1],node2_2[2],goal_configuration,num_disks)
		
		four_configs_moves = []
		four_configs_moves.append(moves_from_node1_1)
		four_configs_moves.append(moves_from_node1_2)
		four_configs_moves.append(moves_from_node2_1)
		four_configs_moves.append(moves_from_node2_2)

		min_moves = min(moves_from_node1_1, moves_from_node1_2, moves_from_node2_1,moves_from_node2_2)

		index_min_moves = []
		for idx,config_moves in enumerate(four_configs_moves):
			if config_moves == min_moves:
				index_min_moves.append(idx)

		min_move_index_chosen = np.random.choice(index_min_moves)
		if min_move_index_chosen>1:
			next_move_chosen_for_system = move_proposals[1]
			next_states = [node2_1,node2_2]
			next_next_moves = next_move_proposals2
		else:
			next_move_chosen_for_system = move_proposals[0]
			next_states = [node1_1,node1_2]
			next_next_moves = next_move_proposals1


		print("num moves from 4 configs, move chosen>>>",moves_from_node1_1,moves_from_node1_2,moves_from_node2_1,moves_from_node2_2,next_move_chosen_for_system)
		print("next states>>>",next_states)
		print("next next moves>>>",next_next_moves)
		
		return next_move_chosen_for_system, next_states,next_next_moves


def subgoal_module(state_A,state_B,state_C,goal_config,num_disks):
	subgoal_prompt = """Consider the following puzzle problem:
			
	Problem description:
	- There are three lists labeled A, B, and C.
	- There is a set of numbers distributed among those three lists.
	- You can only move numbers from the rightmost end of one list to the rightmost end of another list.
	
	Rule #1: You can only move a number if it is at the rightmost end of its current list.
	Rule #2: You can only move a number to the rightmost end of a list if it is larger than the other numbers in that list.
	
	
	A move is valid if it satisfies both Rule #1 and Rule #2.
	A move is invalid if it violates either Rule #1 or Rule #2.

	Goal: The goal is to generate a single subgoal from the current configuration, that helps in reaching the goal configuration using minimum number of moves.
	
	To generate subgoal use the goal recursion strategy. First if the smallest number isn't at the correct position in list C, then set the subgoal of moving the smallest number to its correct position in list C.
	But before that, the numbers larger than the smallest number and present in the same list as the smallest number must be moved to a list other than list C. 
	This subgoal is recursive because in order to move the next smallest number to the list other than list C, the numbers larger than the next smallest number and present in the same list as the next smallest number must be moved to a list different from the previous other list and so on.
	
	Note in the subgoal configuration all numbers should always be in ascending order in all the three lists.

	Here are two examples:
	
	Example 1:
	
	This is the current configuration:
	A = [0,1]
	B = [2]
	C = []
	
	This is the goal configuration:
	A = []
	B = []
	C = [0, 1, 2]

	Answer:
	I need to move 0 from list A to list C. 
	Step 1. Find the numbers to the right of 0 in list A. There is 1 to the right of 0.
	Step 2. Find the numbers larger than 0 in list C. There are none.
	I will move the numbers found in Step 1 and Step 2 to list B. Hence I will move 1 from list A to list B. Also numbers should be in ascending order in list B.
	Subgoal:
	A = [0]
	B = [1, 2]
	C = []
	
	Example 2:
	
	This is the current configuration:
	A = [1]
	B = [0]
	C = [2]
	
	This is the goal configuration:
	A = []
	B = []
	C = [0, 1, 2]

	Answer:
	I need to move 0 from list B to list C. 
	Step 1. Find the numbers to the right of 0 in list B. There are none.
	Step 2. Find the numbers larger than 0 in list C. There is 2 which is larger than 0.
	I will move the numbers found in Step 1 and Step 2 to list A. Hence, I will move 2 from list C to list A. Also numbers should be in ascending order in list A.
	Subgoal:
	A = [1, 2]
	B = [0]
	C = []    
	  
	

	Here is the task:   
	
	This is the current configuration:
	{}
	{}
	{}
	
	
	This is the goal configuration:
	{}
	{}
	{}
	
	Answer:


	
	""".format("A = "+str(state_A),"B = "+str(state_B),"C = "+str(state_C), "A = "+str(goal_config[0]),"B = "+str(goal_config[1]),"C = "+str(goal_config[2]))


	subgoal_input = [{
				"role": "system",
				"content": "you are an AI assistant",
			}]

	subgoal_input.append({
		"role": "user",
		"content": subgoal_prompt,
	})

	prompt = pipeline.tokenizer.apply_chat_template(
			subgoal_input, 
			tokenize=False, 
			add_generation_prompt=True
	)

	terminators = [
		pipeline.tokenizer.eos_token_id,
		pipeline.tokenizer.convert_tokens_to_ids("<|eot_id|>")
	]

	outputs = pipeline(
		prompt,
		max_new_tokens=1000,
		eos_token_id=terminators,
		do_sample=False
	)


	

		
	
			
	print("Subgoal generated>>",outputs[0]["generated_text"][len(prompt):])
	subgoal = []
	splits = outputs[0]["generated_text"][len(prompt):].split("=")
	for sp in splits:

		if '[' in sp and ']' in sp:

			subgoal.append(json.loads(sp[sp.index('['):sp.index(']')+1]))

		

	if len(subgoal)>3:
		subgoal = subgoal[-3:]
		if task_coordination_module(subgoal ,[state_A,state_B,state_C]):
			if num_disks==3:

				subgoal = [[],[],[0,1,2]]
			else:
				subgoal = [[],[],[0,1,2,3]]

	elif (len(subgoal)==0):
 
		if num_disks==3:

			subgoal = [[],[],[0,1,2]]
		else:
			subgoal = [[],[],[0,1,2,3]]

	else:
		if task_coordination_module(subgoal ,[state_A,state_B,state_C]):
			if num_disks==3:

				subgoal = [[],[],[0,1,2]]
			else:
				subgoal = [[],[],[0,1,2,3]]



		
	return subgoal



	
# num_input_tokens = 0 
# num_output_tokens = 0
icl_examples = [ 3, 22]
for run_no in range(1,2):
	print("run number>>",run_no)

	# num_validator_calls = 0 
	# num_evaluator_calls = 0 
	# num_predictor_calls = 0 
	# num_subgoal_calls = 0 
	# num_coordinator_calls = 0 
	# num_actor_calls = 0
	# num_validator_input_tokens = 0
	# num_validator_output_tokens = 0
	# num_evaluator_input_tokens = 0
	# num_evaluator_output_tokens = 0
	# num_predictor_input_tokens = 0
	# num_predictor_output_tokens = 0
	# num_subgoal_input_tokens = 0
	# num_subgoal_output_tokens = 0
	# num_coordinator_input_tokens = 0
	# num_coordinator_output_tokens = 0
	# num_actor_input_tokens = 0
	# num_actor_output_tokens = 0
	for i in range(26):
		if (i+1) not in icl_examples:
			start_time = time.time()

			num_validator_input_tokens = []
			num_validator_output_tokens = []
			validator_response_time = []
			num_evaluator_input_tokens = []
			num_evaluator_output_tokens = []
			evaluator_response_time = []
			num_predictor_input_tokens = []
			num_predictor_output_tokens = []
			predictor_response_time = []
			num_subgoal_input_tokens = []
			num_subgoal_output_tokens = []
			subgoal_response_time = []
			num_coordinator_input_tokens = []
			num_coordinator_output_tokens = []
			coordinator_response_time = []
			num_actor_input_tokens = []
			num_actor_output_tokens = []
			actor_response_time = []

			A=all_As[i] 

			B=all_Bs[i]

			C=all_Cs[i]
			# A = [2]
			# B = [1, 3]
			# C = [0]
			num_disks = max(A+B+C)+1
			
			start_configuration = [A,B,C]
			if num_disks==3:
				num_steps = 10

				final_target_configuration = [[],[],[0, 1, 2]]
			else:
				num_steps = 20
				final_target_configuration = [[],[],[0, 1, 2, 3]]
					

				
			subgoal_configuration = subgoal_module(A, B, C,final_target_configuration,num_disks)
			print("subgoal generated>>>",subgoal_configuration)
			goal_config = subgoal_configuration

			next_state_prediction = deepcopy(start_configuration)
			current_configuration = deepcopy(start_configuration)

			count = 0
			



			root_prompt = """Consider the following puzzle problem:
			
			Problem description:
			- There are three lists labeled A, B, and C.
			- There is a set of numbers distributed among those three lists.
			- You can only move numbers from the rightmost end of one list to the rightmost end of another list.

			Rule #1: You can only move a number if it is at the rightmost end of its current list.
			Rule #2: You can only move a number to the rightmost end of a list if it is larger than the other numbers in that list.

			A move is valid if it satisfies both Rule #1 and Rule #2.
			A move is invalid if it violates either Rule #1 or Rule #2.
			
			Goal: The goal is to end up in the goal configuration using minimum number of moves.

			Here are two examples:

			{}

			Here is the task:

			This is the starting configuration:
			{}
			{}
			{}
			This is the goal configuration:
			{}
			{}
			{}

			Give me only two different valid next moves possible from only the starting configuration that would help in reaching the goal configuration using as few moves as possible. 
			Your answer should only be in the format as below:
			1. Move <N> from <src> to <trg>.

			""".format(standard_prompt,"A = "+str(A),"B = "+str(B),"C = "+str(C),"A = "+str(subgoal_configuration[0]),"B = "+str(subgoal_configuration[1]),"C = "+str(subgoal_configuration[2]))


			
			
			print("starting prompt>>",root_prompt)
			external_environment_prompt = deepcopy(root_prompt)

			input = [{
					"role": "system",
					"content": "you are an AI assistant",
				}]

			input.append({
				"role": "user",
				"content": root_prompt,
			})

			


			flag=0
			total_reward = 0
			step = 0
			num_tries=0
			max_content_limit_exceed_count = 0
			depth_flag=0
			next_states = None

			for step in range(num_steps):
				
				first_temp_current_configuration = deepcopy(next_state_prediction)

				print("step>>",step)
				print("first (current) config>>",first_temp_current_configuration)

				if step ==0 or next_states is None:

					
					move_proposals, max_content_limit_exceed_count = actor_module_propose_two_actions(input,first_temp_current_configuration,goal_config,step,max_content_limit_exceed_count)
					print("move proposals>>",move_proposals)
					# print("input now>>>",input)
						
					
					
					next_temp_current_configuration1 = state_predictor_module(first_temp_current_configuration[0], first_temp_current_configuration[1], first_temp_current_configuration[2] ,move_proposals[0])
					next_temp_current_configuration2 = state_predictor_module(first_temp_current_configuration[0], first_temp_current_configuration[1], first_temp_current_configuration[2] ,move_proposals[1])

					print("next config 1>>",next_temp_current_configuration1)
					print("next config 2>>",next_temp_current_configuration2)


				

					next_move_chosen_for_system, next_states, next_next_moves  = rollout_from_2nodes(next_temp_current_configuration1,next_temp_current_configuration2,root_prompt,move_proposals,goal_config,max_content_limit_exceed_count,num_disks)

					
				else:
					next_move_chosen_for_system, next_states, next_next_moves  = rollout_from_2nodes(next_states[0],next_states[1],root_prompt,next_next_moves,goal_config,max_content_limit_exceed_count,num_disks)


				

				# print("error monitor gpt full response>>",validator_response.choices[0].message.content)
				# print("move_validity>>",move_validity)
				
				
				
				no_to_move = int(next_move_chosen_for_system.split(" ")[1])
				source_list = next_move_chosen_for_system.split(" ")[3]
				target_list = next_move_chosen_for_system.split(" ")[5]
				# print(gpt_response,no_to_move,source_list,target_list)
				
				total_reward+=-1
				response_flag =0
				if no_to_move not in current_configuration[char_int_mapping[source_list]]:
					user_message = next_move_chosen_for_system+"." + "\nInvalid move because {} is not in {}. You get a penalty of -10. For each move you get an additional penalty of -1.".format(no_to_move,source_list)
					reward_message = "Invalid move because {} is not in {}. You get a penalty of -10. For each move you get an additional penalty of -1.".format(no_to_move,source_list)
					response_flag =1
				else:
					if current_configuration[char_int_mapping[source_list]][-1]!= no_to_move:
						user_message = next_move_chosen_for_system + "." + "\nInvalid move because it violates Rule #1. You get a penalty of -10. For each move you get an additional penalty of -1."
						reward_message = "Invalid move because it violates Rule #1. You get a penalty of -10. For each move you get an additional penalty of -1."
						response_flag =1
					else:
						if len(current_configuration[char_int_mapping[target_list]]):
							max_target_list = max(current_configuration[char_int_mapping[target_list]])
						else:
							max_target_list = -1

						if no_to_move < max_target_list:
							user_message = next_move_chosen_for_system +"." + "\nInvalid move because it violates Rule #2. You get a penalty of -10. For each move you get an additional penalty of -1."
							reward_message = "Invalid move because it violates Rule #2. You get a penalty of -10. For each move you get an additional penalty of -1."
							response_flag=1
						else:
							user_message = next_move_chosen_for_system+'.'+'\nFor each move you get a penalty of -1.'
							reward_message = "For each move you get a penalty of -1."
							current_configuration[char_int_mapping[source_list]].pop()
							current_configuration[char_int_mapping[target_list]].append(no_to_move)

				if response_flag==1:
					total_reward+=-10

				next_state_prediction = state_predictor_module(first_temp_current_configuration[0], first_temp_current_configuration[1], first_temp_current_configuration[2] ,next_move_chosen_for_system)
					
				if task_coordination_module(next_state_prediction,final_target_configuration):
					flag=1

					internal_configuration_msg = """This is the current configuration:
					{}
					{}
					{}

					This is the goal configuration:
					{}
					{}
					{}

					Give me only two different valid next moves possible from only the current configuration that would help in reaching the goal configuration using as few moves as possible.
					Your answer should only be in the format as below:
					1. Move <N> from <src> to <trg>.

					""".format("A = "+str(next_state_prediction[0]),"B = "+str(next_state_prediction[1]),"C = "+str(next_state_prediction[2]),"A = "+str(final_target_configuration[0]),"B = "+str(final_target_configuration[1]),"C = "+str(final_target_configuration[2]))

					
					configuration_msg = """This is the current configuration:
					{}
					{}
					{}

					This is the goal configuration:
					{}
					{}
					{}

					Give me only two different valid next moves possible from only the current configuration that would help in reaching the goal configuration using as few moves as possible.
					Your answer should only be in the format as below:
					1. Move <N> from <src> to <trg>.

					""".format("A = "+str(current_configuration[0]),"B = "+str(current_configuration[1]),"C = "+str(current_configuration[2]),"A = "+str(final_target_configuration[0]),"B = "+str(final_target_configuration[1]),"C = "+str(final_target_configuration[2]))


					root_prompt+="\n"+next_move_chosen_for_system+"."+"\n"+internal_configuration_msg

					print("internal configuration message>>>",internal_configuration_msg)
					# print("external feedback>>",reward_message+"\n"+configuration_msg)
					external_environment_prompt+="\n"+user_message +"\n"+configuration_msg

					print("external feedback>>",user_message+"\n"+configuration_msg)
				


					
					
					if current_configuration==final_target_configuration:
						total_reward+=100

					test_dir = './logs/'
					check_path(test_dir)
					output_dir = test_dir + 'llama3 70b map solve toh/'
					check_path(output_dir)
					output_dir+='run{}/'.format(run_no)
					check_path(output_dir)


					with open(output_dir+'problem{}_new.log'.format(i+1), 'a') as w:
						w.write(root_prompt +'\n'+"Solved problem in {} steps. Total reward = {}".format(step+1,total_reward))

					
					with open(output_dir+'problem{}_new.log'.format(i+1), 'a') as w:
						w.write("External environment feedback>>>>\n"+external_environment_prompt + '\n'+"Solved problem in {} steps. Total reward = {}".format(step+1,total_reward))


					break

				elif task_coordination_module(next_state_prediction,subgoal_configuration):
					print("subgoal reached>>>>")
					subgoal_flag=1
					goal_config = final_target_configuration

					internal_configuration_msg = """This is the current configuration:
					{}
					{}
					{}

					This is the goal configuration:
					{}
					{}
					{}

					Give me only two different valid next moves possible from only the current configuration that would help in reaching the goal configuration using as few moves as possible.
					Your answer should only be in the format as below:
					1. Move <N> from <src> to <trg>.

					""".format("A = "+str(next_state_prediction[0]),"B = "+str(next_state_prediction[1]),"C = "+str(next_state_prediction[2]),"A = "+str(goal_config[0]),"B = "+str(goal_config[1]),"C = "+str(goal_config[2]))

					
					configuration_msg = """This is the current configuration:
					{}
					{}
					{}

					This is the goal configuration:
					{}
					{}
					{}

					Give me only two different valid next moves possible from only the current configuration that would help in reaching the goal configuration using as few moves as possible.
					Your answer should only be in the format as below:
					1. Move <N> from <src> to <trg>.

					""".format("A = "+str(current_configuration[0]),"B = "+str(current_configuration[1]),"C = "+str(current_configuration[2]),"A = "+str(goal_config[0]),"B = "+str(goal_config[1]),"C = "+str(goal_config[2]))


					root_prompt+="\n"+next_move_chosen_for_system+"."+"\n"+internal_configuration_msg

					print("internal configuration message>>>",internal_configuration_msg)
					# print("external feedback>>",reward_message+"\n"+configuration_msg)
					external_environment_prompt+="\n"+user_message +"\n"+configuration_msg

					print("external feedback>>",user_message+"\n"+configuration_msg)
				
				

				
					input = [{
						"role": "system",
						"content": "you are an AI assistant",
					}]

					input.append({
						"role": "user",
						"content": root_prompt,
					})


				else:

					internal_configuration_msg = """This is the current configuration:
					{}
					{}
					{}

					This is the goal configuration:
					{}
					{}
					{}

					Give me only two different valid next moves possible from only the current configuration that would help in reaching the goal configuration using as few moves as possible.
					Your answer should only be in the format as below:
					1. Move <N> from <src> to <trg>.

					""".format("A = "+str(next_state_prediction[0]),"B = "+str(next_state_prediction[1]),"C = "+str(next_state_prediction[2]),"A = "+str(goal_config[0]),"B = "+str(goal_config[1]),"C = "+str(goal_config[2]))

					
					configuration_msg = """This is the current configuration:
					{}
					{}
					{}

					This is the goal configuration:
					{}
					{}
					{}

					Give me only two different valid next moves possible from only the current configuration that would help in reaching the goal configuration using as few moves as possible.
					Your answer should only be in the format as below:
					1. Move <N> from <src> to <trg>.

					""".format("A = "+str(current_configuration[0]),"B = "+str(current_configuration[1]),"C = "+str(current_configuration[2]),"A = "+str(goal_config[0]),"B = "+str(goal_config[1]),"C = "+str(goal_config[2]))


					root_prompt+="\n"+next_move_chosen_for_system+"."+"\n"+internal_configuration_msg

					print("internal configuration message>>>",internal_configuration_msg)
					# print("external feedback>>",reward_message+"\n"+configuration_msg)
					external_environment_prompt+="\n"+user_message +"\n"+configuration_msg

					print("external feedback>>",user_message+"\n"+configuration_msg)
				
				

				
					input = [{
						"role": "system",
						"content": "you are an AI assistant",
					}]

					input.append({
						"role": "user",
						"content": root_prompt,
					})

					
					
				

				
				

				
				
			

					# print("error monitor feedback>>>",validator_response.choices[0].message.content + "\n"+configuration_msg)

			if flag==0:
				test_dir = './logs/'
				check_path(test_dir)
				output_dir = test_dir + 'llama3 70b map solve toh/'
				check_path(output_dir)
				output_dir+='run{}/'.format(run_no)
				check_path(output_dir)

				with open(output_dir+'problem{}_new.log'.format(i+1), 'a') as w:
					w.write(root_prompt +'\n'+"Timed out. Couldn't solve problem in {} steps. Total reward = {}".format(num_steps,total_reward))

				with open(output_dir+'problem{}_new.log'.format(i+1), 'a') as w:
						w.write("\nExternal environment feedback>>>>\n"+external_environment_prompt +'\n'+"Timed out. Couldn't solve problem in {} steps. Total reward = {}".format(num_steps,total_reward))

			
			end_time = time.time()
			
			print("done solving problem {}".format(i+1))

