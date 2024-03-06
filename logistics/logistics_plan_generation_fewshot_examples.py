standard_prompt = '''

Example 1:

As initial conditions I have that, location_0_0 is an airport, location_1_0 is an airport, airplane_0 is at location_0_0, airplane_1 is at location_0_0, package_0 is at location_1_0, truck_0 is at location_0_0, truck_1 is at location_1_0, location_0_0 is in the city city_0 and location_1_0 is in the city city_1.
My goal is to have that package_0 is at location_0_0.

My plan is as follows:

[PLAN]
fly airplane_1 from location_0_0 to location_1_0
load package_0 into airplane_1 at location_1_0
fly airplane_1 from location_1_0 to location_0_0
unload package_0 from airplane_1 at location_0_0
[PLAN END]


Example 2:

As initial conditions I have that, location_0_0 is an airport, location_1_0 is an airport, airplane_0 is at location_1_0, package_0 is at location_1_0, truck_0 is at location_0_0, truck_1 is at location_1_0, location_0_0 is in the city city_0, location_0_1 is in the city city_0, location_1_0 is in the city city_1 and location_1_1 is in the city city_1.
My goal is to have that package_0 is at location_1_1.

My plan is as follows:

[PLAN]
load package_0 into truck_1 at location_1_0
drive truck_1 from location_1_0 to location_1_1 in city_1
unload package_0 from truck_1 at location_1_1
[PLAN END]

Example 3:

As initial conditions I have that, location_0_0 is an airport, location_1_0 is an airport, airplane_0 is at location_0_0, package_0 is at location_0_1, truck_0 is at location_0_0, truck_1 is at location_1_1, location_0_0 is in the city city_0, location_0_1 is in the city city_0, location_1_0 is in the city city_1 and location_1_1 is in the city city_1.
My goal is to have that package_0 is at location_1_0.

My plan is as follows:

[PLAN]
drive truck_0 from location_0_0 to location_0_1 in city_0
load package_0 into truck_0 at location_0_1
drive truck_0 from location_0_1 to location_0_0 in city_0
unload package_0 from truck_0 at location_0_0
load package_0 into airplane_0 at location_0_0
fly airplane_0 from location_0_0 to location_1_0
unload package_0 from airplane_0 at location_1_0
[PLAN END]


'''