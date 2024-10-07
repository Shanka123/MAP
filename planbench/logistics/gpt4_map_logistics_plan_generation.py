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

		I have to plan logistics to transport packages within cities via trucks and between cities via airplanes. Locations within a city are directly connected (trucks can move between any two such locations), and so are the cities. In each city there is exactly one truck and each city has one location that serves as an airport.
		Here are the actions that can be performed:

		Load a package into a truck. For example, load package_1 into truck_1 at location_1_1.
		Load a package into an airplane. For example, load package_1 into airplane_1 at location_1_1.
		Unload a package from a truck. For example, unload package_1 from truck_1 at location_1_1.
		Unload a package from an airplane. For example, unload package_1 from airplane_1 at location_1_1.
		Drive a truck from one location to another location. For example, drive truck_1 from location_1_1 to location_1_2 in city_1.
		Fly an airplane from one city to another city. For example, fly airplane_1 from location_1_1 to location_2_1. Here location_1_1 is the airport in city_1 and location_2_1 is the airport in city_2.

		The following are the restrictions on the actions:
		A package can be loaded into a truck only if the package and the truck are in the same location.
		Once a package is loaded into a truck, the package is not at the location and is in the truck.   
		A package can be loaded into an airplane only if the package and the airplane are in the same location.
		Once a package is loaded into an airplane, the package is not at the location and is in the airplane.
		A package can be unloaded from a truck only if the package is in the truck.
		Once a package is unloaded from a truck, the package is not in the truck and is at the location of the truck.
		A package can be unloaded from an airplane only if the package in the airplane.
		Once a package is unloaded from an airplane, the package is not in the airplane and is at the location of the airplane.   
		A truck can be driven from one location to another if the truck is at the from-location and both from-location and to-location are locations in the same city.
		Once a truck is driven from one location to another, it is not at the from-location and is at the to-location.
		An airplane can be flown from one city to another if the from-location and the to-location are airports and the airplane is at the from-location.
		Once an airplane is flown from one city to another the airplane is not at the from-location and is at the to-location.

		Goal: The goal is check whether the action when taken on the current state satisfies or violates the restrictions and based on that if it is a valid or invalid move.

		Here are two examples:

		Example 1:

		Current state: 
		As initial conditions I have that, location_0_0 is an airport, location_1_0 is an airport, airplane_0 is at location_0_0, airplane_1 is at location_0_0, package_0 is at location_1_0, truck_0 is at location_0_0, truck_1 is at location_1_0, location_0_0 is in the city city_0 and location_1_0 is in the city city_1.
		

		Action: 
		fly airplane_1 from location_0_0 to location_1_0.

		Answer: 
		location_0_0 is an airport. location_1_0 is an airport. location_0_0 is in the city city_0 and location_1_0 is in the city city_1. airplane_1 is at location_0_0. Hence, fly airplane_1 from location_0_0 to location_1_0 is a valid action.


		Example 2:

		Current state:
		As initial conditions I have that, location_0_0 is an airport, location_1_0 is an airport, airplane_0 is at location_1_0, package_0 is at location_1_0, package_1 is at location_0_0, truck_0 is at location_0_0, truck_1 is at location_1_0, location_0_0 is in the city city_0 and location_1_0 is in the city city_1.
		

		Action:
		load package_1 into airplane_0 at location_0_0.


		Answer:
		package_1 is at location_0_0. airplane_0 is at location_1_0. Since package_1 and airplane_0 aren't in the same location, load package_1 into airplane_0 at location_0_0 is an invalid action. 


		Here is the task:

		Current state:
		{}

		Action:
		{}.

		Answer:


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

	You will be given a current state, and an action. Your task is to predict the next state that results after taking the action at the current state.
    
    
    Here are two examples:

    Example 1:

    Current state: 
    As initial conditions I have that, location_0_0 is an airport, location_1_0 is an airport, airplane_0 is at location_0_0, airplane_1 is at location_0_0, package_0 is at location_1_0, truck_0 is at location_0_0, truck_1 is at location_1_0, location_0_0 is in the city city_0 and location_1_0 is in the city city_1.
    

    Action: 
    fly airplane_1 from location_0_0 to location_1_0.

    Next state: 
    As initial conditions I have that, location_0_0 is an airport, location_1_0 is an airport, airplane_0 is at location_0_0, airplane_1 is at location_1_0, package_0 is at location_1_0, truck_0 is at location_0_0, truck_1 is at location_1_0, location_0_0 is in the city city_0 and location_1_0 is in the city city_1.
   


    Example 2:

    Current state:
    As initial conditions I have that, location_0_0 is an airport, location_1_0 is an airport, airplane_0 is at location_1_0, package_0 is at location_1_0, truck_0 is at location_0_0, truck_1 is at location_1_0, location_0_0 is in the city city_0, location_0_1 is in the city city_0, location_1_0 is in the city city_1 and location_1_1 is in the city city_1.
    

    Action:
    load package_0 into truck_1 at location_1_0.

    Next state:
    As initial conditions I have that, location_0_0 is an airport, location_1_0 is an airport, airplane_0 is at location_1_0, truck_0 is at location_0_0, truck_1 is at location_1_0, package_0 is in truck_1, location_0_0 is in the city city_0, location_0_1 is in the city city_0, location_1_0 is in the city city_1 and location_1_1 is in the city city_1.
   

    Here is the task:

    Current state:
    {}
    
    Action:
    {}.
    
    Please note that just because a package is in a truck at location A doesn’t mean the package is at location A, the package needs to be unloaded before it’s at location A.
    Please provide your answer for the next state that results after taking the action at the current state in the following format only: “Next state: < >”.


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
	return predictor_response.choices[0].message.content.split("Next state:")[-1]




def task_coordination_module(current_state,goal):

	task_coordination_prompt= """

	You will be given a current state and the goal, and your task is to say whether the goal is acheived in the current state.
    
    Here are two examples:

    Example 1:

    Current state:
    As initial conditions I have that, location_0_0 is an airport, location_1_0 is an airport, airplane_0 is at location_0_0, airplane_1 is at location_0_0, package_0 is in airplane_0, truck_0 is at location_0_0, truck_1 is at location_1_0, location_0_0 is in the city city_0 and location_1_0 is in the city city_1.
    
    Goal:
    My goal is to have that package_0 is at location_0_0.

    Thoughts: My goal is to have that package_0 is at location_0_0. package_0 is currently in airplane_0. However, if a package is in an airplane, the package is not at the location and is in the airplane. Hence the package is not at location 0_0.

    Answer: no 

    Example 2:

    Current state:
    As initial conditions I have that, location_0_0 is an airport, location_1_0 is an airport, airplane_0 is at location_0_0, airplane_1 is at location_1_0, truck_0 is at location_0_0, truck_1 is at location_1_0, package_0 is at location_0_0, location_0_0 is in the city city_0 and location_1_0 is in the city city_1.
    
    Goal:
    My goal is to have that package_0 is at location_0_0.

    Thoughts: My goal is to have that package_0 is at location_0_0. package_0 is currently at location 0_0. 

    Answer: yes


    Here is the task:

    Current state:
    {}

    Goal:
    {}

    Please note that just because a package is in a truck at location A doesn’t mean the package is at location A, the package needs to be unloaded before it’s at location A.
    First give your thoughts after "Thoughts:". Then give your final answer after "Answer:".

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
				if len(actor_truncated_response)==43 or len(actor_truncated_response)==45 or len(actor_truncated_response)==46 or len(actor_truncated_response)==48 or len(actor_truncated_response)==57:

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


with open('task_1_plan_generation.json') as f:
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

	I have to plan logistics to transport packages within cities via trucks and between cities via airplanes. Locations within a city are directly connected (trucks can move between any two such locations), and so are the cities. In each city there is exactly one truck and each city has one location that serves as an airport.
	Here are the actions that can be performed:

	Load a package into a truck. For example, load package_1 into truck_1 at location_1_1.
	Load a package into an airplane. For example, load package_1 into airplane_1 at location_1_1.
	Unload a package from a truck. For example, unload package_1 from truck_1 at location_1_1.
	Unload a package from an airplane. For example, unload package_1 from airplane_1 at location_1_1.
	Drive a truck from one location to another location. For example, drive truck_1 from location_1_1 to location_1_2 in city_1.
	Fly an airplane from one city to another city. For example, fly airplane_1 from location_1_1 to location_2_1. Here location_1_1 is the airport in city_1 and location_2_1 is the airport in city_2.

	The following are the restrictions on the actions:
	A package can be loaded into a truck only if the package and the truck are in the same location.
	Once a package is loaded into a truck, the package is not at the location and is in the truck.   
	A package can be loaded into an airplane only if the package and the airplane are in the same location.
	Once a package is loaded into an airplane, the package is not at the location and is in the airplane.
	A package can be unloaded from a truck only if the package is in the truck.
	Once a package is unloaded from a truck, the package is not in the truck and is at the location of the truck.
	A package can be unloaded from an airplane only if the package in the airplane.
	Once a package is unloaded from an airplane, the package is not in the airplane and is at the location of the airplane.   
	A truck can be driven from one location to another if the truck is at the from-location and both from-location and to-location are locations in the same city.
	Once a truck is driven from one location to another, it is not at the from-location and is at the to-location.
	An airplane can be flown from one city to another if the from-location and the to-location are airports and the airplane is at the from-location.
	Once an airplane is flown from one city to another the airplane is not at the from-location and is at the to-location.

	Goal: The goal is to give the actions to achieve the goal.

	Here are three examples:

	Example 1:

	Starting state:
	As initial conditions I have that, location_0_0 is an airport, location_1_0 is an airport, airplane_0 is at location_0_0, airplane_1 is at location_0_0, package_0 is at location_1_0, truck_0 is at location_0_0, truck_1 is at location_1_0, location_0_0 is in the city city_0 and location_1_0 is in the city city_1.
	
	Goal:
	My goal is to have that package_0 is at location_0_0.

	My actions to achieve the goal from the starting state:

	[START] fly airplane_1 from location_0_0 to location_1_0 [END]
	[START] load package_0 into airplane_1 at location_1_0 [END]
	[START] fly airplane_1 from location_1_0 to location_0_0 [END]
	[START] unload package_0 from airplane_1 at location_0_0 [END]


	Example 2:

	Starting state:
	As initial conditions I have that, location_0_0 is an airport, location_1_0 is an airport, airplane_0 is at location_1_0, package_0 is at location_1_0, truck_0 is at location_0_0, truck_1 is at location_1_0, location_0_0 is in the city city_0, location_0_1 is in the city city_0, location_1_0 is in the city city_1 and location_1_1 is in the city city_1.
	
	Goal:
	My goal is to have that package_0 is at location_1_1.

	My actions to achieve the goal from the starting state:

	[START] load package_0 into truck_1 at location_1_0 [END]
	[START] drive truck_1 from location_1_0 to location_1_1 in city_1 [END]
	[START] unload package_0 from truck_1 at location_1_1 [END]

	Example 3:

	Starting state:
	As initial conditions I have that, location_0_0 is an airport, location_1_0 is an airport, airplane_0 is at location_0_0, package_0 is at location_0_1, truck_0 is at location_0_0, truck_1 is at location_1_1, location_0_0 is in the city city_0, location_0_1 is in the city city_0, location_1_0 is in the city city_1 and location_1_1 is in the city city_1.
	
	Goal:
	My goal is to have that package_0 is at location_1_0.

	My actions to achieve the goal from the starting state:

	[START] drive truck_0 from location_0_0 to location_0_1 in city_0 [END]
	[START] load package_0 into truck_0 at location_0_1 [END]
	[START] drive truck_0 from location_0_1 to location_0_0 in city_0 [END]
	[START] unload package_0 from truck_0 at location_0_0 [END]
	[START] load package_0 into airplane_0 at location_0_0 [END]
	[START] fly airplane_0 from location_0_0 to location_1_0 [END]
	[START] unload package_0 from airplane_0 at location_1_0 [END]



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
