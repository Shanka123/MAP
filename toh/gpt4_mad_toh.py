import openai
from gen_start_config import *
from toh_two_shot_examples import standard_prompt
import time
import argparse
import os
openai.api_type = "azure"
openai.api_base = "https://gcrgpt4aoai3.openai.azure.com/"
openai.api_version = "2023-03-15-preview" # can use the older api version openai.api_version = "2022-12-01"

all_As, all_Bs, all_Cs = generate_all_start_config()

icl_examples = [ 3, 22]
agents = 2
rounds = 3
number_target_mapping = {3:"C = [0, 1, 2]", 4:"C = [0, 1, 2, 3]",5:"C = [0, 1, 2, 3, 4]"}
num_steps = {3:"10",4:"20"}

def check_path(path):
	if not os.path.exists(path):
		os.mkdir(path)

parser = argparse.ArgumentParser()

parser.add_argument
parser.add_argument('--openai_api_key', type = str, help='openai key', required= True)
parser.add_argument('--output_dir',type=str, help='directory name where output log files will be stored', required= True)

args = parser.parse_args()
print(args)

openai.api_key = args.openai_api_key

def generate_answer(answer_context):
    try:
        completion = openai.ChatCompletion.create(
                engine='gpt-4-32k',
                messages=answer_context,
                    max_tokens=2000, n=1)
       
    except:
        print("retrying due to an error......")
        time.sleep(60)
        return generate_answer(answer_context)

    return completion

def construct_assistant_message(completion):
    content = completion["choices"][0]["message"]["content"]
    return {"role": "assistant", "content": content}


def construct_message(agents, idx,A, B, C,num_disks):

    
    prefix_string = "These are the recent/updated opinions from other agents: "

    for agent in agents:
        agent_response = agent[idx]["content"]
        response = "\n\n One agent response: ```{}```".format(agent_response)

        prefix_string = prefix_string + response

    query_string = """\n\n Use these opinions carefully as additional advice, can you provide an updated answer?
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
    Step 1. Move <N> from <src> to <tgt>.
    A = []
    B = []
    C = []
    """.format( "A = "+str(A),"B = "+str(B),"C = "+str(C),number_target_mapping[num_disks],num_steps[num_disks])  
    prefix_string = prefix_string + query_string
    return {"role": "user", "content": prefix_string}


for i in range(106):
	if (i+1) not in icl_examples:
		start_time = time.time()
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

		Here are two examples:
		{}

		Here is the task:
		
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
		Step 1. Move <N> from <src> to <tgt>.
		A = []
		B = []
		C = []

		""".format(standard_prompt, "A = "+str(A),"B = "+str(B),"C = "+str(C),number_target_mapping[num_disks],num_steps[num_disks])

		test_dir = './logs/'
		check_path(test_dir)
		output_dir = test_dir + args.output_dir + '/'
		check_path(output_dir)

		with open(output_dir+'problem{}.log'.format(i+1), 'a') as w:
			w.write(prompt +'\n')

		
		agent_contexts = [[{"role": "user", "content":prompt}] for agent in range(agents)]



		for round in range(rounds):
		    for agent_i, agent_context in enumerate(agent_contexts):
		       
		        
		        if round != 0:
		            agent_contexts_other = agent_contexts[:agent_i] + agent_contexts[agent_i+1:]
		            message = construct_message(agent_contexts_other, 2*round - 1, A, B, C,num_disks)
		            agent_context.append(message)

		            print("message: ", message)

		        completion = generate_answer(agent_context)

		        assistant_message = construct_assistant_message(completion)
		        agent_context.append(assistant_message)
		        
		        print("Round {}, agent number {}, response {}".format(round+1, agent_i+1,completion))


		with open(output_dir+'problem{}.log'.format(i+1), 'a') as w:
			w.write("\nGPT-4 Agent1 Response>>>>>>>\n"+agent_contexts[0][-1]["content"])

		with open(output_dir+'problem{}.log'.format(i+1), 'a') as w:
			w.write("\nGPT-4 Agent2 Response>>>>>>>\n"+agent_contexts[1][-1]["content"])
		

		
		print("done solving problem {}".format(i+1))
		