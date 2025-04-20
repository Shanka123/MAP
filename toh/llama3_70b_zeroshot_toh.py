import openai
from gen_start_config import *

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
num_steps = {3:"10",4:"20"}

def check_path(path):
	if not os.path.exists(path):
		os.mkdir(path)





for i in range(26):
	A=all_As[i] 

	B=all_Bs[i]

	C=all_Cs[i]
	num_disks = max(A+B+C)+1
	prompt = """Consider the following puzzle problem:

	Problem description:
	- There are three lists labeled A, B, and C.
	- There is a set of numbers distributed among those three lists.
	- You can only move numbers from the rightmost end of one list to the rightmost end of another list.
	Rule #1: You can only move a number if it is at the rightmost end of its current list.
	Rule #2: You can only move a number to the rightmost end of a list if it is larger than the other numbers in that list.

	A move is valid if it satisfies both Rule #1 and Rule #2.
	A move is invalid if it violates either Rule #1 or Rule #2.


	Goal: The goal is to end up in the configuration where all numbers are in list C, in ascending order using minimum number of moves.
	
	This is the starting configuration:
	{}
	{}
	{}
	This is the goal configuration:
	A = []
	B = []
	{}
	
	Give me the sequence of moves to solve the puzzle from the starting configuration, updating the lists after each move. Please try to use as few moves as possible, and make sure to follow the rules listed above. Please limit your answer to a maximum of {} steps.
	Please format your answer as below:
	Step 1. Move <N> from list <src> to list <tgt>.
	A = []
	B = []
	C = []

	""".format("A = "+str(A),"B = "+str(B),"C = "+str(C),number_target_mapping[num_disks],num_steps[num_disks])

	test_dir = './logs/'
	check_path(test_dir)
	output_dir = test_dir +  'llama3_70b_toh_zeroshot/'
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

	actor_prompt = pipeline.tokenizer.apply_chat_template(
			input, 
			tokenize=False, 
			add_generation_prompt=True
	)

	terminators = [
		pipeline.tokenizer.eos_token_id,
		pipeline.tokenizer.convert_tokens_to_ids("<|eot_id|>")
	]

	outputs = pipeline(
		actor_prompt,
		max_new_tokens=2000,
		eos_token_id=terminators,
		do_sample=False)


	
		



	


	with open(output_dir+'problem{}.log'.format(i+1), 'a') as w:
		w.write("Llama3-70b Response>>>>>>>\n"+outputs[0]["generated_text"][len(actor_prompt):])
	
	
	
	print("done solving problem {}".format(i+1))
