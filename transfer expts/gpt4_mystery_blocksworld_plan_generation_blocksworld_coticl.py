import openai
import argparse
import os
from blocksworld_plan_generation_fewshot_cot_examples import standard_prompt
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

	Here are three examples:
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

	

	

	Starting state:
	{}

	Goal:
	{}
	
	My plan is as follows:

	Please provide each action for the plan to achieve the goal from the starting state after "Action:" and between a [START] and a [END] token.


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