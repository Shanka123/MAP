import openai
import argparse
import os
from toh_two_shot_examples import standard_prompt
# from toh_twoshot_cot_examples import standard_prompt
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
	
	Please provide each action for the plan to achieve the goal from the starting state between a [START] and a [END] token.


	""".format(standard_prompt, instance['query'].split("[STATEMENT]")[2].split("My goal is to")[0],instance['query'].split("[STATEMENT]")[2].split("My plan is as follows:")[0].split("\n")[-3])

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

			response= client.chat.completions.create(model=deployment_name, messages=input,temperature=0.0,top_p = 0,max_tokens=4000)
			
			

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