"""
This is a demonstration of the AC-3 algorithm, which is used for constraint satisfaction, a process in artificial intelligence.

Here, we use it to allocate sections of courses to rooms based on numerous factors:
- Class size (random, but higher codes generally mean less seats)
- Timeslots
- Rooms available

Course sections are randomly generated with random times and sizes.
Rooms are also randomly generated with random capacities.

The aim is to allocate every course section to a room, with no two classes using the same room at the same time.

If the algorithm completes:
- each course's domain (which has all possible rooms) is reduced to just one room which holds as little seats as possible while fitting the course
    (i.e. for a course with 40 seats, we want a room with 40 seats over a room with 70)
- a file 'output.txt' is written to which lists what room each course is allocated to.

NOTE: Due to the way this is set up, the algorithm semi-frequently returns no solution. Just run it a few times and check 'output.txt' for the final output when it succeeds.
"""
import json, random

# A list of dictionaries, containing course code, capacity, start, end, domain (rooms possible), and neighbors (other classes at the same time)
courses = []
# A list of dictionaries, containing room number and capacity
rooms = []

"""
Checks if two two-number intervals overlap
    [16, 18] and [17, 18] overlap
    [16, 18] and [16, 17] overlap
    [16, 17] and [17, 18] do not overlap
"""
def overlapping_intervals(i1_first, i1_second, i2_first, i2_second):
    return i1_second > i2_first and i1_first < i2_second

"""
Given an array of dicts, finds an item with the given field consisting of the given value
"""
def find_item_by_field(array, field, value):
    for item in array:
        if item.get(field) == value:
            return item
    return None  # Return None if the item is not found

"""
Performs the AC-3 algorithm on the courses array
"""
def ac3(courses, queue=None):
    if queue is None: # if we start with nothing, populate the queue with all conflicts
        queue = []
        for course in courses:
            for j in range(len(course['neighbors'])):
                queue.append((course, find_item_by_field(courses, 'course', course['neighbors'][j])))

    while queue: # navigate through all items of the queue
        course, neighbor = queue.pop(0)
        if revise(course, neighbor):
            if not course['domain']: # an empty domain means there is no solution to this problem
                print(course['course'] + ' has an empty domain. Not solvable!')
                return False
            
            for other_neighbor in course['neighbors']:
                if other_neighbor != neighbor:
                    queue.append((find_item_by_field(courses, 'course', other_neighbor), course))
    
    return True

"""
Based on constraints, revise the domain of a course and add it back to the queue if so
"""
def revise(course, neighbor):
    revised = False # initially it is unchanged
    for room in course['domain']:
        if room in neighbor['domain']: # if this room is in the other course's domain, then remove it, mark as revised
            course['domain'].remove(room)
            revised = True
    return revised

# set up the courses and capacities
course_codes = ['CISC106', 'CISC108', 'CISC181', 'CISC210', 'CISC220', 'CISC260', 'CISC275', 'CISC303', 'CISC304', 'CISC320', 'CISC355', 'CISC360', 'CISC361', 'CISC372', 'CISC374', 'CISC401', 'CISC410', 'CISC411', 'CISC436', 'CISC437', 'CISC450', 'CISC464', 'CISC465', 'CISC471', 'CISC474', 'CISC475', 'CISC476', 'CISC481', 'CISC483', 'CISC484', 'CISC498']
for code in course_codes:
    if random.randint(1, 2) == 1: # add only half of these (approx.) to avoid frequent conflict runs (you can remove this limit but unsolvable problems may happen more often)
        section_num = 10
        for i in range(random.randint(1, (5 - int(code[4])) + 1)):
            hours = random.randint(1, 2)
            start_time = random.randint(8, 18)
            end_time = start_time + hours
            courses.append({
                'course': code + '0' + str(section_num),
                'capacity': random.randrange(10, 40, 5) * (5 - int(code[4])),
                'start': start_time,
                'end': end_time
            })
            section_num += 1

# set up rooms
consonants = 'BCDFGHJKLMNPRSTVWY'
vowels = 'AEIOU'
patterns = ['CCV', 'CVV', 'CVC', 'VCC', 'VVC']
buildings = []
# generate the buildings
for i in range(random.randint(5, 15)):
    pattern_chosen = patterns[random.randint(0, len(patterns) - 1)]
    building = ''
    for ch in pattern_chosen:
        if ch == 'C':
            building += consonants[random.randint(0, len(consonants) - 1)]
        else:
            building += vowels[random.randint(0, len(vowels) - 1)]
    buildings.append(building)
# generate the rooms
for i in range(len(courses) + random.randint(50, 70)):
    rooms.append({
        'number': buildings[random.randint(0, len(buildings) - 1)] + str(random.randint(100, 499)),
        'capacity': random.randrange(10, 200, 5)
    })

# add domains to classes (rooms that can be used)
for course in courses:
    dom = []
    for room in rooms:
        if room['capacity'] >= course['capacity'] and room['capacity'] < course['capacity'] + 10:
            dom.append(room['number'])
    course['domain'] = dom

# add neighbors to classes (classes that occur at the same time)
for course in courses:
    neighbors = []
    for other_course in courses:
        if other_course['course'] == course['course']:
            continue
        if overlapping_intervals(course['start'], course['end'], other_course['start'], other_course['end']):
            neighbors.append(other_course['course'])
    course['neighbors'] = neighbors

output_lines = []
output_lines.append('===AVAILABLE ROOMS===')
for room in rooms:
    output_lines.append(json.dumps(room, sort_keys=False))
output_lines.append('\n===AVAILABLE COURSES===')
for course in courses:
    output_lines.append(course['course'] + ' from ' + str(course['start']) + ':00 to ' + str(course['end']) + ':00 in ' + ', '.join(course['domain']))
    output_lines.append('\tCapacity: ' + str(course['capacity']))

result = ac3(courses)
if result:
    output_lines.append('\n===FINAL CLASS SCHEDULE: POSSIBLE===')
    for course in courses:
        output_lines.append(course['course'] + ' from ' + str(course['start']) + ':00 to ' + str(course['end']) + ':00 in ' + ', '.join(course['domain']))
        output_lines.append('\tCapacity: ' + str(course['capacity']))

    # pick a single room for each course by assigning it to the room that just fits everyone
    min = 99999
    for course in courses:
        for room_num in course['domain']:
            room = find_item_by_field(rooms, 'number', room_num)
            if room['capacity'] < min:
                course['domain'] = [room['number']]

    output_lines.append('\n===FINAL CLASS SCHEDULE: CHOSEN===')
    for course in courses:
        output_lines.append(course['course'] + ' from ' + str(course['start']) + ':00 to ' + str(course['end']) + ':00 in ' + ', '.join(course['domain']))
        output_lines.append('\tCapacity of Course: ' + str(course['capacity']))
        
        # print(course['domain'][0])
        output_lines.append('\tCapacity of Room: ' + str(find_item_by_field(rooms, 'number', course['domain'][0])['capacity']))

    with open('output.txt', 'w') as file:
        for line in output_lines:
            file.write(line + '\n')
