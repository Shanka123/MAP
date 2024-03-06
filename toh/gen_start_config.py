
import random
import numpy as np
def generate_all_start_config():
	all_As = []
	all_Bs = []
	all_Cs = []
	int_arr_mapping = {0:all_As,1:all_Bs,2:all_Cs}

	# 3 disks

	all_As.append([0,1,2])
	all_Bs.append([])
	all_Cs.append([])

	all_As.append([])
	all_Bs.append([0,1,2])
	all_Cs.append([])

	tuples_2_1 = [([0,1],[2]),([1,2],[0]),([0,2],[1])]
	for i in range(3):
		for j in range(i+1,3):
			for tup in tuples_2_1:
				int_arr_mapping[i].append(tup[0])
				int_arr_mapping[j].append(tup[1])
				int_arr_mapping[3-i-j].append([])

				int_arr_mapping[i].append(tup[1])
				int_arr_mapping[j].append(tup[0])
				int_arr_mapping[3-i-j].append([])
	tuples_1_1_1 = [([0],[1],[2])]
	for i in range(3):
		for j in range(i+1,3):
			for tup in tuples_1_1_1:
				int_arr_mapping[i].append(tup[0])
				int_arr_mapping[j].append(tup[1])
				int_arr_mapping[3-i-j].append(tup[2])
				int_arr_mapping[i].append(tup[1])
				int_arr_mapping[j].append(tup[0])
				int_arr_mapping[3-i-j].append(tup[2])





	# 4 disks
	all_As.append([0,1,2,3])
	all_Bs.append([])
	all_Cs.append([])

	all_As.append([])
	all_Bs.append([0,1,2,3])
	all_Cs.append([])

	tuples_3_1 = [([0,1,2],[3]),([0,2,3],[1]),([1,2,3],[0]),([0,1,3],[2])]

	tuples_2_2 = [([0,1],[2,3]),([0,2],[1,3]),([0,3],[1,2])]
	tuples_2_1_1 = [([0,1],[2],[3]),([0,2],[1],[3]),([0,3],[1],[2]),([1,2],[0],[3]),([2,3],[0],[1]),([1,3],[0],[2])]

	for i in range(3):
		for j in range(i+1,3):
			for tup in tuples_3_1:
				int_arr_mapping[i].append(tup[0])
				int_arr_mapping[j].append(tup[1])
				int_arr_mapping[3-i-j].append([])

				int_arr_mapping[i].append(tup[1])
				int_arr_mapping[j].append(tup[0])
				int_arr_mapping[3-i-j].append([])

	for i in range(3):
		for j in range(i+1,3):
			for tup in tuples_2_2:
				int_arr_mapping[i].append(tup[0])
				int_arr_mapping[j].append(tup[1])
				int_arr_mapping[3-i-j].append([])

				int_arr_mapping[i].append(tup[1])
				int_arr_mapping[j].append(tup[0])
				int_arr_mapping[3-i-j].append([])

	for i in range(3):
		for j in range(i+1,3):
			for tup in tuples_2_1_1:
				int_arr_mapping[i].append(tup[0])
				int_arr_mapping[j].append(tup[1])
				int_arr_mapping[3-i-j].append(tup[2])
				int_arr_mapping[i].append(tup[1])
				int_arr_mapping[j].append(tup[0])
				int_arr_mapping[3-i-j].append(tup[2])






	# 5 disks

	all_As.append([0,1,2,3,4])
	all_Bs.append([])
	all_Cs.append([])

	all_As.append([])
	all_Bs.append([0,1,2,3,4])
	all_Cs.append([])

	tuples_4_1 = [([0,1,2,3],[4]),([0,1,2,4],[3]),([0,1,3,4],[2]),([0,2,3,4],[1]),([1,2,3,4],[0])]

	tuples_3_2 = [([0,1,2],[3,4]),([0,1,3],[2,4]),([0,3,4],[1,2]),([1,2,3],[0,4]),([1,3,4],[0,2]),([2,3,4],[0,1]),([0,1,4],[2,3]),([0,2,4],[1,3]),([0,2,3],[1,4]),([1,2,4],[0,3])] 

	tuples_2_2_1 = [([0,1],[2,3],[4]),([0,2],[1,3],[4]),([0,3],[1,2],[4]), ([0,1],[2,4],[3]),([0,2],[1,4],[3]),([0,4],[1,2],[3]), ([0,1],[3,4],[2]),([0,3],[1,4],[2]),([0,4],[1,3],[2]), ([0,2],[3,4],[1]),([0,3],[2,4],[1]),([0,4],[2,3],[1]), ([1,2],[3,4],[0]),([1,3],[2,4],[0]),([1,4],[2,3],[0])]

	tuples_3_1_1 = [([0,1,2],[3],[4]),([0,1,3],[2],[4]),([0,3,4],[1],[2]),([1,2,3],[0],[4]),([1,3,4],[0],[2]),([2,3,4],[0],[1]),([0,1,4],[2],[3]),([0,2,4],[1],[3]),([0,2,3],[1],[4]),([1,2,4],[0],[3])] 

	for i in range(3):
		for j in range(i+1,3):
			for tup in tuples_4_1:
				int_arr_mapping[i].append(tup[0])
				int_arr_mapping[j].append(tup[1])
				int_arr_mapping[3-i-j].append([])

				int_arr_mapping[i].append(tup[1])
				int_arr_mapping[j].append(tup[0])
				int_arr_mapping[3-i-j].append([])

	for i in range(3):
		for j in range(i+1,3):
			for tup in tuples_3_2:
				int_arr_mapping[i].append(tup[0])
				int_arr_mapping[j].append(tup[1])
				int_arr_mapping[3-i-j].append([])

				int_arr_mapping[i].append(tup[1])
				int_arr_mapping[j].append(tup[0])
				int_arr_mapping[3-i-j].append([])

	for i in range(3):
		for j in range(i+1,3):
			for tup in tuples_2_2_1:
				int_arr_mapping[i].append(tup[0])
				int_arr_mapping[j].append(tup[1])
				int_arr_mapping[3-i-j].append(tup[2])
				int_arr_mapping[i].append(tup[1])
				int_arr_mapping[j].append(tup[0])
				int_arr_mapping[3-i-j].append(tup[2])


	for i in range(3):
		for j in range(i+1,3):
			for tup in tuples_3_1_1:
				int_arr_mapping[i].append(tup[0])
				int_arr_mapping[j].append(tup[1])
				int_arr_mapping[3-i-j].append(tup[2])
				int_arr_mapping[i].append(tup[1])
				int_arr_mapping[j].append(tup[0])
				int_arr_mapping[3-i-j].append(tup[2])




	return all_As, all_Bs, all_Cs
	



	
