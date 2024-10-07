standard_prompt = '''

Example 1:

Starting state:
As initial conditions I have that, object b craves object c, harmony, planet object a, planet object c, planet object d, province object a, province object b and province object d.

Goal:
My goal is to have that object c craves object b.

My actions to achieve the goal from the starting state:

[PLAN]
[START] feast object b from object c [END]
[START] succumb object b [END]
[START] attack object c [END]
[START] overcome object c from object b [END]
[PLAN END]


Example 2:

Starting state:
As initial conditions I have that, object a craves object b, object d craves object c, harmony, planet object b, planet object c, province object a and province object d.

Goal:
My goal is to have that object c craves object a.

My actions to achieve the goal from the starting state:

[PLAN]
[START] feast object d from object c [END]
[START] succumb object d [END]
[START] attack object c [END]
[START] overcome object c from object a [END]
[PLAN END]

Example 3:

Starting state:
As initial conditions I have that, object b craves object c, object c craves object d, object d craves object a, harmony, planet object a and province object b.

Goal:
My goal is to have that object a craves object c and object d craves object a.

My actions to achieve the goal from the starting state:

[PLAN]
[START] feast object b from object c [END]
[START] succumb object b [END]
[START] feast object c from object d [END]
[START] succumb object c [END]
[START] feast object d from object a [END]
[START] overcome object d from object b [END]
[START] attack object a [END]
[START] overcome object a from object c [END]
[START] feast object d from object b [END]
[START] overcome object d from object a [END]
[PLAN END]

'''