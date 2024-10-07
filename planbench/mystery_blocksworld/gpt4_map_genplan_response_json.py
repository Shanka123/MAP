from tqdm import tqdm
import os
import argparse
import numpy as np

def check_path(path):
    if not os.path.exists(path):
        os.mkdir(path)

parser = argparse.ArgumentParser()

parser.add_argument


parser.add_argument('--output_dir',type=str, help='directory name where output log files are stored', required= True)


args = parser.parse_args()
print(args)

with open('mystery_blocksworld_task_1_plan_generation.json') as f:
    data = json.load(f)
file_no = 0
for instance in tqdm(data["instances"]):
    if "problem{}.log".format(file_no+1) in os.listdir(args.output_dir):
    
        file_baseline = open(os.path.join(args.output_dir,'problem{}.log'.format(file_no+1)), 'r')
        lines_baseline = file_baseline.read().splitlines()
        for i in range(len(lines_baseline)):
            if "GPT-4 answer>>>>>>>" in lines_baseline[i]:
                answer_index = i
                break
        if "Solved" in lines_baseline[answer_index-1]:
            steps = int(lines_baseline[answer_index-1].split(" ")[3])
        else:
            steps = int(lines_baseline[answer_index-1].split(" ")[6])
        
        gpt_plan = ""
        for j in range(1,steps+1):

            gpt_plan+=lines_baseline[answer_index+j]+"\n"
        gpt_plan+="[PLAN END]"
        instance["llm_raw_response"] = gpt_plan
        output_dir = 'LLMs-Planning/plan-bench/responses/mystery_blocksworld/map/'
        check_path(output_dir)

        with open(output_dir+'task_1_plan_generation.json', 'w') as file:
            json.dump(data, file, indent=4)
        file_no=file_no+1
    else:
        file_no=file_no+1
        continue