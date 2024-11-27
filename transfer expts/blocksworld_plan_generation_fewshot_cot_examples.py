standard_prompt = '''

Example 1:

Starting state:
As initial conditions I have that, the red block is clear, the blue block is clear, the yellow block is clear, the hand is empty, the blue block is on top of the orange block, the red block is on the table, the orange block is on the table and the yellow block is on the table.

Goal:
My goal is to have that the orange block is on top of the blue block.

My plan is as follows:

[PLAN]
1. Current state: the red block is clear, the blue block is clear, the yellow block is clear, the hand is empty, the blue block is on top of the orange block, the red block is on the table, the orange block is on the table and the yellow block is on the table
Action: [START] unstack the blue block from on top of the orange block [END]
Reason: The above action is applicable in the current state because its preconditions; the blue block is clear, the hand is empty and the blue block is on top of the orange block, are satisfied in the current state.
Resulting State: the red block is clear, the orange block is clear, the yellow block is clear, the hand is currently holding blue block, the red block is on the table, the orange block is on the table and the yellow block is on the table

2. Current State: the red block is clear, the orange block is clear, the yellow block is clear, the hand is currently holding blue block, the red block is on the table, the orange block is on the table and the yellow block is on the table
Action: [START] put down the blue block [END]
Reason: The above action is applicable in the current state because its preconditions; the hand is currently holding blue block, are satisfied in the current state.
Resulting State: the red block is clear, the blue block is clear, the orange block is clear, the yellow block is clear, the hand is empty, the red block is on the table, the blue block is on the table, the orange block is on the table and the yellow block is on the table

3. Current State: the red block is clear, the blue block is clear, the orange block is clear, the yellow block is clear, the hand is empty, the red block is on the table, the blue block is on the table, the orange block is on the table and the yellow block is on the table
Action: [START] pick up the orange block [END]
Reason: The above action is applicable in the current state because its preconditions; the orange block is clear, the hand is empty and the orange block is on the table, are satisfied in the current state.
Resulting State: the red block is clear, the blue block is clear, the yellow block is clear, the hand is currently holding orange block, the red block is on the table, the blue block is on the table and the yellow block is on the table

4. Current State: the red block is clear, the blue block is clear, the yellow block is clear, the hand is currently holding orange block, the red block is on the table, the blue block is on the table and the yellow block is on the table
Action: [START] stack the orange block on top of the blue block [END]
Reason: The above action is applicable in the current state because its preconditions; the blue block is clear and the hand is currently holding orange block, are satisfied in the current state.
Resulting State: the red block is clear, the orange block is clear, the yellow block is clear, the hand is empty, the orange block is on top of the blue block, the red block is on the table, the blue block is on the table and the yellow block is on the table

Final State: the red block is clear, the orange block is clear, the yellow block is clear, the hand is empty, the orange block is on top of the blue block, the red block is on the table, the blue block is on the table and the yellow block is on the table
The goal conditions are satisfied in the final state. Hence, the above plan is valid.
[PLAN END]


Example 2:

Starting state:
As initial conditions I have that, the red block is clear, the yellow block is clear, the hand is empty, the red block is on top of the blue block, the yellow block is on top of the orange block, the blue block is on the table and the orange block is on the table.

Goal:
My goal is to have that the orange block is on top of the red block.

My plan is as follows:

[PLAN]
1. Current state: the red block is clear, the yellow block is clear, the hand is empty, the red block is on top of the blue block, the yellow block is on top of the orange block, the blue block is on the table and the orange block is on the table
Action: [START] unstack the yellow block from on top of the orange block [END]
Reason: The above action is applicable in the current state because its preconditions; the yellow block is clear, the hand is empty and the yellow block is on top of the orange block, are satisfied in the current state.
Resulting State: the red block is clear, the orange block is clear, the hand is currently holding yellow block, the red block is on top of the blue block, the blue block is on the table and the orange block is on the table

2. Current state: the red block is clear, the orange block is clear, the hand is currently holding yellow block, the red block is on top of the blue block, the blue block is on the table and the orange block is on the table
Action: [START] put down the yellow block [END]
Reason: The above action is applicable in the current state because its preconditions; the hand is currently holding yellow block, are satisfied in the current state.
Resulting State: the red block is clear, the orange block is clear, the yellow block is clear, the hand is empty, the red block is on top of the blue block, the yellow block is on the table, the blue block is on the table and the orange block is on the table

3. Current state: the red block is clear, the orange block is clear, the yellow block is clear, the hand is empty, the red block is on top of the blue block, the yellow block is on the table, the blue block is on the table and the orange block is on the table
Action: [START] pick up the orange block [END]
Reason: The above action is applicable in the current state because its preconditions; the orange block is clear, the hand is empty and the orange block is on the table, are satisfied in the current state.
Resulting State: the red block is clear, the yellow block is clear, the hand is currently holding orange block, the red block is on top of the blue block, the yellow block is on the table and the blue block is on the table

4. Current state: the red block is clear, the yellow block is clear, the hand is currently holding orange block, the red block is on top of the blue block, the yellow block is on the table and the blue block is on the table
Action: [START] stack the orange block on top of the red block [END]
Reason: The above action is applicable in the current state because its preconditions; the red block is clear and the hand is currently holding orange block, are satisfied in the current state.
Resulting State: the yellow block is clear, the hand is empty, the red block is on top of the blue block, the orange block is on top of the red block, the yellow block is on the table and the blue block is on the table

Final State: the yellow block is clear, the hand is empty, the red block is on top of the blue block, the orange block is on top of the red block, the yellow block is on the table and the blue block is on the table
The goal conditions are satisfied in the final state. Hence, the above plan is valid.
[PLAN END]

Example 3:

Starting state:
As initial conditions I have that, the blue block is clear, the hand is empty, the blue block is on top of the orange block, the orange block is on top of the yellow block, the yellow block is on top of the red block and the red block is on the table.

Goal:
My goal is to have that the red block is on top of the orange block and the yellow block is on top of the red block.

My plan is as follows:

[PLAN]
1. Current state: the blue block is clear, the hand is empty, the blue block is on top of the orange block, the orange block is on top of the yellow block, the yellow block is on top of the red block and the red block is on the table
Action: [START] unstack the blue block from on top of the orange block [END]
Reason: The above action is applicable in the current state because its preconditions; the blue block is clear, the hand is empty and the blue block is on top of the orange block, are satisfied in the current state.
Resulting State: the hand is currently holding blue block, the orange block is clear, the orange block is on top of the yellow block, the yellow block is on top of the red block and the red block is on the table

2. Current state: the hand is currently holding blue block, the orange block is clear, the orange block is on top of the yellow block, the yellow block is on top of the red block and the red block is on the table
Action: [START] put down the blue block [END]
Reason: The above action is applicable in the current state because its preconditions; the hand is currently holding blue block, are satisfied in the current state.
Resulting State: the hand is empty, the blue block is clear, the orange block is clear, the orange block is on top of the yellow block, the yellow block is on top of the red block, the red block is on the table and the blue block is on the table

3. Current state: the hand is empty, the blue block is clear, the orange block is clear, the orange block is on top of the yellow block, the yellow block is on top of the red block, the red block is on the table and the blue block is on the table
Action: [START] unstack the orange block from on top of the yellow block [END]
Reason: The above action is applicable in the current state because its preconditions; the orange block is clear, the hand is empty and the orange block is on top of the yellow block, are satisfied in the current state.
Resulting State: the hand is currently holding orange block, the blue block is clear, the yellow block is clear, the yellow block is on top of the red block, the red block is on the table and the blue block is on the table

4. Current state: the hand is currently holding orange block, the blue block is clear, the yellow block is clear, the yellow block is on top of the red block, the red block is on the table and the blue block is on the table
Action: [START] put down the orange block [END]
Reason: The above action is applicable in the current state because its preconditions; the hand is currently holding orange block, are satisfied in the current state.
Resulting State: the hand is empty, the orange block is clear, the blue block is clear, the yellow block is clear, the yellow block is on top of the red block, the red block is on the table, the orange block is on the table and the blue block is on the table


5. Current state: the hand is empty, the orange block is clear, the blue block is clear, the yellow block is clear, the yellow block is on top of the red block, the red block is on the table, the orange block is on the table and the blue block is on the table
Action: [START] unstack the yellow block from on top of the red block [END]
Reason: The above action is applicable in the current state because its preconditions; the yellow block is clear, the hand is empty and the yellow block is on top of the red block, are satisfied in the current state.
Resulting State: the hand is currently holding yellow block, the orange block is clear, the blue block is clear, the red block is clear, the red block is on the table, the orange block is on the table and the blue block is on the table

6. Current state: the hand is currently holding yellow block, the orange block is clear, the blue block is clear, the red block is clear, the red block is on the table, the orange block is on the table and the blue block is on the table
Action: [START] stack the yellow block on top of the blue block [END]
Reason: The above action is applicable in the current state because its preconditions; the blue block is clear and the hand is currently holding yellow block, are satisfied in the current state.
Resulting State: the hand is empty, the orange block is clear, the yellow block is clear, the red block is clear, the yellow block is on top of the blue block, the red block is on the table, the orange block is on the table and the blue block is on the table

7. Current state: the hand is empty, the orange block is clear, the yellow block is clear, the red block is clear, the yellow block is on top of the blue block, the red block is on the table, the orange block is on the table and the blue block is on the table
Action: [START] pick up the red block [END]
Reason: The above action is applicable in the current state because its preconditions; the red block is clear, the hand is empty and the red block is on the table, are satisfied in the current state.
Resulting State: the hand is currently holding red block, the orange block is clear, the yellow block is clear, the yellow block is on top of the blue block, the orange block is on the table and the blue block is on the table


8. Current state: the hand is currently holding red block, the orange block is clear, the yellow block is clear, the yellow block is on top of the blue block, the orange block is on the table and the blue block is on the table
Action: [START] stack the red block on top of the orange block [END]
Reason: The above action is applicable in the current state because its preconditions; the orange block is clear and the hand is currently holding red block, are satisfied in the current state.
Resulting State: the hand is empty, the red block is clear, the yellow block is clear, the red block is on top of the orange block, the yellow block is on top of the blue block, the orange block is on the table and the blue block is on the table

9. Current state: the hand is empty, the red block is clear, the yellow block is clear, the red block is on top of the orange block, the yellow block is on top of the blue block, the orange block is on the table and the blue block is on the table
Action: [START] unstack the yellow block from on top of the blue block [END]
Reason: The above action is applicable in the current state because its preconditions; the yellow block is clear, the hand is empty and the yellow block is on top of the blue block, are satisfied in the current state.
Resulting State: the hand is currently holding yellow block, the red block is clear, the blue block is clear, the red block is on top of the orange block, the orange block is on the table and the blue block is on the table

10. Current state: the hand is currently holding yellow block, the red block is clear, the blue block is clear, the red block is on top of the orange block, the orange block is on the table and the blue block is on the table
Action: [START] stack the yellow block on top of the red block [END]
Reason: The above action is applicable in the current state because its preconditions; the red block is clear and the hand is currently holding yellow block, are satisfied in the current state.
Resulting State: the hand is empty, the yellow block is clear, the blue block is clear, the red block is on top of the orange block, the yellow block is on top of the red block, the orange block is on the table and the blue block is on the table

Final State: the hand is empty, the yellow block is clear, the blue block is clear, the red block is on top of the orange block, the yellow block is on top of the red block, the orange block is on the table and the blue block is on the table
The goal conditions are satisfied in the final state. Hence, the above plan is valid.
[PLAN END]

'''