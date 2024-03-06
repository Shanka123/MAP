import openai
import argparse
import os

import time
import json
from tqdm import tqdm
openai.api_type = "azure"
openai.api_base = "https://gcrgpt4aoai3.openai.azure.com/"
openai.api_version = "2023-03-15-preview" # can use the older api version openai.api_version = "2022-12-01"

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

with open('task_1_plan_generation.json') as f:
	data = json.load(f)
i=0
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


	

	Here is the task:
	
	{}
	
	What is the plan to achieve my goal? Just give the actions in the plan.


	""".format(instance['query'].split("[STATEMENT]")[2])

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
			response = openai.ChatCompletion.create(
				engine='gpt-4-32k',
				messages=input,temperature=0.0,top_p = 0,
					max_tokens=2000)

			num_input_tokens= response["usage"]["prompt_tokens"]
			num_output_tokens= response["usage"]["completion_tokens"]

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

