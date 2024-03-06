import json
import os
import argparse
import numpy as np

from copy import deepcopy

parser = argparse.ArgumentParser()

parser.add_argument


parser.add_argument('--output_dir',type=str, help='directory name where output log files are stored', required= True)

args = parser.parse_args()
print(args)

graph_info_lists = [(1,7), (1,10),(1,13),(1,11), 
(2,5), (2,8),(2,11),(2,14) ,
(3,6), (3,9),(3,12),(3,8), 
(4,7), (4,10),(4,13),(4,15), 
(5,8), (5,11),(5,14), 
(6,9), (6,12),(6,15), 
(7,10), (7,13),  
(8,14), (9,12), (9,15),
              (10,13), (11,14),(12,15)]

A=np.zeros((15,15))

reward_rooms = [8,15]
reward_values = [12,48]
    
for node_tup in graph_info_lists:
    
        
            
    A[node_tup[0]-1,node_tup[1]-1] = 1
    A[node_tup[1]-1,node_tup[0]-1] = 1


all_rewards = []
all_frac_invalid_moves = []
all_solved = []

optimal_zeroshot_steps = []
# solved_1step = []
# solved_2step = []
# solved_4step = []
# total_invalid_moves_1 = 0
# total_moves_1 = 0
# total_invalid_moves_2 = 0
# total_moves_2 = 0
# total_invalid_moves_4 = 0
# total_moves_4 = 0
total_invalid_moves = 0 
total_moves = 0 
for file in os.listdir(args.output_dir):
    file_no = int(file.split(".")[0][7:])
    
    
    
    file_baseline = open(os.path.join(args.output_dir,file), 'r')
    lines_baseline = file_baseline.read().splitlines()
    file_baseline.close()
    
    
    for i in range(len(lines_baseline)):
        if "GPT-4 Response after rewardReval >>>>>>>" in lines_baseline[i]:
            count = i
            while "that yields the most reward is:" not in lines_baseline[count]:
                count+=1

            rooms_splits = lines_baseline[count].split(":")[1].strip().replace(".","").split(",")


  
            

    
    total_reward = 0 
    num_invalid_moves = 0
    solved_without_invalid = 0 
    num_moves = min(6,len(rooms_splits)-1)
    total_moves+=num_moves
#     if valuepath_optimal_steps[file_no-1]==1:
        
#         total_moves_1+=num_moves
#     elif valuepath_optimal_steps[file_no-1]==2:
#         total_moves_2+=num_moves
#     elif valuepath_optimal_steps[file_no-1]==4:
#         total_moves_4+=num_moves
    for k in range(num_moves):

        total_reward+=-1

        if A[int(rooms_splits[k])-1,int(rooms_splits[k+1])-1]!=1:
            total_reward+=-10
            num_invalid_moves+=1
#             if valuepath_optimal_steps[file_no-1]==1:
        
#                 total_invalid_moves_1+=1
#             elif valuepath_optimal_steps[file_no-1]==2:
#                 total_invalid_moves_2+=1
#             elif valuepath_optimal_steps[file_no-1]==4:
#                 total_invalid_moves_4+=1
            
            total_invalid_moves+=1

#             print("Invalid move because room {} is not connected to room {}.".format(int(rooms_splits[k]),int(rooms_splits[k+1])))

    
    if int(rooms_splits[num_moves]) in reward_rooms and num_invalid_moves==0:

        total_reward+=reward_values[reward_rooms.index(int(rooms_splits[num_moves]))]
        if int(rooms_splits[num_moves])==15:
            print(file_no)
#             optimal_zeroshot_steps.append((valuepath_optimal_steps[file_no-1],num_moves))
            solved_without_invalid = 1
    all_rewards.append(total_reward)
    all_frac_invalid_moves.append(num_invalid_moves/num_moves)
#     if valuepath_optimal_steps[file_no-1]==1:
        
#         solved_1step.append(solved_without_invalid)
#     elif valuepath_optimal_steps[file_no-1]==2:
#         solved_2step.append(solved_without_invalid)
#     elif valuepath_optimal_steps[file_no-1]==4:
#         solved_4step.append(solved_without_invalid)
    all_solved.append(solved_without_invalid)

print("fraction solved without invalid>>>",np.mean(np.array(all_solved)))
print("fraction invalid>>",np.mean(np.array(all_frac_invalid_moves)))
