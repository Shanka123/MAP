import openai
import argparse
import os
from mystery_blocksworld_plan_generation_fewshot_examples import standard_prompt
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

agents = 2
rounds = 3

def generate_answer(answer_context):
    try:
    	completion = client.chat.completions.create(model=deployment_name, messages=answer_context,max_tokens=2000,n=1)
			
			

       
       
    except:
        print("retrying due to an error......")
        time.sleep(60)
        return generate_answer(answer_context)

    return completion

def construct_assistant_message(completion):
    content = completion.choices[0].message.content
    return {"role": "assistant", "content": content}


def construct_message(agents, idx,query):

    
    prefix_string = "These are the recent/updated opinions from other agents: "

    for agent in agents:
        agent_response = agent[idx]["content"]
        response = "\n\n One agent response: ```{}```".format(agent_response)

        prefix_string = prefix_string + response

    query_string = """\n\n Use these opinions carefully as additional advice, can you provide an updated answer?
    {}

   
    """.format( query)  
    prefix_string = prefix_string + query_string
    return {"role": "user", "content": prefix_string}



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

	Here are three examples:
	{}

	Here is the task:

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


	
	agent_contexts = [[{"role": "user", "content":prompt}] for agent in range(agents)]



	for round in range(rounds):
	    for agent_i, agent_context in enumerate(agent_contexts):
	       
	        
	        if round != 0:
	            agent_contexts_other = agent_contexts[:agent_i] + agent_contexts[agent_i+1:]
	            message = construct_message(agent_contexts_other, 2*round - 1, instance['query'].split("[STATEMENT]")[2])
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
		

	with open(output_dir+'problem{}.log'.format(i+1), 'a') as w:
		w.write("\nGround truth answer>>>>>>>\n"+instance['ground_truth_plan'])

	
	
	print("done solving problem {}".format(i+1))
	i=i+1
