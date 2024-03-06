
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


    
for node_tup in graph_info_lists:
    
        
            
    A[node_tup[0]-1,node_tup[1]-1] = 1
    A[node_tup[1]-1,node_tup[0]-1] = 1


all_rewards_step2 = []
all_frac_invalid_moves_step2 = []
all_solved_step2 = []

all_rewards_step3 = []
all_frac_invalid_moves_step3 = []
all_solved_step3 = []

all_rewards_step4 = []
all_frac_invalid_moves_step4 = []
all_solved_step4 = []
total_invalid_moves = 0
total_moves = 0 
count_step2 = 0 
optimal_llmpfc_steps = []
for file in os.listdir(args.output_dir):
    if "optimal_steps_2" in file:
        count_step2+=1

        target_room = int(file.split("_")[1])
        file_baseline = open(os.path.join(args.output_dir,file), 'r')
        lines_baseline = file_baseline.read().splitlines()
        file_baseline.close()

        task_index = 0 
        for i in range(len(lines_baseline)):
        
            if "Here is the task:" in lines_baseline[i]:
                task_index = i

        for i in range(task_index,len(lines_baseline)):
            if "List of rooms visited" in lines_baseline[i]:
                rooms_splits = json.loads(lines_baseline[i].split("=")[1])



        total_reward = 0 
        num_invalid_moves = 0
        solved_without_invalid = 0 
        num_moves =  min(len(rooms_splits) -1, 6)
        total_moves+=num_moves
        for k in range(num_moves):

            total_reward+=-1

            if A[int(rooms_splits[k])-1,int(rooms_splits[k+1])-1]!=1:
                total_reward+=-10
                num_invalid_moves+=1
                total_invalid_moves+=1

    #             print("Invalid move because room {} is not connected to room {}.".format(int(rooms_splits[k]),int(rooms_splits[k+1])))

    #     print(num_moves, rooms_splits[num_moves])
        if int(rooms_splits[num_moves])==target_room and num_invalid_moves==0:
    #         print("yes")

            total_reward+=10

            solved_without_invalid = 1
            optimal_llmpfc_steps.append((2,num_moves))
        all_rewards_step2.append(total_reward)
        all_frac_invalid_moves_step2.append(num_invalid_moves/num_moves)
        all_solved_step2.append(solved_without_invalid)
print("for 2 step path>>")
print("fraction solved without invalid>>>",np.mean(np.array(all_solved_step2)))
print("fraction invalid>>",np.mean(np.array(all_frac_invalid_moves_step2)))
# print("Average reward>>>",np.mean(np.array(all_rewards_step2)))


count_step3 = 0 
for file in os.listdir(args.output_dir):
    if "optimal_steps_3" in file:
        count_step3+=1

        target_room = int(file.split("_")[1])
        file_baseline = open(os.path.join(args.output_dir,file), 'r')
        lines_baseline = file_baseline.read().splitlines()
        file_baseline.close()

        task_index = 0 
        for i in range(len(lines_baseline)):
        
            if "Here is the task:" in lines_baseline[i]:
                task_index = i

        for i in range(task_index,len(lines_baseline)):
            if "List of rooms visited" in lines_baseline[i]:
                rooms_splits = json.loads(lines_baseline[i].split("=")[1])



        total_reward = 0 
        num_invalid_moves = 0
        solved_without_invalid = 0 
        num_moves =  min(len(rooms_splits) -1, 6)
        total_moves+=num_moves
        for k in range(num_moves):

            total_reward+=-1

            if A[int(rooms_splits[k])-1,int(rooms_splits[k+1])-1]!=1:
                total_reward+=-10
                num_invalid_moves+=1
                total_invalid_moves+=1

    #             print("Invalid move because room {} is not connected to room {}.".format(int(rooms_splits[k]),int(rooms_splits[k+1])))

    #     print(num_moves, rooms_splits[num_moves])
        if int(rooms_splits[num_moves])==target_room and num_invalid_moves==0:
    #         print("yes")

            total_reward+=10

            solved_without_invalid = 1
            optimal_llmpfc_steps.append((3,num_moves))
        all_rewards_step3.append(total_reward)
        all_frac_invalid_moves_step3.append(num_invalid_moves/num_moves)
        all_solved_step3.append(solved_without_invalid)
print("for 3 step path>>")
print("fraction solved without invalid>>>",np.mean(np.array(all_solved_step3)))
print("fraction invalid>>",np.mean(np.array(all_frac_invalid_moves_step3)))

count_step4 = 0 
for file in os.listdir(args.output_dir):
    if "optimal_steps_4" in file:
        count_step4+=1

        target_room = int(file.split("_")[1])
        file_baseline = open(os.path.join(args.output_dir,file), 'r')
        lines_baseline = file_baseline.read().splitlines()
        file_baseline.close()

        task_index = 0 
        for i in range(len(lines_baseline)):
        
            if "Here is the task:" in lines_baseline[i]:
                task_index = i

        for i in range(task_index,len(lines_baseline)):
            if "List of rooms visited" in lines_baseline[i]:
                rooms_splits = json.loads(lines_baseline[i].split("=")[1])



        total_reward = 0 
        num_invalid_moves = 0
        solved_without_invalid = 0 
        num_moves =  min(len(rooms_splits) -1, 6)
        total_moves+=num_moves
        for k in range(num_moves):

            total_reward+=-1

            if A[int(rooms_splits[k])-1,int(rooms_splits[k+1])-1]!=1:
                total_reward+=-10
                num_invalid_moves+=1
                total_invalid_moves+=1

    #             print("Invalid move because room {} is not connected to room {}.".format(int(rooms_splits[k]),int(rooms_splits[k+1])))

    #     print(num_moves, rooms_splits[num_moves])
        if int(rooms_splits[num_moves])==target_room and num_invalid_moves==0:
    #         print("yes")

            total_reward+=10

            solved_without_invalid = 1
            optimal_llmpfc_steps.append((4,num_moves))
        all_rewards_step4.append(total_reward)
        all_frac_invalid_moves_step4.append(num_invalid_moves/num_moves)
        all_solved_step4.append(solved_without_invalid)
print("for 4 step path>>")
print("fraction solved without invalid>>>",np.mean(np.array(all_solved_step4)))
print("fraction invalid>>",np.mean(np.array(all_frac_invalid_moves_step4)))
