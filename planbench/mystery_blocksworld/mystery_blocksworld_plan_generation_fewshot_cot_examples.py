standard_prompt = '''

Example 1:

Starting state:
As initial conditions I have that, object b craves object c, harmony, planet object a, planet object c, planet object d, province object a, province object b and province object d.

Goal:
My goal is to have that object c craves object b.

My plan is as follows:

[PLAN]
1. Current State: object b craves object c, harmony, planet object a, planet object c, planet object d, province object a, province object b and province object d
Action: [START] feast object b from object c [END]
Reason: The above action is applicable in the current state because its preconditions; object b craves object c, harmony and province object b, are satisfied in the current state.
Resulting State: pain object b, planet object a, planet object c, planet object d, province object a, province object c and province object d

2. Current State: pain object b, planet object a, planet object c, planet object d, province object a, province object c and province object d
Action: [START] succumb object b [END]
Reason: The above action is applicable in the current state because its preconditions; pain object b, are satisfied in the current state.
Resulting State: harmony, planet object a, planet object b, planet object c, planet object d, province object a, province object b, province object c and province object d

3. Current State: harmony, planet object a, planet object b, planet object c, planet object d, province object a, province object b, province object c and province object d
Action: [START] attack object c [END]
Reason: The above action is applicable in the current state because its preconditions; harmony, planet object c and province object c, are satisfied in the current state.
Resulting State: pain object c, planet object a, planet object b, planet object d, province object a, province object b and province object d

4. Current State: pain object c, planet object a, planet object b, planet object d, province object a, province object b and province object d
Action: [START] overcome object c from object b [END]
Reason: The above action is applicable in the current state because its preconditions; pain object c and province object b, are satisfied in the current state.
Resulting State: object c craves object b, harmony, planet object a, planet object b, planet object d, province object a, province object c and province object d

Final State: object c craves object b, harmony, planet object a, planet object b, planet object d, province object a, province object c and province object d
The goal conditions are satisfied in the final state. Hence, the above plan is valid.
[PLAN END]



Example 2:

Starting state:
As initial conditions I have that, object a craves object b, object d craves object c, harmony, planet object b, planet object c, province object a and province object d.

Goal:
My goal is to have that object c craves object a.


My plan is as follows:

[PLAN]
1. Current State: object a craves object b, object d craves object c, harmony, planet object b, planet object c, province object a and province object d
Action: [START] feast object d from object c [END]
Reason: The above action is applicable in the current state because its preconditions; object d craves object c, harmony and province object d, are satisfied in the current state.
Resulting State: pain object d, object a craves object b, planet object b, planet object c, province object a and province object c

2. Current State: pain object d, object a craves object b, planet object b, planet object c, province object a and province object c
Action: [START] succumb object d [END]
Reason: The above action is applicable in the current state because its preconditions; pain object d, are satisfied in the current state.
Resulting State: harmony, object a craves object b, planet object b, planet object c, planet object d, province object a, province object c and province object d

3. Current State: harmony, object a craves object b, planet object b, planet object c, planet object d, province object a, province object c and province object d
Action: [START] attack object c [END]
Reason: The above action is applicable in the current state because its preconditions; harmony, planet object c and province object c, are satisfied in the current state.
Resulting State: pain object c, object a craves object b, planet object b, planet object d, province object a and province object d

4. Current State: pain object c, object a craves object b, planet object b, planet object d, province object a and province object d
Action: [START] overcome object c from object a [END]
Reason: The above action is applicable in the current state because its preconditions; pain object c and province object a, are satisfied in the current state.
Resulting State: object c craves object a, object a craves object b, harmony, planet object b, planet object d, province object c and province object d

Final State: object c craves object a, object a craves object b, harmony, planet object b, planet object d, province object c and province object d
The goal conditions are satisfied in the final state. Hence, the above plan is valid.
[PLAN END]



Example 3:

Starting state:
As initial conditions I have that, object b craves object c, object c craves object d, object d craves object a, harmony, planet object a and province object b.

Goal:
My goal is to have that object a craves object c and object d craves object a.

My plan is as follows:

[PLAN]
1. Current State: object b craves object c, object c craves object d, object d craves object a, harmony, planet object a and province object b
Action: [START] feast object b from object c [END]
Reason: The above action is applicable in the current state because its preconditions; object b craves object c, harmony and province object b, are satisfied in the current state.
Resulting State: pain object b, object c craves object d, object d craves object a, planet object a and province object c

2. Current State: pain object b, object c craves object d, object d craves object a, planet object a and province object c
Action: [START] succumb object b [END]
Reason: The above action is applicable in the current state because its preconditions; pain object b, are satisfied in the current state.
Resulting State: harmony, object c craves object d, object d craves object a, planet object a, planet object b, province object b and province object c

3. Current State: harmony, object c craves object d, object d craves object a, planet object a, planet object b, province object b and province object c
Action: [START] feast object c from object d [END]
Reason: The above action is applicable in the current state because its preconditions; object c craves object d, harmony and province object c, are satisfied in the current state.
Resulting State: pain object c, object d craves object a, planet object a, planet object b, province object b and province object d

4. Current State: pain object c, object d craves object a, planet object a, planet object b, province object b and province object d
Action: [START] succumb object c [END]
Reason: The above action is applicable in the current state because its preconditions; pain object c, are satisfied in the current state.
Resulting State: harmony, object d craves object a, planet object a, planet object b, planet object c, province object b, province object c and province object d

5. Current State: harmony, object d craves object a, planet object a, planet object b, planet object c, province object b, province object c and province object d
Action: [START] feast object d from object a [END]
Reason: The above action is applicable in the current state because its preconditions; object d craves object a, harmony and province object d, are satisfied in the current state.
Resulting State: pain object d, planet object a, planet object b, planet object c, province object a, province object b and province object c

6. Current State: pain object d, planet object a, planet object b, planet object c, province object a, province object b and province object c
Action: [START] overcome object d from object b [END]
Reason: The above action is applicable in the current state because its preconditions; pain object d and province object b, are satisfied in the current state.
Resulting State: harmony, object d craves object b, planet object a, planet object b, planet object c, province object a, province object c and province object d

7. Current State: harmony, object d craves object b, planet object a, planet object b, planet object c, province object a, province object c and province object d
Action: [START] attack object a [END]
Reason: The above action is applicable in the current state because its preconditions; harmony, planet object a and province object a, are satisfied in the current state.
Resulting State: pain object a, object d craves object b, planet object b, planet object c, province object c and province object d

8. Current State: pain object a, object d craves object b, planet object b, planet object c, province object c and province object d
Action: [START] overcome object a from object c [END]
Reason: The above action is applicable in the current state because its preconditions; pain object a and province object c, are satisfied in the current state.
Resulting State: harmony, object a craves object c, object d craves object b, planet object b, planet object c, province object a and province object d

9. Current State: harmony, object a craves object c, object d craves object b, planet object b, planet object c, province object a and province object d
Action: [START] feast object d from object b [END]
Reason: The above action is applicable in the current state because its preconditions; object d craves object b, harmony and province object d, are satisfied in the current state.
Resulting State: pain object d, object a craves object c, planet object b, planet object c, province object a and province object b

10. Current State: pain object d, object a craves object c, planet object b, planet object c, province object a and province object b
Action: [START] overcome object d from object a [END]
Reason: The above action is applicable in the current state because its preconditions; pain object d and province object a, are satisfied in the current state.
Resulting State: harmony, object a craves object c, object d craves object a, planet object b, planet object c, province object b and province object d

Final State: harmony, object a craves object c, object d craves object a, planet object b, planet object c, province object b and province object d
The goal conditions are satisfied in the final state. Hence, the above plan is valid.
[PLAN END]


'''