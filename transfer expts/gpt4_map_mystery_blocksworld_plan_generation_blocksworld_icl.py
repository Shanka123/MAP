import openai

from copy import deepcopy
import time
import json
import os
import argparse
import re
from tqdm import tqdm
from openai import AzureOpenAI





def check_path(path):
	if not os.path.exists(path):
		os.mkdir(path)



parser = argparse.ArgumentParser()

parser.add_argument
parser.add_argument('--output_dir',type=str, help='directory name where output log files will be stored', required= True)

args = parser.parse_args()
print(args)


def move_validator_module(current_state,action):

	move_validator_prompt= """
	I am playing with a set of blocks where I need to arrange the blocks into stacks. Here are the actions I can do

	Pick up a block
	Unstack a block from on top of another block
	Put down a block
	Stack a block on top of another block

	I have the following restrictions on my actions:
	I can only pick up or unstack one block at a time.
	I can only pick up or unstack a block if my hand is empty.
	I can only pick up a block if the block is on the table and the block is clear. A block is clear if the block has no other blocks on top of it and if the block is not picked up.
	I can only unstack a block from on top of another block if the block I am unstacking was really on top of the other block.
	I can only unstack a block from on top of another block if the block I am unstacking is clear.
	Once I pick up or unstack a block, I am holding the block.
	I can only put down a block that I am holding.
	I can only stack a block on top of another block if I am holding the block being stacked.
	I can only stack a block on top of another block if the block onto which I am stacking the block is clear.
	Once I put down or stack a block, my hand becomes empty.
	Once you stack a block on top of a second block, the second block is no longer clear.


	Goal: The goal is to check whether the action when taken on the current state satisfies or violates the restrictions and based on that if it is a valid or invalid move.

	Here are two examples:

	Example 1:

	Current state: 
	As initial conditions I have that, the red block is clear, I am holding the orange block, the blue block is clear, the blue block is on the table, the yellow block is clear, the yellow block is on the table, the red block is on the table.


	Action: 
	pick up the red block.

	Answer: 
	To perform pick up red block, the following facts need to be true: the hand is empty, the red block is on the table, the red block is clear. Based on the current state, I am holding the orange block, so the hand is empty is false. Hence, pick up red block is an invalid action.


	Example 2:

	Current state:
	As initial conditions I have that, the red block is clear, the yellow block is clear, the hand is empty, the red block is on top of the blue block, the yellow block is on top of the orange block, the blue block is on the table and the orange block is on the table.

	Action:
	unstack the yellow block from on top of the orange block.


	Answer:
	To perform unstack the yellow block from on top of the orange block, the following facts need to be true: the hand is empty, the yellow block is on top of the orange block, the yellow block is clear. Based on the current state, all the facts are true. Hence, unstack the yellow block from on top of the orange block is a valid action.


	Here is the task:

	I am playing with a set of objects. Here are the actions I can do:

	Attack object x
	Feast object x from object y
	Succumb object x
	Overcome object x from object y

	I have the following restrictions on my actions:
    To perform Attack object x action, the following facts need to be true: Province object x, Planet object x, Harmony.
    To perform Succumb object x action, the following facts need to be true: Pain object x.
    To perform Overcome object x from object y action, the following needs to be true: Province object y, Pain object x.
    To perform Feast object x from object y action, the following needs to be true: Object x Craves object y, Province object x, Harmony.
	   
	Goal: The goal is to check whether the action when taken on the current state satisfies or violates the restrictions and based on that if it is a valid or invalid move.

	
	Current state:
	{}

	Action:
	{}.

	Check each of the facts which needs to be true for the action to be valid. If any of the facts isn't true the action is invalid.



	""".format(current_state,action)

	move_validator_input = [{
	    "role": "system",
	    "content": "you are an AI assistant",
	}]

	move_validator_input.append({
	    "role": "user",
	    "content": move_validator_prompt,
	})

	another_cur_try = 0
	while another_cur_try <10:
		try:
			time1 = time.time()
			validator_response= client.chat.completions.create(model=deployment_name, messages=move_validator_input,temperature=0.0,top_p = 0,max_tokens=1000)
			

			

			time2 = time.time()
			another_cur_try+=1
			
			# global num_validator_input_tokens
			# global num_validator_output_tokens
			# global validator_response_time
			# num_validator_calls+=1
			# num_validator_input_tokens.append(validator_response["usage"]["prompt_tokens"])
			# num_validator_output_tokens.append(validator_response["usage"]["completion_tokens"])
			# validator_response_time.append(time2-time1)

			char_list_response = validator_response.choices[0].message.content.split('\n')[-1].replace(".","").split(" ")
			if 'invalid' in char_list_response or 'Invalid' in char_list_response or 'not valid' in char_list_response or 'not a valid' in char_list_response :
				move_validity = 'no'
			else:
				move_validity = 'yes'

			

					
			# if 'Move' in gpt_truncated_response and 'from list' in gpt_truncated_response and 'to list' in gpt_truncated_response and (('A' in gpt_truncated_response and 'B' in gpt_truncated_response ) or ('C' in gpt_truncated_response and 'B' in gpt_truncated_response ) or ('A' in gpt_truncated_response and 'C' in gpt_truncated_response )) :

			break

		except Exception as e:
			err = f"Error: {str(e)}"
			print(err)
			time.sleep(120)
			
			continue
	print("validator response>>>",validator_response.choices[0].message.content)
	print("validity>>>",move_validity)
	return move_validity, validator_response.choices[0].message.content




def state_predictor_module(current_state,action):

	state_predictor_prompt= """

	I am playing with a set of blocks where I need to arrange the blocks into stacks. Here are the actions I can do

	Pick up a block
	Unstack a block from on top of another block
	Put down a block
	Stack a block on top of another block

	I have the following restrictions on my actions:
	Once I pick up or unstack a block, I am holding the block.
	Once I put down or stack a block, my hand becomes empty.
	Once you stack a block on top of a second block, the second block is no longer clear.


	Goal: The goal is to only predict the next state that results after taking the action at the current state.


	Here are three examples:

	Example 1:

	Current state:
	As initial conditions I have that, the red block is clear, the blue block is clear, the yellow block is clear, the hand is empty, the blue block is on top of the orange block, the red block is on the table, the orange block is on the table and the yellow block is on the table.


	Action:
	unstack the blue block from on top of the orange block.

    Once unstack the blue block from on top of the orange block is performed, the following facts will be true: I am holding the blue block, the orange block is clear
	Once unstack the blue block from on top of the orange block is performed, the following facts will be false: the hand is empty, the blue block is clear
    Next state:
	As initial conditions I have that, the red block is clear, I am holding the blue block, the yellow block is clear, the orange block is clear, the red block is on the table, the orange block is on the table and the yellow block is on the table.

	Example 2:

	Current state:
	As initial conditions I have that, the red block is clear, the blue block is in my hand, the yellow block is clear, the orange block is clear, the red block is on the table, the orange block is on the table and the yellow block is on the table.

	Action:
	put down the blue block.

	Once put down the blue block is performed, the following facts will be true: the hand is empty, the blue block is clear, the blue block is on the table
    Once put down the blue block is performed, the following facts will be false: I am holding the blue block
	Next state:
	As initial conditions I have that, the hand is empty, the red block is clear, the blue block is clear, the yellow block is clear, the orange block is clear, the red block is on the table, the blue block is on the table, the orange block is on the table and the yellow block is on the table.
    
    Example 3:

	Current state:
	As initial conditions I have that, the red block is clear, I am holding the orange block, the blue block is clear, the blue block is on the table, the yellow block is clear, the yellow block is on the table, the red block is on the table.
    
	Action:
	stack the orange block on top of the yellow block.

	Once stack the orange block on top of the yellow block is performed, the following facts will be true: the hand is empty, the orange block is on top of the yellow block, the orange block is clear
    Once stack the orange block on top of the yellow block is performed, the following facts will be false: I am holding the orange block, the yellow block is clear
	Next state:
	As initial conditions I have that, the red block is clear, the hand is empty, the blue block is clear, the blue block is on the table, the orange block is on top of the yellow block, the orange block is clear, the red block is on the table, the yellow block is on the table.




	Here is the task:

	I am playing with a set of objects. Here are the actions I can do:

	Attack object x
	Feast object x from object y
	Succumb object x
	Overcome object x from object y

	I have the following restrictions on my actions:
 
    Once Attack object x action is performed the following facts will be true: Pain object x.
    Once Attack object x action is performed the following facts will be false: Province object x, Planet object x, Harmony.
    
    Once Succumb object x action is performed the following facts will be true: Province object x, Planet object x, Harmony.    
    Once Succumb object x action is performed the following facts will be false: Pain object x.
   
    Once Overcome object x from object y action is performed the following will be true: Harmony, Province object x, Object x Craves object y.
    Once Overcome object x from object y action is performed the following will be false: Province object y, Pain object x.
   
    Once Feast object x from object y action is performed the following will be true: Pain object x, Province object y.
    Once Feast object x from object y action is performed the following will be false: Object x Craves object y, Province object x, Harmony.


	Goal: The goal is to only predict the next state that results after taking the action at the current state.


	

	Current state:
	{}

	Action:
	{}.

	First analyse the facts that will be true and false once the action is performed. Then please provide the next state that results after taking the action at the current state, after adding the facts that will be true and removing the facts that will be false in the following format only: “Next state: < >”.

	""".format(current_state,action)

	state_predictor_input = [{
		"role": "system",
		"content": "you are an AI assistant",
	}]

	state_predictor_input.append({
		"role": "user",
		"content": state_predictor_prompt,
	})

	cur_try=0
	while cur_try<10:

		try:
			time1 = time.time()

			predictor_response= client.chat.completions.create(model=deployment_name, messages=state_predictor_input,temperature=0.0,top_p = 0,max_tokens=1000)
			

			
			time2=time.time()

			# global num_predictor_calls
			
			# num_predictor_calls+=1
			
			break

		except Exception as e:
			err = f"Error: {str(e)}"
			print(err)
			time.sleep(120)
			cur_try+=1
			continue

	print("predictor_response>>",predictor_response.choices[0].message.content)
	
	# state_predictor_output.append(json.loads(predictor_response.choices[0].message.content.split("\n")[0].split("=")[-1]))
	# state_predictor_output.append(json.loads(predictor_response.choices[0].message.content.split("\n")[1].split("=")[-1]))
	# state_predictor_output.append(json.loads(predictor_response.choices[0].message.content.split("\n")[2].split("=")[-1]))
	return predictor_response.choices[0].message.content.split("Next state:")[-1].replace("”","").strip()




def task_coordination_module(current_state,goal):

	task_coordination_prompt= """

	You will be a given a current state and the goal, and your task is to say whether the goal is achieved in the current state.

	Here are two examples:

	Example 1:

	Current state:
	As initial conditions I have that, the red block is clear, the blue block is clear, the yellow block is clear, the hand is empty, the blue block is on top of the orange block, the red block is on the table, the orange block is on the table and the yellow block is on the table.
	
    Goal:
	My goal is to have that the orange block is on top of the blue block.

	Answer: 
	Currently the blue block is on top of the orange block. However my goal is to have the orange block is on top of the blue block. Hence the goal is not achieved in the current state. Hence no. 

	Example 2:

	Current state:
	As initial conditions I have that, the blue block is clear, the hand is empty, the yellow block is on top of the red block, the red block is on top of the orange block, the yellow block is clear, the blue block is on the table and the orange block is on the table.

	Goal:
	My goal is to have that the red block is on top of the orange block and the yellow block is on top of the red block.

	Answer:
	Currently the yellow block is on top of the red block, the red block is on top of the orange block. However my goal is to have the red block is on top of the orange block and the yellow block is on top of the red block. Hence the goal is achieved in the current state. Hence yes. 

	Here is the task:

	Current state:
	{} 

	Goal:
	{}

	First check whether the goal has been achieved in the current state. Then provide your answer according to the format “Answer: < yes or no >”. 


	""".format(current_state,goal)


	task_coordination_input = [{
				"role": "system",
				"content": "you are an AI assistant",
			}]

	task_coordination_input.append({
		"role": "user",
		"content": task_coordination_prompt,
	})

	cur_try=0
	while cur_try<10:

		try:
			time1=time.time()

			task_coordination_response = client.chat.completions.create(model=deployment_name, messages=task_coordination_input,temperature=0.0,top_p = 0,max_tokens=1000)
			

			
			time2=time.time()

			

			# num_coordinator_calls+=1

			print("coordinator response>>>",task_coordination_response.choices[0].message.content)
			extracted_response = task_coordination_response.choices[0].message.content.split("Answer:")[-1]
			
			if "yes" in extracted_response or "Yes" in extracted_response:
				

				
				match_flag=1
			else:
				match_flag=0
				
			
			print("coordinator extracted response and match flag>>>",extracted_response,match_flag)
			break

		except Exception as e:
			err = f"Error: {str(e)}"
			print(err)
			time.sleep(60)
			cur_try+=1
			continue

	return match_flag


def actor_module_propose_action(previous_move,actor_input,temp_current_configuration,goal):


	num_tries = 0

	while num_tries < 10:
		cur_try = 0
		check_flag = 0
		break_flag = 0 
		while cur_try <10:
			try:
				if check_flag==1:
					
					actor_response = client.chat.completions.create(model=deployment_name, messages=actor_input,temperature=0.1*cur_try,max_tokens=200)
			

					

					# num_input_tokens+=actor_response["usage"]["prompt_tokens"]
					# num_output_tokens+=actor_response["usage"]["completion_tokens"]

				else:
					actor_response = client.chat.completions.create(model=deployment_name, messages=actor_input,temperature=0.0,top_p=0,max_tokens=200)
			
					

					# num_input_tokens+=actor_response["usage"]["prompt_tokens"]
					# num_output_tokens+=actor_response["usage"]["completion_tokens"]


				
				
				print("actor_response>>",actor_response.choices[0].message.content)
				
				

				
				start = actor_response.choices[0].message.content.index( "[START]" ) + len( "[START]" )
				end = actor_response.choices[0].message.content.index( "[END]", start )
				actor_truncated_response = actor_response.choices[0].message.content[start:end].replace('.','').strip()
				print("actor truncated response and length>>",actor_truncated_response, len(actor_truncated_response))
				if len(actor_truncated_response)==28 or len(actor_truncated_response)==16 or len(actor_truncated_response)==15 or len(actor_truncated_response)==31:

					break_flag = 1
					break

					


				else:
					

					cur_try+=1
					check_flag =1
					# print("move response not found for problem {}, step {}. Here is the original full response>> {}".format(i+1,step,response.choices[0].message.content))
					continue
				# if 'Move' in gpt_truncated_response and 'from list' in gpt_truncated_response and 'to list' in gpt_truncated_response and (('A' in gpt_truncated_response and 'B' in gpt_truncated_response ) or ('C' in gpt_truncated_response and 'B' in gpt_truncated_response ) or ('A' in gpt_truncated_response and 'C' in gpt_truncated_response )) :
				
				# print("configuration>>",current_configuration)
				# print("gpt response>>",gpt_truncated_response)
			

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
				if "substring not found" in err:

					actor_input.append({
					"role": "assistant",
					"content": actor_response.choices[0].message.content,
					})

					internal_configuration_msg = """
					You didn't provide the next action in between a [START] and a [END] token.

					Current state:
					{}

					Goal:
					{}

					Please try again to give me only the next action possible from the current state that would help in achieving the goal. 
					Please provide the next action in between a [START] and a [END] token.


					""".format(temp_current_configuration,goal)


					actor_input.append({
					"role": "user",
					"content": internal_configuration_msg,
				})

				print(err)
				print("Length of input now>>",len(actor_input))
				time.sleep(120)
				cur_try+=1
				check_flag=1
				continue

		if break_flag==0:
			actor_truncated_response = previous_move
		else:
			previous_move = actor_truncated_response

		move_validity, move_validator_response = move_validator_module(temp_current_configuration,actor_truncated_response)

		if move_validity == "yes":
			break
		else:

			actor_input.append({
				"role": "assistant",
				"content": actor_response.choices[0].message.content,
			})

			internal_configuration_msg = """
			{}

			Current state:
			{}

			Goal:
			{}

			Please try again to give me only the next action possible from the current state that would help in achieving the goal. 
			Please provide the next action in between a [START] and a [END] token.


			""".format(move_validator_response,temp_current_configuration,goal)


			actor_input.append({
			"role": "user",
			"content": internal_configuration_msg,
		})
			
			num_tries+=1



	return actor_truncated_response,previous_move

with open('mystery_blocksworld_task_1_plan_generation.json') as f:
	data = json.load(f)
i=0
for instance in tqdm(data["instances"]):
	# if i<163:
		
	# 	print("done solving problem {}".format(i+1))
	# 	i=i+1
	# 	continue
	# else:


	max_steps = len(instance['ground_truth_plan'].split("\n"))+3
		
	prompt = """

	I am playing with a set of blocks where I need to arrange the blocks into stacks. Here are the actions I can do

	Pick up a block
	Unstack a block from on top of another block
	Put down a block
	Stack a block on top of another block

	I have the following restrictions on my actions:
	I can only pick up or unstack one block at a time.
	I can only pick up or unstack a block if my hand is empty.
	I can only pick up a block if the block is on the table and the block is clear. A block is clear if the block has no other blocks on top of it and if the block is not picked up.
	I can only unstack a block from on top of another block if the block I am unstacking was really on top of the other block.
	I can only unstack a block from on top of another block if the block I am unstacking is clear.
	Once I pick up or unstack a block, I am holding the block.
	I can only put down a block that I am holding.
	I can only stack a block on top of another block if I am holding the block being stacked.
	I can only stack a block on top of another block if the block onto which I am stacking the block is clear.
	Once I put down or stack a block, my hand becomes empty.
	Once you stack a block on top of a second block, the second block is no longer clear.



	Goal: The goal is to give the actions to achieve the goal.

	Here are three examples:

	Example 1:

	Starting state:
	As initial conditions I have that, the red block is clear, the blue block is clear, the yellow block is clear, the hand is empty, the blue block is on top of the orange block, the red block is on the table, the orange block is on the table and the yellow block is on the table.

	Goal:
	My goal is to have that the orange block is on top of the blue block.

	My actions to achieve the goal from the starting state:

	[START] unstack the blue block from on top of the orange block [END]
	[START] put down the blue block [END]
	[START] pick up the orange block [END]
	[START] stack the orange block on top of the blue block [END]


	Example 2:

	Starting state:
	As initial conditions I have that, the red block is clear, the yellow block is clear, the hand is empty, the red block is on top of the blue block, the yellow block is on top of the orange block, the blue block is on the table and the orange block is on the table.

	Goal:
	My goal is to have that the orange block is on top of the red block.


	My actions to achieve the goal from the starting state:

	[START] unstack the yellow block from on top of the orange block [END]
	[START] put down the yellow block [END]
	[START] pick up the orange block [END]
	[START] stack the orange block on top of the red block [END]

	Example 3:

	Starting state:
	As initial conditions I have that, the blue block is clear, the hand is empty, the blue block is on top of the orange block, the orange block is on top of the yellow block, the yellow block is on top of the red block and the red block is on the table.

	Goal:
	My goal is to have that the red block is on top of the orange block and the yellow block is on top of the red block.

	My actions to achieve the goal from the starting state:

	[START] unstack the blue block from on top of the orange block [END]
	[START] put down the blue block [END]
	[START] unstack the orange block from on top of the yellow block [END]
	[START] put down the orange block [END]
	[START] unstack the yellow block from on top of the red block [END]
	[START] stack the yellow block on top of the blue block [END]
	[START] pick up the red block [END]
	[START] stack the red block on top of the orange block [END]
	[START] unstack the yellow block from on top of the blue block [END]
	[START] stack the yellow block on top of the red block [END]

	Here is the task:

	I am playing with a set of objects. Here are the actions I can do:

	Attack object x
	Feast object x from object y
	Succumb object x
	Overcome object x from object y

	I have the following restrictions on my actions:
	
    To perform Attack object x action, the following facts need to be true: Province object x, Planet object x, Harmony.
    Once Attack object x action is performed the following facts will be true: Pain object x.
    Once Attack object x action is performed the following facts will be false: Province object x, Planet object x, Harmony.
    To perform Succumb object x action, the following facts need to be true: Pain object x.
    Once Succumb object x action is performed the following facts will be true: Province object x, Planet object x, Harmony.    
    Once Succumb object x action is performed the following facts will be false: Pain object x.
   	To perform Overcome object x from object y action, the following needs to be true: Province object y, Pain object x.
    Once Overcome object x from object y action is performed the following will be true: Harmony, Province object x, Object x Craves object y.
    Once Overcome object x from object y action is performed the following will be false: Province object y, Pain object x.
   	To perform Feast object x from object y action, the following needs to be true: Object x Craves object y, Province object x, Harmony.
	Once Feast object x from object y action is performed the following will be true: Pain object x, Province object y.
    Once Feast object x from object y action is performed the following will be false: Object x Craves object y, Province object x, Harmony.


	Goal: The goal is to give the actions to achieve the goal.



	Starting state:
	{}

	Goal:
	{}
	
	Give me only the next action possible from the starting state that would help in achieving the goal. 
	Please provide the next action in between a [START] and a [END] token.



	""".format(instance['query'].split("[STATEMENT]")[2].split("My goal is to")[0],instance['query'].split("[STATEMENT]")[2].split("My plan is as follows:")[0].split("\n")[-3])

	next_state_prediction = deepcopy(instance['query'].split("[STATEMENT]")[2].split("My goal is to")[0])
	goal = deepcopy(instance['query'].split("[STATEMENT]")[2].split("My plan is as follows:")[0].split("\n")[-3])
	

	input = [{
		"role": "system",
		"content": "you are an AI assistant",
	}]

	input.append({
		"role": "user",
		"content": prompt,
	})

	print("starting prompt>>",prompt)
	step=0
	flag=0
	gpt_actions = ""
	previous_move = None
	for step in range(max_steps):
		
		first_temp_current_configuration = deepcopy(next_state_prediction)

		print("step>>",step)
				
		print("config>>",first_temp_current_configuration)
				
		move_proposal,previous_move = actor_module_propose_action(previous_move, input,first_temp_current_configuration,goal)
					
		print("move proposal>>",move_proposal)
		gpt_actions+=move_proposal+'\n'

		next_state_prediction = state_predictor_module(first_temp_current_configuration, move_proposal)

		if task_coordination_module(next_state_prediction,goal):
			flag=1

			internal_configuration_msg = """
			Current state:
			{}

			Goal:
			{}
		
			Give me only the next action possible from the current state that would help in achieving the goal. 
			Please provide the next action in between a [START] and a [END] token.
			

			""".format(next_state_prediction,goal)
			print("internal configuration message>>>",internal_configuration_msg)

			prompt+="\n"+move_proposal+'.'+"\n"+internal_configuration_msg
			
			test_dir = './logs/'
			check_path(test_dir)
			output_dir = test_dir + args.output_dir + '/'
			check_path(output_dir)
			# output_dir+='run{}/'.format(run_no)
			# check_path(output_dir)

			with open(output_dir+'problem{}.log'.format(i+1), 'a') as w:
				w.write(prompt +'\n'+"Solved problem in {} steps.".format(step+1))



			break


		else:

			internal_configuration_msg = """
			Current state:
			{}

			Goal:
			{}

			Give me only the next action possible from the current state that would help in achieving the goal. 
			Please provide the next action in between a [START] and a [END] token.
			

			""".format(next_state_prediction,goal)

			print("internal configuration message>>>",internal_configuration_msg)

			prompt+="\n"+move_proposal+'.'+"\n"+internal_configuration_msg


			input = [{
					"role": "system",
					"content": "you are an AI assistant",
					}]

			input.append({
				"role": "user",
				"content": prompt
			})


				
	if flag==0:
		test_dir = './logs/'
		check_path(test_dir)
		output_dir = test_dir + args.output_dir + '/'
		check_path(output_dir)
	

		with open(output_dir+'problem{}.log'.format(i+1), 'a') as w:
			w.write(prompt +'\n'+"Timed out. Couldn't solve problem in {} steps.".format(max_steps))


		

	

	with open(output_dir+'problem{}.log'.format(i+1), 'a') as w:
		w.write("\nGPT-4 answer>>>>>>>\n"+gpt_actions)


	with open(output_dir+'problem{}.log'.format(i+1), 'a') as w:
		w.write("\nGround truth answer>>>>>>>\n"+instance['ground_truth_plan'])



	
	print("done solving problem {}".format(i+1))
	i=i+1