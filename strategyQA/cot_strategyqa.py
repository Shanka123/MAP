import openai
from copy import deepcopy

import time
import re
import json
import numpy as np
import os
import random
from openai import AzureOpenAI



def cot_module(question):

	cot_prompt = """Answer the following question: {}

	Make a strategy then write. Your output should be of the following format:
	
	Strategy:
	Your strategy about how to answer the question.
	
	Answer:
	Your answer to the question. It should end with either “the answer is true” or “the answer is false”.
	""".format(question)


	cot_input = [{
	"role": "system",
	"content": "you are an AI assistant",
	}]

	cot_input.append({
		"role": "user",
		"content": cot_prompt,
	})

	# num_tries = 0
	# while num_tries<5:

	cur_try=0
	while cur_try<20:

		try:
			response= client.chat.completions.create(model=deployment_name, messages=cot_input,temperature=0.0,top_p = 0,max_tokens=2000)
		
			

			print("response>>>", response.choices[0].message.content)
			char_list_response = response.choices[0].message.content.split('Answer:')[-1]
			if 'False' in char_list_response or 'false' in char_list_response or 'not true' in char_list_response:
				answer= 'False'
			else:
				answer= 'True'

			print("answer>>",answer)

			break

		except Exception as e:
			err = f"Error: {str(e)}"
			print(err)
			time.sleep(120)
			cur_try+=1
			continue

	
	return answer

with open('dev.json') as f:
	data = json.load(f)

random.seed(2024)
selected_ids = random.sample(list(np.arange(len(data))),100)

correct = 0 
count=0

for idx in selected_ids:
	question = data[idx]['question']
	print("question>>>",question)
	print("correct answer>>>",data[idx]['answer'])
	count+=1

	
	answer = cot_module(question)
	
	
		
	if str(answer) == str(data[idx]['answer']):
		print("correct answer$$$$")
		correct+=1
	else:
		print("incorrect answer!!!!")


	
		
		

	print("Number of correct answers till now>>>",correct)
	print("Total questions till now>>>",count)

print("Total number of correct answers>>",correct)


