import numpy as np


#generate a blank board 
def generate_board():
    #from 0-8
    coords = []
    for x in range(4, -5, -1):
        new_row = []

        #is 0
        if x == 0:
            for y in range(-4, 5):
                new_row.append((x, y))
            coords.append(new_row)
        # bigger than 0
        elif (x > 0):
            for y in range(-4, 5 - x):
                new_row.append((x, y))
            coords.append(new_row)
        #less than 0
        #-4, -3, -2, -1, 
        else:
            for y in range (-4 - x, 5):
                new_row.append((x, y))
            coords.append(new_row)
    return coords


def generate_adjacent_coords(coord):

    generated_coords = []
    generated_coords.append(tuple(np.add(coord, (0,1))))
    generated_coords.append(tuple(np.add(coord, (0,-1))))
    generated_coords.append(tuple(np.add(coord, (1,0))))
    generated_coords.append(tuple(np.add(coord, (-1,1))))
    generated_coords.append(tuple(np.add(coord, (1,-1))))
    generated_coords.append(tuple(np.add(coord, (-1,0))))
    # ensure nothing goes wrong with it
    for new_coord in generated_coords:
        if not limit_checker(new_coord) or abs(new_coord[0]) >= 5 or abs(new_coord[1]) >= 5:
            generated_coords.remove(new_coord)

    return generated_coords


    
#checks if boundaries exceeded
def limit_checker(coord):

    #limit determined by x
    initial = 9
    limit = 4

    if abs(coord[0]) > 4 or abs(coord[1] > 4):
        return False

    if (coord[0] == 0 and coord[1] == 0):
        return True
        
    # for positive coordinates check positive end if exceeding
    if (coord[0] > 0): 
        if coord[1] > limit - coord[0] and coord[1] != -limit:
            return False


    # for negative coordinates check the negative end 
    else:
        if (coord[1] < -(limit + coord[0])):
            return False


    return True

def check_limit_and_add(curr_coord, generated_coord, array):
    new = tuple(np.add(curr_coord, generated_coord))
    if limit_checker(new):
        if new not in array:
            array.append(new)


def generate_direction_tuple(start, destination):

    difference = [x for x in tuple(np.subtract(destination, start))]

    #get the magnitude to change by (e.g. +1 or -1 to move towards the next corner)
    x_change_by = 1 if difference[0] > 0 else -1
    y_change_by = 1 if difference[1] > 0 else -1

    # for horizontal moves
    # if we are on the same plane 
    if start[0] == destination[0]:
        x_change_by = 0
    if start[1] == destination[1]:
        y_change_by = 0


    # initialise and return that coord
    return (x_change_by, y_change_by)


def hex_boundary_getter(coord, radius, edge_boundaries):

    #first find out the corners 
    corners = []
    corners = [(-radius, 0), #can mirror them
               (-radius, radius), 
               (0, radius),
               (radius, 0),
               (radius, -radius),
               (0, -radius)] 
    corners = [tuple(np.add(coord, x)) for x in corners]

    # print(coord)
    # print(f'corners: {corners}')

    #first check if our corners are in bounds, otherwise change
    new_corners = []
    
    for i in range(0, len(corners)):

        # if a corner doesnt conform
        if not limit_checker(corners[i]):
            #from our target coord get the direction of travel to the corner
            new_corner_dir = generate_direction_tuple(coord, corners[i])

            #create new possible corner starting from the coord we passed through
            potential_corner = coord
            #keep testing if we reach an edge
            while limit_checker(tuple(np.add(potential_corner, new_corner_dir))):
                potential_corner = tuple(np.add(potential_corner, new_corner_dir))

            #set that as our new corner
            if potential_corner not in new_corners:
                new_corners.append(potential_corner) 
        #otherwise ok to go
        else:
            new_corners.append(corners[i]) 

    #first pass for corners
    corners = new_corners


    #fix for _/ part of the hex_ring
    if len(edge_boundaries) > 0:

        #for all the corners 
        for i in range(len(corners)):
            #get the general direction
            direction = generate_direction_tuple(corners[i], corners[(i + 1) % len(corners)])
            if (direction) == (1,1):
                # print(corners[i], corners[(i + 1) % len(corners)])

                #then from corners[i]
                if corners[i] in edge_boundaries:

                    move_by = (0, 1)
                    #starting from that index 
                    missing_coord = corners[i]
                    # print(f'before: {missing_coord}, {corners[(i + 1) % len(corners)]}, {tuple(np.subtract(corners[(i + 1) % len(corners)], missing_coord))}')
                    while tuple(np.subtract(corners[(i + 1) % len(corners)], missing_coord)) != (1, 0):
                        missing_coord = tuple(np.add(missing_coord, move_by))
                        # print(missing_coord)

                    # print(f'after: {missing_coord}, {corners[(i + 1) % len(corners)]}')
                    #then add to array of corners at that certain part
                    if missing_coord not in corners:
                        corners.insert(corners.index(corners[(i + 1) % len(corners)]), missing_coord) #will be used for the code below
                        break
                
    # print(f'other_new: {corners}')



    # # fill up the gaps between the corners
    hex_ring = []
    
    # #initialisation
    # #for each pair fill in the gaps in between
    for i in range(len(corners)):
        # print(f'checking for{corners[i]} to {corners[(i + 1) % len(corners)]}')
        #we are crawiling on one side 
        one_side = []

        #direction of travel for one side 
        side_travel_direction = generate_direction_tuple(corners[i], corners[(i + 1) % len(corners)])
        # print(f'dir: {side_travel_direction}')
        # initialise first 
        new_coord = tuple(np.add(corners[i], side_travel_direction))
        # print(f'new: {new_coord}')
        
        
        # BUILD ONE SIDE
        while new_coord != corners[(i + 1) % len(corners)] and limit_checker(new_coord):
            #if we are about to add an existing corner stop
            if (new_coord == corners[(i + 1) % len(corners)]):
                break


            #special case: (1,1), have to check the _/ direction 
            #otherwise add to array
            # print(f'found{new_coord}')
            one_side.append(new_coord) 

            # setup for next one
            new_coord = tuple(np.add(new_coord, side_travel_direction))
            
        one_side = [corners[i]] + one_side

        #check if the side conforms
        filtered_side = []
        for boundary_coord in one_side:
            if limit_checker(boundary_coord) and boundary_coord not in hex_ring:
                filtered_side.append(boundary_coord)


        hex_ring += filtered_side
        
        
    
    # print(hex_ring)
    # print(len(hex_ring))

    # filter for duplicated stuff
    [hex_ring.remove(value) for value in hex_ring if not limit_checker(value)]

    return hex_ring


#returns the distance in hexes

#rework this 
def distance_in_hexes(current, destination):

    difference = tuple(np.subtract(destination, current))

    if current == destination:
        return 0
        
    # if both positive add and take that as distance
    if difference[0] > 0 and difference[1] > 0:
        return difference[0] + difference[1] 

    # if both negative take abs sum of (x, y)
    if difference[0] < 0 and difference[1] < 0:
        return abs(difference[0] + difference[1]) 

    #if positive, negative take positive as distance
    if difference[0] > 0 and difference[1] < 0:
        return abs(difference[1])

    #if negative, positive, take positive as distance
    else:
        return abs(difference[0])
    


# gets all coords in one region
def hex_region_generator(coord, radius, edge_boundaries):

    #empty array, dont include current coord as thats the origin
    region = []

    #then loop to fill it in 
    for i in range(1, radius + 1):
        # print(f'raidus: {i}, coord: {coord}')
        for found_coord in hex_boundary_getter(coord, i, edge_boundaries):
            if found_coord not in region:
                region.append(found_coord)

    # print(len(region))
    return region




