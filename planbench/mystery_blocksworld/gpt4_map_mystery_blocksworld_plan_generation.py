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

	I am playing with a set of objects. Here are the actions I can do:

	Attack object
	Feast object from another object
	Succumb object
	Overcome object from another object

	I have the following restrictions on my actions:
    To perform Attack action, the following facts need to be true: Province object, Planet object, Harmony.
    To perform Succumb action, the following facts need to be true: Pain object.
    To perform Overcome action, the following needs to be true: Province other object, Pain object.
    To perform Feast action, the following needs to be true: Object Craves other object, Province object, Harmony.
	   
	Goal: The goal is to check whether the action when taken on the current state satisfies or violates the restrictions and based on that if it is a valid or invalid move.

	Here are two examples:

	Example 1:

	Current state: 
	As initial conditions I have that, object a craves object c, object c craves object b, object d craves object a, harmony, planet object b and province object d.


	Action: 
	feast object c from object b.

	Answer: 
	To perform feast object c from object b, the following facts need to be true: object c craves object b, province object c, harmony. Based on the current state, province object c isn't true. Hence, feast object c from object b is an invalid action.


	Example 2:

	Current state:
	As initial conditions I have that, object b craves object c, harmony, planet object a, planet object c, planet object d, province object a, province object b and province object d.


	Action:
	feast object b from object c.


	Answer:
	To perform feast object b from object c, the following facts need to be true: object b craves object c, province object b, harmony. Based on the current state, all the facts are true. Hence, feast object b from object c is a valid action.


	Here is the task:

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

	I am playing with a set of objects. Here are the actions I can do:

	Attack object
	Feast object from another object
	Succumb object
	Overcome object from another object

	I have the following restrictions on my actions:
 
    Once Attack action is performed the following facts will be true: Pain object.
    Once Attack action is performed the following facts will be false: Province object, Planet object, Harmony.
    
    Once Succumb action is performed the following facts will be true: Province object, Planet object, Harmony.    
    Once Succumb action is performed the following facts will be false: Pain object.
   
    Once Overcome action is performed the following will be true: Harmony, Province object, Object Craves other object.
    Once Overcome action is performed the following will be false: Province other object, Pain object.
   
    Once Feast action is performed the following will be true: Pain object, Province other object.
    Once Feast action is performed the following will be false: Object Craves other object, Province object, Harmony.

	Goal: The goal is to only predict the next state that results after taking the action at the current state.


	Here are three examples:

	Example 1:

	Current state:
	As initial conditions I have that, object a craves object c, object c craves object b, object d craves object a, harmony, planet object b and province object d.


	Action:
	feast object d from object a.

	Once feast object d from object a is performed the following will be true: pain object d, province object a.
	Once ffeast object d from object a is performed the following will be false: object d craves object a, province object d, harmony.
	Next state:
	As initial conditions I have that, pain object d, province object a, object a craves object c, object c craves object b, planet object b.

	Example 2:

	Current state:
	As initial conditions I have that, pain object d, province object b, planet object b, planet object a, planet object c, province object a, province object c.

	Action:
	overcome object d from object a.

	Once overcome object d from object a is performed the following facts will be true: harmony, province object d, object d craves object a.    
	Once overcome object d from object a is performed the following facts will be false: province object a, pain object d.
	Next state:
	As initial conditions I have that object d craves object a, harmony, planet object a, planet object b, planet object c, province object b, province object c, province object d.

	Example 3:

	Current state:
	As initial conditions I have that, pain object b, planet object a, planet object c, planet object d, province object a, province object d, province object c.


	Action:
	succumb object b.

	Once succumb object b is performed the following facts will be true: province object b, planet object b, harmony.    
	Once succumb object b is performed the following facts will be false: pain object b.
	Next state:
	As initial conditions I have that, harmony, planet object a, planet object b, planet object c, planet object d, province object a, province object b, province object c, province object d.



	Here is the task:

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
	As initial conditions I have that, object a craves object c, object c craves object b, object d craves object a, harmony, planet object b and province object d.

	Goal:
	My goal is to have that object a craves object d and object d craves object b.

	Answer: 
	Currently object a craves object c, object c craves object b, object d craves object a. However my goal is to have that object a craves object d and object d craves object b. Hence the goal is not achieved in the current state. Hence no. 

	Example 2:

	Current state:
	As initial conditions I have that, harmony, province object c, object c craves object b, province object a, planet object a, planet object d, province object d, planet object b. 

	Goal:
	My goal is to have that object c craves object b.

	Answer:
	Currently object c craves object b. However my goal is to have that object c craves object b. Hence the goal is achieved in the current state. Hence yes. 

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

	I am playing with a set of objects. Here are the actions I can do:

	Attack object
	Feast object from another object
	Succumb object
	Overcome object from another object

	I have the following restrictions on my actions:
    To perform Attack action, the following facts need to be true: Province object, Planet object, Harmony.
    Once Attack action is performed the following facts will be true: Pain object.
    Once Attack action is performed the following facts will be false: Province object, Planet object, Harmony.
    To perform Succumb action, the following facts need to be true: Pain object.
    Once Succumb action is performed the following facts will be true: Province object, Planet object, Harmony.    
    Once Succumb action is performed the following facts will be false: Pain object.
    To perform Overcome action, the following needs to be true: Province other object, Pain object.
    Once Overcome action is performed the following will be true: Harmony, Province object, Object Craves other object.
    Once Overcome action is performed the following will be false: Province other object, Pain object.
    To perform Feast action, the following needs to be true: Object Craves other object, Province object, Harmony.
    Once Feast action is performed the following will be true: Pain object, Province other object.
    Once Feast action is performed the following will be false:, Object Craves other object, Province object, Harmony.


	Goal: The goal is to give the actions to achieve the goal.

	Here are three examples:

	Example 1:

	Starting state:
	As initial conditions I have that, object b craves object c, harmony, planet object a, planet object c, planet object d, province object a, province object b and province object d.
	
	Goal:
	My goal is to have that object c craves object b.

	My actions to achieve the goal from the starting state:

	[START] feast object b from object c [END]
	[START] succumb object b [END]
	[START] attack object c [END]
	[START] overcome object c from object b [END]


	Example 2:

	Starting state:
	As initial conditions I have that, object a craves object b, object d craves object c, harmony, planet object b, planet object c, province object a and province object d.
	
	Goal:
	My goal is to have that object c craves object a.

	My actions to achieve the goal from the starting state:

	[START] feast object d from object c [END]
	[START] succumb object d [END]
	[START] attack object c [END]
	[START] overcome object c from object a [END]

	Example 3:

	Starting state:
	As initial conditions I have that, object b craves object c, object c craves object d, object d craves object a, harmony, planet object a and province object b.
	
	Goal:
	My goal is to have that object a craves object c and object d craves object a.

	My actions to achieve the goal from the starting state:

	[START] feast object b from object c [END]
	[START] succumb object b [END]
	[START] feast object c from object d [END]
	[START] succumb object c [END]
	[START] feast object d from object a [END]
	[START] overcome object d from object b [END]
	[START] attack object a [END]
	[START] overcome object a from object c [END]
	[START] feast object d from object b [END]
	[START] overcome object d from object a [END]



	Here is the task:

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
