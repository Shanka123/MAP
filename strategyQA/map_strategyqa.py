import openai
from copy import deepcopy

import time
import re
import json
import numpy as np
import os
import random
from openai import AzureOpenAI

def monitor_decomposer_first(question, subquestion):
	monitor_prompt = """

	Our goal is to answer the following question:

	Question: {}

	However, in order to answer this Question, we first need to consider a set of simpler sub-questions. The following sub-question has been proposed:

	Proposed sub-question: {}

	Is the proposed sub-question relevant for answering the main Question? Before providing a final answer, think very carefully about the original Question, and the knowledge that is required to answer it. Then, indicate whether the proposed sub-question is relevant using the following format: “Answer: < relevant or not relevant >”

	""".format(question, subquestion)

	monitor_input = [{
	"role": "system",
	"content": "you are an AI assistant",
	}]

	monitor_input.append({
		"role": "user",
		"content": monitor_prompt,
	})

	cur_try=0
	while cur_try<20:

		try:

			monitor_response= client.chat.completions.create(model=deployment_name, messages=monitor_input,temperature=0.0,top_p = 0,max_tokens=500)
			
		

			print("monitor decomposer first response>>>", monitor_response.choices[0].message.content)
			char_list_response = monitor_response.choices[0].message.content.split('Answer:')[-1]
			if 'not relevant' in char_list_response or 'Not Relevant' in char_list_response or 'Not relevant' in char_list_response:
				validity = 'no'
			else:
				validity = 'yes'

			print("validity>>",validity)

			break

		except Exception as e:
			err = f"Error: {str(e)}"
			print(err)
			time.sleep(120)
			cur_try+=1
			continue
	return validity,monitor_response.choices[0].message.content


def monitor_decomposer_rest(question, prev_subquestions,prev_subanswers,current_subquestion):
	monitor_prompt = """

	Our goal is to answer the following question:

	Question: {}

	However, in order to answer this Question, we first need to consider a set of simpler sub-questions. The following sub-questions and corresponding answers are provided to you:

	""".format(question)

	prev_subquestions_answers=""
	for idx, (ques,ans) in enumerate(zip(prev_subquestions,prev_subanswers)):
		prev_subquestions_answers+="Sub-question {}: ".format(str(idx+1)) +  ques + "\n"
		prev_subquestions_answers+="Answer: " + ans +"\n\n"

	query_msg = """The following sub-question has been proposed:

		Proposed sub-question : {}

		Is the proposed sub-question relevant for answering the main Question? Before providing a final answer, think very carefully about the original Question, and the knowledge that is required to answer it, and the provided sub-questions and corresponding answers. Then, indicate whether the proposed sub-question is relevant using the following format: “Answer: < relevant or not relevant >”


		""".format(current_subquestion)

	monitor_full_prompt = monitor_prompt+ "\n" + prev_subquestions_answers + query_msg

	monitor_input = [{
	"role": "system",
	"content": "you are an AI assistant",
	}]

	monitor_input.append({
		"role": "user",
		"content": monitor_full_prompt,
	})

	cur_try=0
	while cur_try<20:

		try:

			monitor_response= client.chat.completions.create(model=deployment_name, messages=monitor_input,temperature=0.0,top_p = 0,max_tokens=500)
			
		

			print("monitor decomposer rest response>>>", monitor_response.choices[0].message.content)
			char_list_response = monitor_response.choices[0].message.content.split('Answer:')[-1]
			if 'not relevant' in char_list_response or 'Not Relevant' in char_list_response or 'Not relevant' in char_list_response:
				validity = 'no'
			else:
				validity = 'yes'

			print("validity>>",validity)

			break

		except Exception as e:
			err = f"Error: {str(e)}"
			print(err)
			time.sleep(120)
			cur_try+=1
			continue
	return validity,monitor_response.choices[0].message.content


def monitor_actor_first(subquestion, subanswer):
	monitor_prompt = """

	Our goal is to answer the following question:

	Question: {}

	The following answer has been proposed:

	Proposed Answer: {}

	Is this the correct answer to the question? Before providing your answer, think very carefully about the Question and the Proposed Answer. Then, indicate whether the Proposed Answer is correct, using the following format: “The Proposed Answer is < correct or not correct > “. If the Proposed Answer does not contain a final answer, please give the following response: “No final answer was given”.

	""".format(subquestion,subanswer)

	monitor_input = [{
	"role": "system",
	"content": "you are an AI assistant",
	}]

	monitor_input.append({
		"role": "user",
		"content": monitor_prompt,
	})

	cur_try=0
	while cur_try<20:

		try:

			monitor_response= client.chat.completions.create(model=deployment_name, messages=monitor_input,temperature=0.0,top_p = 0,max_tokens=500)
			
			

			print("monitor actor first response>>>", monitor_response.choices[0].message.content)
			char_list_response = monitor_response.choices[0].message.content
			if 'not correct' in char_list_response or 'incorrect' in char_list_response or 'Not Correct' in char_list_response or 'No final answer was given' in char_list_response or 'no final answer was given' in char_list_response:
				validity = 'no'
			else:
				validity = 'yes'

			print("validity>>",validity)

			break

		except Exception as e:
			err = f"Error: {str(e)}"
			print(err)
			time.sleep(120)
			cur_try+=1
			continue
	return validity,monitor_response.choices[0].message.content



def monitor_actor_rest(current_subquestion,current_subanswer, prev_subquestions,prev_subanswers):
	monitor_prompt = """

	Our goal is to answer the following question:

	Question: {}

	However, in order to answer this Question, we first need to consider a set of simpler sub-questions. The following sub-questions and corresponding answers are provided to you:
	""".format(current_subquestion)

	prev_subquestions_answers=""
	for idx, (ques,ans) in enumerate(zip(prev_subquestions,prev_subanswers)):
		prev_subquestions_answers+="Sub-question {}: ".format(str(idx+1)) +  ques + "\n"
		prev_subquestions_answers+="Answer: " + ans +"\n\n"

	query_msg = """Based on the information in these sub-questions and answers, the following answer has been proposed for the original Question:

		Proposed Answer: {}

		Is this the correct answer to the original Question? Before providing your answer, think very carefully about the Question and the Proposed Answer, and the provided sub-questions and corresponding answers. Then, indicate whether the Proposed Answer is correct, using the following format: “The Proposed Answer is < correct or not correct > “. If the Proposed Answer does not contain a final answer, please give the following response: “No final answer was given”.



		""".format(current_subanswer)


	monitor_full_prompt = monitor_prompt+ "\n" + prev_subquestions_answers + query_msg

	monitor_input = [{
	"role": "system",
	"content": "you are an AI assistant",
	}]

	monitor_input.append({
		"role": "user",
		"content": monitor_full_prompt,
	})

	cur_try=0
	while cur_try<20:

		try:

			monitor_response= client.chat.completions.create(model=deployment_name, messages=monitor_input,temperature=0.0,top_p = 0,max_tokens=500)
			
			

			print("monitor actor rest response>>>", monitor_response.choices[0].message.content)
			char_list_response = monitor_response.choices[0].message.content
			if 'not correct' in char_list_response or 'incorrect' in char_list_response or 'Not Correct' in char_list_response or 'No final answer was given' in char_list_response or 'no final answer was given' in char_list_response:
				validity = 'no'
			else:
				validity = 'yes'

			print("validity>>",validity)

			break

		except Exception as e:
			err = f"Error: {str(e)}"
			print(err)
			time.sleep(120)
			cur_try+=1
			continue
	return validity,monitor_response.choices[0].message.content



def monitor_predictor(question, subquestions,subanswers,answer):

	monitor_prompt = """

	Our goal is to answer the following question:

	Question: {}

	To help us in answering this question, we have the following sub-questions and answers:

	""".format(question)

	subquestions_answers=""
	for idx, (ques,ans) in enumerate(zip(subquestions,subanswers)):
		subquestions_answers+="Sub-question {}: ".format(str(idx+1)) +  ques + "\n"
		subquestions_answers+="Answer: " + ans +"\n\n"


	query_msg = """Based on these sub-questions and answers, the following answer to the main Question has been proposed:

		Proposed Answer: {}

		Is this the correct answer to the Question? Before providing your answer, think very carefully about the Question, the sub-questions and answers and the Proposed Answer. Then, indicate whether the Proposed Answer is correct, using the following format: “The Proposed Answer is < correct or not correct > “. If the Proposed Answer does not contain a final answer, please give the following response: “No final answer was given”.
		""".format(answer)

	monitor_full_prompt = monitor_prompt+ "\n" + subquestions_answers + query_msg



	monitor_input = [{
	"role": "system",
	"content": "you are an AI assistant",
	}]

	monitor_input.append({
		"role": "user",
		"content": monitor_full_prompt,
	})

	cur_try=0
	while cur_try<20:

		try:
			monitor_response= client.chat.completions.create(model=deployment_name, messages=monitor_input,temperature=0.0,top_p = 0,max_tokens=1000)
			
			

			print("monitor predictor response>>>", monitor_response.choices[0].message.content)
			char_list_response = monitor_response.choices[0].message.content
			if 'not correct' in char_list_response or 'incorrect' in char_list_response or 'Not Correct' in char_list_response or 'No final answer was given' in char_list_response or 'no final answer was given' in char_list_response:
				validity = 'no'
			else:
				validity = 'yes'

			print("validity>>",validity)

			break

		except Exception as e:
			err = f"Error: {str(e)}"
			print(err)
			time.sleep(120)
			cur_try+=1
			continue
	return validity,monitor_response.choices[0].message.content

def actor_module_first(subquestion):
	actor_prompt = """
	Question: {}

	Please provide an answer to the above question. Before providing an answer, think very carefully about the question. Then, provide the answer in the following format: “Answer: < >”. You must provide an answer to the question, even if you are uncertain. Please keep in mind that the question may pertain to a hypothetical or counterfactual scenario.


	""".format(subquestion)

	actor_input = [{
	"role": "system",
	"content": "you are an AI assistant",
	}]

	actor_input.append({
		"role": "user",
		"content": actor_prompt,
	})

	num_tries = 0
	while num_tries<5:

	

		cur_try=0
		while cur_try<20:

			try:
				if cur_try==0:

					actor_response= client.chat.completions.create(model=deployment_name, messages=actor_input,temperature=0.0,top_p = 0,max_tokens=1000)
				else:
					actor_response= client.chat.completions.create(model=deployment_name, messages=actor_input,temperature=0.05*cur_try,max_tokens=1000)


			

				print("actor first response>>>", actor_response.choices[0].message.content)
				
				print("extracted answer from actor first response>>>", actor_response.choices[0].message.content.split("Answer:")[-1])
				break

				

			except Exception as e:
				err = f"Error: {str(e)}"
				print(err)
				time.sleep(60)
				cur_try+=1
				continue

		

		validity, validity_response = monitor_actor_first(subquestion,actor_response.choices[0].message.content.split("Answer:")[-1])
		
		if validity=="yes":
			break
		else:

			actor_input.append({
			"role": "assistant",
			"content": actor_response.choices[0].message.content,
			})

			internal_configuration_msg = """
			{}

			Question: {}

			Please try again to provide an answer to the above question. Before providing an answer, think very carefully about the question. Then, provide the answer in the following format: “Answer: < >”. You must provide an answer to the question, even if you are uncertain. Please keep in mind that the question may pertain to a hypothetical or counterfactual scenario.


			""".format(validity_response,subquestion)

	

			actor_input.append({
			"role": "user",
			"content": internal_configuration_msg,
		})
			
			num_tries+=1

	
	return actor_response.choices[0].message.content.split("Answer:")[-1]



def actor_module_rest(current_subquestion,prev_subquestions,prev_subanswers):
	actor_prompt = """
	Our goal is to answer the following question:

	Question: {}

	However, in order to answer this Question, we first need to consider a set of simpler sub-questions. The following sub-questions and corresponding answers are provided to you:


	""".format(current_subquestion)

	prev_subquestions_answers=""
	for idx, (ques,ans) in enumerate(zip(prev_subquestions,prev_subanswers)):
		prev_subquestions_answers+="Sub-question {}: ".format(str(idx+1)) +  ques + "\n"
		prev_subquestions_answers+="Answer: " + ans +"\n\n"

	query_msg = "Please provide an answer to the original Question. Before providing an answer, think very carefully about the question, and the provided sub-questions and corresponding answers. Then, provide the answer in the following format: “Answer: < >”. You must provide an answer to the question, even if you are uncertain. Please keep in mind that the question may pertain to a hypothetical or counterfactual scenario."


	actor_full_prompt = actor_prompt+ "\n" + prev_subquestions_answers + query_msg


	actor_input = [{
	"role": "system",
	"content": "you are an AI assistant",
	}]

	actor_input.append({
		"role": "user",
		"content": actor_full_prompt,
	})

	num_tries = 0
	while num_tries<5:

	

		cur_try=0
		while cur_try<20:

			try:
				if cur_try==0:

					actor_response= client.chat.completions.create(model=deployment_name, messages=actor_input,temperature=0.0,top_p = 0,max_tokens=1000)
			
				else:
					actor_response= client.chat.completions.create(model=deployment_name, messages=actor_input,temperature=0.05*cur_try,max_tokens=1000)
			
			

				print("actor rest response>>>", actor_response.choices[0].message.content)
				print("extracted answer from actor rest response>>>", actor_response.choices[0].message.content.split("Answer:")[-1])
				

				break

				

			except Exception as e:
				err = f"Error: {str(e)}"
				print(err)
				time.sleep(60)
				cur_try+=1
				continue

		
	

		validity, validity_response = monitor_actor_rest(current_subquestion,actor_response.choices[0].message.content.split("Answer:")[-1], prev_subquestions,prev_subanswers)
		
		if validity=="yes":
			break
		else:

			actor_input.append({
			"role": "assistant",
			"content": actor_response.choices[0].message.content,
			})

			internal_configuration_msg = """
			{}

			Question: {}

			Please try again to provide an answer to the original Question. Before providing an answer, think very carefully about the question, and the provided sub-questions and corresponding answers. Then, provide the answer in the following format: “Answer: < >”. You must provide an answer to the question, even if you are uncertain. Please keep in mind that the question may pertain to a hypothetical or counterfactual scenario."

			""".format(validity_response,current_subquestion)

	

			actor_input.append({
			"role": "user",
			"content": internal_configuration_msg,
		})
			
			num_tries+=1

	
	return actor_response.choices[0].message.content.split("Answer:")[-1]
	
def decomposer_module(question):

	decomposer_prompt = """
	Question: {}


	In order to answer this question, we will first need to break it down into a set of simpler sub-questions. Which sub-questions need to be answered first in order to answer the main Question? It is very important that you pay close attention to the exact criteria required in the Question. Before providing a list of sub-questions, first think about the main Question step by step, identifying the knowledge required to answer it correctly. Then, provide the list of sub-questions in following format “Sub-questions: 1. < sub-question 1 > 2. < sub-question 2 > … “

	""".format(question)

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
		

			print("decomposer response>>>", decomposer_response.choices[0].message.content)
			

			break

			

		except Exception as e:
			err = f"Error: {str(e)}"
			print(err)
			time.sleep(120)
			cur_try+=1
			continue

	all_subquestions = re.findall('\..*?\?',decomposer_response.choices[0].message.content.split("Sub-questions:")[-1])


	extracted_subquestions=[]
	for q in all_subquestions:
	    
	    extracted_subquestions.append(q[1:].strip())

	print("all extracted subquestions>>",extracted_subquestions)

	extracted_subanswers = []
	flag=0
	for i in range(len(extracted_subquestions)):
		
		if i ==0:
			ans = actor_module_first(extracted_subquestions[0])
			extracted_subanswers.append(ans)
		else:
			ans = actor_module_rest(extracted_subquestions[i],extracted_subquestions[:i],extracted_subanswers)
			extracted_subanswers.append(ans)
				
			

	return extracted_subquestions,extracted_subanswers



def predictor_module(question,subquestions,subanswers):

	predictor_prompt = """

	Our goal is to answer the following question:

	Question: {}

	To help us in answering this question, we have been provided with the following sub-questions and answers:


	""".format(question)

	subquestions_answers=""
	for idx, (ques,ans) in enumerate(zip(subquestions,subanswers)):
		subquestions_answers+="Sub-question {}: ".format(str(idx+1)) +  ques + "\n"
		subquestions_answers+="Answer: " + ans +"\n\n"


	query_msg = "Let’s try to answer the original Question, using the knowledge contained in the answers to the sub-questions. Before providing a final answer, think carefully about the Question and the answers to the sub-questions. Then, provide your final answer to the Question in the following format: “Final Answer: < true or false >”. You must provide an answer to the question, even if you are uncertain. Please keep in mind that the question may pertain to a hypothetical or counterfactual scenario."

	predictor_full_prompt = predictor_prompt+ "\n" + subquestions_answers + query_msg



	predictor_input = [{
	"role": "system",
	"content": "you are an AI assistant",
	}]

	predictor_input.append({
		"role": "user",
		"content": predictor_full_prompt,
	})

	# num_tries = 0
	# while num_tries<5:

	cur_try=0
	while cur_try<20:

		try:
			predictor_response= client.chat.completions.create(model=deployment_name, messages=predictor_input,temperature=0.0,top_p = 0,max_tokens=1000)
		
			

			print("predictor response>>>", predictor_response.choices[0].message.content)
			char_list_response = predictor_response.choices[0].message.content.split('Final Answer:')[-1]
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

		# validity, validity_response = monitor_predictor(question, subquestions,subanswers,char_list_response)
		# if validity=="yes":
		# 	break
		# else:

		# 	predictor_input.append({
		# 	"role": "assistant",
		# 	"content": predictor_response.choices[0].message.content,
		# 	})

		# 	internal_configuration_msg = """
			
		# 	{}
				
		# 	Question: {}
			
		

		# 	Let’s try again to answer the original Question, using the knowledge contained in the answers to the sub-questions. Before providing a final answer, think carefully about the Question and the answers to the sub-questions. Then, provide your final answer to the Question in the following format: “Final Answer: < true or false >”. You must provide an answer to the question, even if you are uncertain. Please keep in mind that the question may pertain to a hypothetical or counterfactual scenario.

		# 	""".format(validity_response,question)

		# 	predictor_input.append({
		# 	"role": "user",
		# 	"content": internal_configuration_msg,
		# })
			
		# 	num_tries+=1

	return answer




with open('dev.json') as f:
	data = json.load(f)

random.seed(2024)
selected_ids = random.sample(list(np.arange(len(data))),100)

correct = 0 
count=0
for idx in selected_ids:
	question = data[idx]['question']
	# question = "Are ground bell peppers the main ingredient of black pepper?"
	print("question>>>",question)
	print("correct answer>>>",data[idx]['answer'])
	count+=1

	
	subquestions,subanswers = decomposer_module(question)
	
	answer = predictor_module(question,subquestions,subanswers)

	
		
	if str(answer) == str(data[idx]['answer']):
		print("correct answer$$$$")
		correct+=1
	else:
		print("incorrect answer!!!!")


	
		
		

	print("Number of correct answers till now>>>",correct)
	print("Total questions till now>>>",count)

print("Total number of correct answers>>",correct)







