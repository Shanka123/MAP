import openai
import argparse
import os
from logistics_plan_generation_fewshot_examples import standard_prompt
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



with open('task_1_plan_generation.json') as f:
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
