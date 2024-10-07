import openai
import argparse
import os
import time
import json
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



with open('mystery_blocksworld_task_1_plan_generation.json') as f:
	data = json.load(f)
i=0
for instance in tqdm(data["instances"]):


	
		
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



	Here is the task:
	
	Starting state:
	{}

	Goal:
	{}
	
	What is the plan to achieve my goal from the starting state? Just give the actions in the plan.

	Please provide each action in the plan between a [START] and a [END] token, according to the format:
	1. [START] <Action 1> [END]
	2. [START] <Action 2> [END]
	.
	.
	.


	""".format(instance['query'].split("[STATEMENT]")[2].split("My goal is to")[0],instance['query'].split("[STATEMENT]")[2].split("My plan is as follows:")[0].split("\n")[-3])

	test_dir = './logs/'
	check_path(test_dir)
	output_dir = test_dir + args.output_dir + '/'
	check_path(output_dir)

	with open(output_dir+'problem{}.log'.format(i+1), 'a') as w:
		w.write(prompt +'\n')


	
	


	input = [{
		"role": "system",
		"content": "you are an AI assistant",
	}]

	input.append({
		"role": "user",
		"content": prompt,
	})

	another_cur_try = 0
	while another_cur_try <5:
		try:

			response= client.chat.completions.create(model=deployment_name, messages=input,temperature=0.0,top_p = 0,max_tokens=2000)
			
			

			num_input_tokens= response.usage.prompt_tokens
			num_output_tokens= response.usage.completion_tokens

			break

		except Exception as e:
			err = f"Error: {str(e)}"
			print(err)
			time.sleep(60)
			another_cur_try+=1
			
			continue
	instance["llm_raw_response"] = response.choices[0].message.content

	with open(output_dir+'task_1_plan_generation.json', 'w') as file:
		json.dump(data, file, indent=4)


	with open(output_dir+'problem{}.log'.format(i+1), 'a') as w:
		w.write("GPT-4 Response>>>>>>>\n"+response.choices[0].message.content)
		

	
	with open(output_dir+'problem{}.log'.format(i+1), 'a') as w:
		w.write("\nGround truth answer>>>>>>>\n"+instance['ground_truth_plan'])

	
	
	print("done solving problem {}".format(i+1))
	i=i+1
