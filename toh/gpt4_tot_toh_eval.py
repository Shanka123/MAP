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


total_moves = 0 
total_invalid_moves = 0 
icl_exs = [3,22]
all_solved = []
all_solved_best = []
all_solved_v2 = []

for file in os.listdir(args.output_dir):
	if ".pkl" in file:


		with open(os.path.join(args.output_dir,file), 'rb') as input_file:


	
            sols = pickle.load(input_file)

        
        temp_acc = []  
        min_frac_invalid_val = 10000
        for m in range(len(sols)):


            moves_decoded_tuples = []
            all_configuration_after_moves = []
            for s in sols[m]:
                if "Move" in s:
                    moves_decoded_tuples.append((int(s.split(" ")[1]),s.split(" ")[3],s.split(" ")[5]))
                else:
                    all_configuration_after_moves.append(s)

            print(moves_decoded_tuples)
            char_int_mapping = {'A':0,'B':1,'C':2}
            target_configuration = [[],[],[0,1,2]]

            num_invalid_moves = 0
            solved_without_invalid = 0 
            num_moves = min(10,len(moves_decoded_tuples))
            total_moves +=num_moves
            for k in range(num_moves):

                current_configuration = all_configuration_after_moves[k]

                no_to_move = moves_decoded_tuples[k][0]
                source_list = moves_decoded_tuples[k][1]
                target_list = moves_decoded_tuples[k][2]
            #  
                if no_to_move not in current_configuration[char_int_mapping[source_list]]:

            #             print("Invalid move because {} is not in {}".format(no_to_move,source_list))


                    num_invalid_moves+=1
                    total_invalid_moves+=1
                else:
                    if current_configuration[char_int_mapping[source_list]][-1]!= no_to_move:

            #                 print("Invalid move because it violates Rule #1.")

                        num_invalid_moves+=1
                        total_invalid_moves+=1
                    else:
                        if len(current_configuration[char_int_mapping[target_list]]):
                            max_target_list = max(current_configuration[char_int_mapping[target_list]])
                        else:
                            max_target_list = -1

                        if no_to_move < max_target_list:

            #                     print("Invalid move because it violates Rule #2")


                            num_invalid_moves+=1
                            total_invalid_moves+=1

            if (num_invalid_moves/num_moves)< min_frac_invalid_val:
                min_frac_invalid_val = num_invalid_moves/num_moves
            
            if all_configuration_after_moves[num_moves] == target_configuration and num_invalid_moves==0:


                solved_without_invalid=1
            temp_acc.append(solved_without_invalid)
            
            all_solved.append(solved_without_invalid)
        all_solved_v2.append(np.mean(temp_acc))
        if sum(temp_acc)>0:
            all_solved_best.append(1)
        else:
            all_solved_best.append(0)
        
        min_frac_invalid_allprobs.append(min_frac_invalid_val)
        
print("fraction solved without invalid (Best case)>>>",np.mean(np.array(all_solved_best)))
print("fraction solved without invalid (Avg case)>>>",np.mean(np.array(all_solved)))
print("fraction invalid moves>>",total_invalid_moves/total_moves)

            
