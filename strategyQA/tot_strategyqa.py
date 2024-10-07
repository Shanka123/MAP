import itertools
import numpy as np
from functools import partial
import openai
from openai import AzureOpenAI
import re
import json
import numpy as np
import os
import random
import time


cot_prompt1 = """Answer the following question: {input}

    Make a strategy then write. Your output should be of the following format:
    
    Strategy:
    Your strategy about how to answer the question.
    
    """

cot_prompt2 = """Answer the following question: {input}

    
    {strategy}

    Use the strategy to answer the question. Your output should be of the following format:
    Answer:
    Your answer to the question. It should end with either “the answer is true” or “the answer is false”.
    
    """

vote_prompt = """Given an instruction and several choices, decide which choice is most promising. Analyze each choice in detail, then conclude in the last line "The best choice is <s>", where s the integer id of the choice.
"""

def vote_prompt_wrap(x: str, ys: list) -> str:
    prompt = vote_prompt
    for i, y in enumerate(ys, 1):
        # y = y.replace('Plan:\n', '')
        # TODO: truncate the plan part?
        prompt += f'Choice {i}:\n{y}\n'
    return prompt

def vote_outputs_unwrap(vote_outputs: list, n_candidates: int) -> list:
    vote_results = [0] * n_candidates
    for vote_output in vote_outputs:
        pattern = r".*best choice is .*(\d+).*"
        match = re.match(pattern, vote_output, re.DOTALL)
        if match:
            vote = int(match.groups()[0]) - 1
            if vote in range(n_candidates):
                vote_results[vote] += 1
        else:
            print(f'vote no match: {[vote_output]}')
    return vote_results
  
def get_votes(x, ys, n_evaluate_sample):
    vote_prompt = vote_prompt_wrap(x, ys)

    vote_input = [{
    "role": "system",
    "content": "you are an AI assistant",
    }]

    vote_input.append({
        "role": "user",
        "content": vote_prompt,
    })
    
    cur_try=0
    while cur_try<20:

        try:

            response= client.chat.completions.create(model=deployment_name, messages=vote_input,temperature=1.0,n=n_evaluate_sample,max_tokens=1000)
            break

        except Exception as e:
            err = f"Error: {str(e)}"
            print(err)
            time.sleep(120)
            cur_try+=1
            continue

    vote_outputs = []
    vote_outputs.extend([choice.message.content for choice in response.choices])
   
    
    values = vote_outputs_unwrap(vote_outputs, len(ys))
    return values



def get_samples1(x, y, n_generate_sample):
  
    cot_prompt = cot_prompt1.format(input=x)

    cot_input = [{
    "role": "system",
    "content": "you are an AI assistant",
    }]

    cot_input.append({
        "role": "user",
        "content": cot_prompt,
    })
    
    cur_try=0
    while cur_try<20:

        try:

            response= client.chat.completions.create(model=deployment_name, messages=cot_input,temperature=1.0,n=n_generate_sample,max_tokens=1000)
            break

        except Exception as e:
            err = f"Error: {str(e)}"
            print(err)
            time.sleep(120)
            cur_try+=1
            continue

    samples = []
    samples.extend([choice.message.content for choice in response.choices])
   
    return [y + _ for _ in samples]

def get_samples2(x, y, n_generate_sample):
  
    cot_prompt = cot_prompt2.format(input=x,strategy = y)

    cot_input = [{
    "role": "system",
    "content": "you are an AI assistant",
    }]

    cot_input.append({
        "role": "user",
        "content": cot_prompt,
    })
    
    cur_try=0
    while cur_try<20:

        try:
            response= client.chat.completions.create(model=deployment_name, messages=cot_input,temperature=1.0,n=n_generate_sample,max_tokens=1000)
            break

        except Exception as e:
            err = f"Error: {str(e)}"
            print(err)
            time.sleep(120)
            cur_try+=1
            continue

    samples = []
    samples.extend([choice.message.content for choice in response.choices])
   
    return [y + _ for _ in samples]

def solve( x):
    
    
    ys = ['']  # current output candidates
    infos = []
    for step in range(2):
        # generation
        if step==0:

            new_ys = [get_samples1(x, y, 5) for y in ys]
        else:
            new_ys = [get_samples2(x, y, 5) for y in ys]
        
        new_ys = list(itertools.chain(*new_ys))
        ids = list(range(len(new_ys)))
        # evaluation
        
        values = get_votes(x, new_ys, 5)
        
        # selection
       
     
        select_ids = sorted(ids, key=lambda x: values[x], reverse=True)[:1]
        select_new_ys = [new_ys[select_id] for select_id in select_ids]

        # log
        
        sorted_new_ys, sorted_values = zip(*sorted(zip(new_ys, values), key=lambda x: x[1], reverse=True))
        print(f'-- new_ys --: {sorted_new_ys}\n-- sol values --: {sorted_values}\n-- choices --: {select_new_ys}\n')
        
        ys = select_new_ys
    
    
    print(ys)

    char_list_response = ys[0].split('Answer:')[-1]
    if 'False' in char_list_response or 'false' in char_list_response or 'not true' in char_list_response:
        answer= 'False'
    else:
        answer= 'True'

    print("answer>>",answer)
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

    
    answer = solve(question)
    
    
        
    if str(answer) == str(data[idx]['answer']):
        print("correct answer$$$$")
        correct+=1
    else:
        print("incorrect answer!!!!")


    
        
        

    print("Number of correct answers till now>>>",correct)
    print("Total questions till now>>>",count)

print("Total number of correct answers>>",correct)



