import openai
from gen_start_config import *
from toh_two_shot_4disk_examples import standard_prompt
import time
import argparse
import os

from openai import AzureOpenAI

from azure.identity import DefaultAzureCredential, ChainedTokenCredential, AzureCliCredential, get_bearer_token_provider
import os


scope = "api://trapi/.default"
credential = get_bearer_token_provider(ChainedTokenCredential(
	AzureCliCredential(),
	DefaultAzureCredential(
		exclude_cli_credential=True,
		# Exclude other credentials we are not interested in.
		exclude_environment_credential=True,
		exclude_shared_token_cache_credential=True,
		exclude_developer_cli_credential=True,
		exclude_powershell_credential=True,
		exclude_interactive_browser_credential=True,
		exclude_visual_studio_code_credentials=True,
		# DEFAULT_IDENTITY_CLIENT_ID is a variable exposed in
		# Azure ML Compute jobs that has the client id of the
		# user-assigned managed identity in it.
		# See https://learn.microsoft.com/en-us/azure/machine-learning/how-to-identity-based-service-authentication#compute-cluster
		# In case it is not set the ManagedIdentityCredential will
		# default to using the system-assigned managed identity, if any.
		managed_identity_client_id=os.environ.get("DEFAULT_IDENTITY_CLIENT_ID"),
	)
),scope)


api_version = '2024-12-01-preview'
deployment_name = 'gpt-4-32k_0314'
instance = 'gcr/shared' # See https://aka.ms/trapi/models for the instance name, remove /openai (library adds it implicitly) 
endpoint = f'https://trapi.research.microsoft.com/{instance}'

client = AzureOpenAI(
	azure_endpoint=endpoint,
	azure_ad_token_provider=credential,
	api_version=api_version,
)


all_As, all_Bs, all_Cs = generate_all_start_config()

number_message_mapping = {3:"three numbers -- 0, 1, and 2 --", 4:"four numbers -- 0, 1, 2, and 3 --",5:"five numbers -- 0, 1, 2, 3, and 4 --"}
number_target_mapping = {3:"C = [0, 1, 2]", 4:"C = [0, 1, 2, 3]",5:"C = [0, 1, 2, 3, 4]"}
num_steps = {3:"10",4:"20"}

def check_path(path):
	if not os.path.exists(path):
		os.mkdir(path)

parser = argparse.ArgumentParser()

parser.add_argument

parser.add_argument('--output_dir',type=str, help='directory name where output log files will be stored', required= True)

args = parser.parse_args()
print(args)



icl_ex1 = [[0, 1, 2],[3],[]]

icl_ex2 = [[1, 2],[0],[3]]

#

for i in range(26,106):

	A=all_As[i] 

	B=all_Bs[i]

	C=all_Cs[i]

	if [A,B,C] !=icl_ex1 and [A,B,C] !=icl_ex2:

	
		start_time = time.time()
		
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

		
		""".format(standard_prompt,"A = "+str(A),"B = "+str(B),"C = "+str(C),number_target_mapping[num_disks],num_steps[num_disks])

		
		test_dir = './logs/'
		check_path(test_dir)
		output_dir = test_dir + args.output_dir + '/'
		check_path(output_dir)

		with open(output_dir+'problem{}.log'.format(i+1), 'a') as w:
			w.write(prompt +'\n')

		


		input = [{
		    "role": "user",
		    "content": prompt,
		}]

		

		another_cur_try = 0
		while another_cur_try <10:
			try:
				time1 = time.time()
				response = client.chat.completions.create(model=deployment_name, messages=input, temperature=0.0,top_p = 0,
				        max_tokens=2000)
			

				time2 = time.time()
				

				break

			except Exception as e:
				err = f"Error: {str(e)}"
				print(err)
				time.sleep(120)
				another_cur_try+=1
				
				continue


		with open(output_dir+'problem{}.log'.format(i+1), 'a') as w:
			w.write("GPT-4 Response>>>>>>>\n"+response.choices[0].message.content)
		
		
		
		
		end_time = time.time()

		
		print("done solving problem {}".format(i+1))
