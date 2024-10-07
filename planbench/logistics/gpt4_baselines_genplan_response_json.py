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
parser.add_argument('--model',type=str, help='name of model', required= True)

args = parser.parse_args()
print(args)


with open('task_1_plan_generation.json') as f:
    data = json.load(f)
file_no = 0
for instance in tqdm(data["instances"]):
    if "problem{}.log".format(file_no+1) in os.listdir(args.output_dir):
    
        file_baseline = open(os.path.join(args.output_dir,'problem{}.log'.format(file_no+1)), 'r')
        lines_baseline = file_baseline.read().splitlines()
        for i in range(len(lines_baseline)):
            if "GPT-4 Response>>>>>>>" in lines_baseline[i]:
                answer_index = i
                break
        for i in range(len(lines_baseline)):
            if "Ground truth answer>>>>>>>" in lines_baseline[i]:
                gt_index = i
        
        gpt_plan = ""
        for j in range(answer_index+1,gt_index):
            if len(lines_baseline[j])>0 and "[START]" in lines_baseline[j] and "[END]" in lines_baseline[j]:
                gpt_plan += lines_baseline[j].split("[START]")[1].split("[END]")[0].replace(".","").strip()+"\n"
                
        
        instance["llm_raw_response"] = gpt_plan + "[PLAN END]\n"
        output_dir = 'LLMs-Planning/plan-bench/responses/logistics/'+ args.model + '/'
        check_path(output_dir)
        with open(output_dir+'task_1_plan_generation.json', 'w') as file:
            json.dump(data, file, indent=4)
        file_no=file_no+1
    else:
        file_no=file_no+1
        continue