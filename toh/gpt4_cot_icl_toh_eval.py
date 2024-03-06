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



total_moves_3disks = 0 
total_invalid_moves_3disks = 0 


total_moves_4disks = 0 
total_invalid_moves_4disks = 0 

frac_solved_3disks = []
frac_solved_4disks = []
for file in os.listdir(args.output_dir):
    
    file_no = int(file.split(".")[0][7:])
        
        
    file_baseline = open(os.path.join(args.output_dir,file), 'r')
    lines_baseline = file_baseline.read().splitlines()
    file_baseline.close()

    initial_A_B_C = []
    char_int_mapping = {'A':0,'B':1,'C':2}
    if file_no<27:

        target_configuration = [[],[],[0,1,2]]
        max_moves = 10
    else:
        target_configuration = [[],[],[0,1,2,3]]
        max_moves = 20
    
    task_index=0
    for q in range(len(lines_baseline)):
        if "Here is the task:" in lines_baseline[q]:
            task_index=q

    for i in range(task_index,len(lines_baseline)):

        if 'This is the starting configuration' in lines_baseline[i]:# or 'Initial configuration' in lines_baseline[i]:
            initial_A_B_C.append(json.loads(lines_baseline[i+1].split("=")[-1]))
            initial_A_B_C.append(json.loads(lines_baseline[i+2].split("=")[-1]))
            initial_A_B_C.append(json.loads(lines_baseline[i+3].split("=")[-1]))
            break

    moves_decoded_tuples = []
    all_configuration_after_moves = []
    all_configuration_after_moves.append(deepcopy(initial_A_B_C))
    for i in range(task_index,len(lines_baseline)):


        if 'Move' in lines_baseline[i] and 'from' in lines_baseline[i] and 'to' in lines_baseline[i] and (('A' in lines_baseline[i] and 'B' in lines_baseline[i] ) or ('C' in lines_baseline[i] and 'B' in lines_baseline[i] ) or ('A' in lines_baseline[i] and 'C' in lines_baseline[i] )):

            if 'Step' in lines_baseline[i]:
                move_line = lines_baseline[i].split('.')[1].replace('.','').strip()

            else:



                move_line = lines_baseline[i].replace('.','').replace(',','').strip()

            if len(moves_decoded_tuples)>0:
                if moves_decoded_tuples[-1] == (int(move_line.split(" ")[1]),move_line.split(" ")[3],move_line.split(" ")[5]):
                    continue
            moves_decoded_tuples.append((int(move_line.split(" ")[1]),move_line.split(" ")[3],move_line.split(" ")[5]))
            count = i

            while ("A =" not in lines_baseline[count]):
                count+=1

            state_output = []

            state_output.append(json.loads(lines_baseline[count].split("=")[-1]))
            state_output.append(json.loads(lines_baseline[count+1].split("=")[-1]))
            state_output.append(json.loads(lines_baseline[count+2].split("=")[-1]))

            all_configuration_after_moves.append(state_output)


    total_reward =0
    num_invalid_moves = 0
    solved_without_invalid = 0 
    num_moves = min(max_moves,len(moves_decoded_tuples))
    if file_no<27:
        total_moves_3disks+=num_moves
    else:
        total_moves_4disks+=num_moves


    for k in range(num_moves):

        current_configuration = all_configuration_after_moves[k]

        no_to_move = moves_decoded_tuples[k][0]
        source_list = moves_decoded_tuples[k][1]
        target_list = moves_decoded_tuples[k][2]
#         print(no_to_move,source_list,target_list)
        total_reward+=-1

        if no_to_move not in current_configuration[char_int_mapping[source_list]]:

#             print("Invalid move because {} is not in {}".format(no_to_move,source_list))

            total_reward+=-10
            num_invalid_moves+=1
        else:
            if current_configuration[char_int_mapping[source_list]][-1]!= no_to_move:

#                 print("Invalid move because it violates Rule #1.")
                total_reward+=-10
                num_invalid_moves+=1
            else:
                if len(current_configuration[char_int_mapping[target_list]]):
                    max_target_list = max(current_configuration[char_int_mapping[target_list]])
                else:
                    max_target_list = -1

                if no_to_move < max_target_list:

#                     print("Invalid move because it violates Rule #2")

                    total_reward+=-10
                    num_invalid_moves+=1

    if file_no<27:
        total_invalid_moves_3disks+=num_invalid_moves
    else:
        total_invalid_moves_4disks+=num_invalid_moves

    if all_configuration_after_moves[num_moves] == target_configuration and num_invalid_moves==0:
   
        solved_without_invalid=1

        total_reward+=100

  
    if file_no<27:

        frac_solved_3disks.append(solved_without_invalid)
    else:
        frac_solved_4disks.append(solved_without_invalid)

print("For 3 disks>>>>")

print("fraction solved without invalid>>>",np.mean(np.array(frac_solved_3disks)))
print("fraction invalid moves>>",total_invalid_moves_3disks/total_moves_3disks)

print("For 4 disks>>>>")

print("fraction solved without invalid>>>",np.mean(np.array(frac_solved_4disks)))
print("fraction invalid moves>>",total_invalid_moves_4disks/total_moves_4disks)
