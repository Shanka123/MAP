standard_prompt = '''

Example 1:

Starting state:
As initial conditions I have that, location_0_0 is an airport, location_1_0 is an airport, airplane_0 is at location_0_0, airplane_1 is at location_0_0, package_0 is at location_1_0, truck_0 is at location_0_0, truck_1 is at location_1_0, location_0_0 is in the city city_0 and location_1_0 is in the city city_1.

Goal:
My goal is to have that package_0 is at location_0_0.

Thoughts: package_0 is initially at location_1_0, and I need to have package_0 at location_0_0. Since, location_0_0 and location_1_0 are in two different cities first I need to load package_0 into an airplane. Before that since both airplanes are at location_0_0, I need to fly an airplane to location_1_0. After loading package_0 into the airplane, I should fly the airplane to location_0_0, and then unload the package from the airplane.

My actions to achieve the goal from the starting state:

[PLAN]
[START] fly airplane_1 from location_0_0 to location_1_0 [END]
[START] load package_0 into airplane_1 at location_1_0 [END]
[START] fly airplane_1 from location_1_0 to location_0_0 [END]
[START] unload package_0 from airplane_1 at location_0_0 [END]
[PLAN END]


Example 2:

Starting state:
As initial conditions I have that, location_0_0 is an airport, location_1_0 is an airport, airplane_0 is at location_1_0, package_0 is at location_1_0, truck_0 is at location_0_0, truck_1 is at location_1_0, location_0_0 is in the city city_0, location_0_1 is in the city city_0, location_1_0 is in the city city_1 and location_1_1 is in the city city_1.

Goal:
My goal is to have that package_0 is at location_1_1.

Thoughts: package_0 is initially at location_1_0, and I need to have package_0 at location_1_1. Since, location_1_0 and location_1_1 are in the same city first I need to load package_0 into a truck. truck_1 is already at location_1_0. After loading package_0 into truck_1, I should drive truck_1 from location_1_0 to location_1_1, and then unload the package from the truck.

My actions to achieve the goal from the starting state:

[PLAN]
[START] load package_0 into truck_1 at location_1_0 [END]
[START] drive truck_1 from location_1_0 to location_1_1 in city_1 [END]
[START] unload package_0 from truck_1 at location_1_1 [END]
[PLAN END]

Example 3:

Starting state:
As initial conditions I have that, location_0_0 is an airport, location_1_0 is an airport, airplane_0 is at location_0_0, package_0 is at location_0_1, truck_0 is at location_0_0, truck_1 is at location_1_1, location_0_0 is in the city city_0, location_0_1 is in the city city_0, location_1_0 is in the city city_1 and location_1_1 is in the city city_1.

Goal:
My goal is to have that package_0 is at location_1_0.

Thoughts: package_0 is initially at location_0_1, and I need to have package_0 at location_1_0. Since, location_0_1 and location_1_0 are in two different cities first I need to load package_0 into an airplane. But before that I need to take package_0 to a location which is an airport. location_0_0 is an airport in city_0 which also has location_0_1. truck_0 is at location_0_0, and hence I need to drive truck_0 to location_0_1, and then load package_0 into truck_0. After loading package_0 into truck_0, I should drive truck_0 to location 0_0. Then unload package_0 from truck_0 and load into airplane_0. After loading package_0 into airplane_0, I should fly airplane_0 to location_1_0, and then unload the package from the airplane.

My actions to achieve the goal from the starting state:

[PLAN]
[START] drive truck_0 from location_0_0 to location_0_1 in city_0 [END]
[START] load package_0 into truck_0 at location_0_1 [END]
[START] drive truck_0 from location_0_1 to location_0_0 in city_0 [END]
[START] unload package_0 from truck_0 at location_0_0 [END]
[START] load package_0 into airplane_0 at location_0_0 [END]
[START] fly airplane_0 from location_0_0 to location_1_0 [END]
[START] unload package_0 from airplane_0 at location_1_0 [END]
[PLAN END]


'''