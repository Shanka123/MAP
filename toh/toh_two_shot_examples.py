# few shot examples for solving tower of hanoi
# problem3.log, problem22.log


standard_prompt = '''

	Example 1:

	This is the starting configuration:
	A = [0, 1]
	B = [2]
	C = []
	This is the goal configuration:
	A = []
	B = []
	C = [0, 1, 2]
	
	Here is the sequence of minimum number of moves to reach the goal configuration from the starting configuration:

	Move 2 from B to C.
	A = [0, 1]
	B = []
	C = [2]

	Move 1 from A to B.
	A = [0]
	B = [1]
	C = [2]

	Move 2 from C to B.
	A = [0]
	B = [1, 2]
	C = []

	Move 0 from A to C.
	A = []
	B = [1, 2]
	C = [0]

	Move 2 from B to A.
	A = [2]
	B = [1]
	C = [0]

	Move 1 from B to C.
	A = [2]
	B = []
	C = [0, 1]

	Move 2 from A to C.
	A = []
	B = []
	C = [0, 1, 2]
	

	Example 2:

	This is the starting configuration::
	A = [1]
	B = [0]
	C = [2]
	This is the goal configuration:
	A = []
	B = []
	C = [0, 1, 2]

	Here is the sequence of minimum number of moves to reach the goal configuration from the starting configuration:

	Move 2 from C to A.
	A = [1, 2]
	B = [0]
	C = []

	Move 0 from B to C.
	A = [1, 2]
	B = []
	C = [0]

	Move 2 from A to B.
	A = [1]
	B = [2]
	C = [0]

	Move 1 from A to C.
	A = []
	B = [2]
	C = [0, 1]

	Move 2 from B to C.
	A = []
	B = []
	C = [0, 1, 2]


	
'''




