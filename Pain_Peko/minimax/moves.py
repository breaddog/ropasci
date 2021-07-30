"""
COMP30024 Artificial Intelligence, Semester 1, 2021
Project Part A: Searching
Coded by:
Leong Tien Foong 1025208
Stephen Iskandar 1024303
"""
import math
import numpy
import random
import itertools

from Pain_Peko.player.rules import *
from Pain_Peko.player.rules import *
from Pain_Peko.minimax.util.hex_util import generate_adjacent_coords, limit_checker, distance_in_hexes





#used to check if swing is possible 
def euclidean_distance(coord, other_coord):

    distance = tuple(numpy.subtract(other_coord, coord))

    return math.sqrt(pow(distance[0], 2) + pow(distance[1], 2))

def generate_starting_move(player_side, board_representation):

    random_token = random.choice(['r', 'p', 's'])

    if player_side == "upper":
        random_coord = random.choice(board_representation[0])
    else:
        random_coord = random.choice(board_representation[-1])

    #return that random move 
    return ('THROW', random_token, random_coord)


def get_region_with_tokens(board_dict):

    region = []

    tokens = list(board_dict.keys())

    same_counter = 0
    previous_length = 0
    for token in tokens:

        #generate 1 hex regions and combine them gradually to get an idea of where to generate
        [region.append(coord) for coord in generate_adjacent_coords(token) if coord not in region]

        #if weve been generating the same stuff for a while already...
        if previous_length == len(region):
            same_counter += 1

            if same_counter == 2:
                return region


        previous_length = len(region)

        


    
    # print(region)
    return region

    

    

#generate moves 
def generate_moves(board_dict, player_tokens, co_existance_dict, allied_tokens, player_information, 
                    board_representation, our_turn, generation_type):

    # print(f'Board to simulate with: {board_dict}')
    #list down all possible moves 
    possible_moves = []
    possible_swings = []
    possible_slides = []
    possible_throws = []

    #board region
    #this helps us to get an idea of where we might want to generate stuff at
    board_region = []

    #some helper stuff
    our_tokens = []
    other_tokens = []
    our_tokens_simplified = []
    other_tokens_simplified = []
    #determine which player to generate for 
    player_of_interest = "us" if our_turn else "them"
    # print(f'player_of_interest: {player_of_interest}')

    # print(f'bd: {board_dict}\n pt: {player_tokens}')
    # accumulate all of our tokens 
    for token in board_dict:
        if player_tokens[token] == player_of_interest:
            our_tokens.append((board_dict[token], token)) 
            our_tokens_simplified.append(token)
        else:
            other_tokens.append((board_dict[token], token))
            other_tokens_simplified.append(token)

    # print(f'Our Tokens: {our_tokens} Their Tokens: {other_tokens}')

    #format is (token_type, coords)
    for token in our_tokens:

        #check if can swing
        possible_swings += generate_possible_swings(board_dict, player_tokens, our_tokens_simplified, token[1], generation_type)

        #check if can slide 
        possible_slides += generate_possible_slides(board_dict, player_tokens, token[1], generation_type)

    # print(f'Swings: {possible_swings}')
    # print(f'Slides: {possible_slides}')
    #check all throws
    #def generate_possible_throws(board_dict, player_tokens, player_information, player_of_interest, player_side, board_representation):
    if player_information[player_of_interest]['nThrowsRemaining'] > 0:
        possible_throws = generate_possible_throws(board_dict, player_tokens, co_existance_dict, player_information, player_of_interest, 
                                                    player_information[player_of_interest]["player_side"], 
                                                    board_representation, generation_type)
    


    possible_moves =  possible_swings + possible_slides + possible_throws
    # possible_moves =  possible_swings + possible_slides
    return possible_moves 

def generate_possible_swings(board_dict, player_tokens, allied_tokens, curr_coord, generation_type):

    possible_swings = []
    
    # first layer, returns all allied tokens 
    for first_layer in [coord for coord in generate_adjacent_coords(curr_coord) if coord in allied_tokens]:
        #for all allies in that projection 
        for swing_coord in generate_adjacent_coords(first_layer):

            #if its not adjacent to the current coordinate or is the current coordinate itself
            if swing_coord not in generate_adjacent_coords(curr_coord) and swing_coord != curr_coord:
                
                #if its a legitimate swing 
                if distance_in_hexes(curr_coord, swing_coord) == 2:
                    #if generate everything 
                    if generation_type == "all":
                        #check if the move will not lead us to defeat (accepts valid and coexistance)
                        if move_validator(board_dict, player_tokens, curr_coord, swing_coord) != janken_outcome.DEFEAT:
                            
                            if abs(swing_coord[0]) < 5 and abs(swing_coord[0]) < 5:
                                possible_swings.append(("swing", board_dict[curr_coord], curr_coord, swing_coord))
                    
                    #generate wins only 
                    if generation_type == "wins":
                        if move_validator(board_dict, player_tokens, curr_coord, swing_coord) == janken_outcome.WIN:

                            if abs(swing_coord[0]) < 5 and abs(swing_coord[0]) < 5:
                                possible_swings.append(("swing", board_dict[curr_coord], curr_coord, swing_coord))

    return possible_swings

def generate_possible_slides(board_dict, player_tokens, curr_coord, generation_type) :

    possible_slides = []

    for slide_coord in generate_adjacent_coords(curr_coord) :

        if limit_checker(slide_coord):
            
            #generate all slides
            if generation_type == "all":
                # eg format is ("slide", "r", (1,1), (1,2))

                if distance_in_hexes(curr_coord, slide_coord) == 1:
                    possible_slides.append(("slide", board_dict[curr_coord], curr_coord, slide_coord))

            #generate wins only 
            if generation_type == "wins":

                if janken_checker(board_dict, player_tokens, curr_coord, slide_coord) == janken_outcome.WIN:

                    if distance_in_hexes(curr_coord, slide_coord) == 1:
                        possible_slides.append(("slide", board_dict[curr_coord], curr_coord, slide_coord))

    return possible_slides


# given our current state, where can we throw 
def generate_possible_throws(board_dict, player_tokens, co_existance_dict, player_information, player_of_interest, 
                                player_side, board_representation, generation_type):

    ##bug here 
    if player_information[player_of_interest]["nThrowsRemaining"] == 0 :
        return []
    
    possible_throws = []
    board_region = get_region_with_tokens(board_dict)


    #we will remove one specific one later on if it outweighs all 
    token_types = ["r", "p", "s"]

    #overall composition for further pruning?
    overall_token_comps = [['r', 0], ['p', 0] , ['s', 0]]
    token_comps = {"us": [0,0,0], "them": [0,0,0]}


    #max_throw_depth
    player = player_information[player_of_interest]["player_side"]
    max_throw_depth = player_information[player_of_interest]["furthestThrowDepth"]
    # print(max_throw_depth)

    # get come composition
    # see if we can eliminate throwing certain types 
    for token in board_dict:

        #get which player to assign to
        player = player_tokens[token]

        #get your RPS sorted 
        if board_dict[token] == "r":
            overall_token_comps[0][-1] += 1
            token_comps[player][0] += 1

        elif board_dict[token] == "p":
            overall_token_comps[1][-1] += 1
            token_comps[player][1] += 1

        elif board_dict[token] == "s":
            overall_token_comps[2][-1] += 1
            token_comps[player][2] += 1
    
    # print(token_comps)

    #check which token we can prune
    #them vs us, which one is least vulnerable?
    rock_diff = ('r', 's', 'p', token_comps["them"][0] - token_comps["us"][2]*2)
    paper_diff = ('p', 'r', 's', token_comps["them"][1] - token_comps["us"][0]*2)
    scissors_diff = ('s', 'p', 'r', token_comps["them"][2] - token_comps["us"][1]*2)
    
    choose_one_to_prune = [rock_diff, paper_diff, scissors_diff]
    choose_one_to_prune.sort(key=lambda x:x[-1], reverse=True)
    # print(token_comps)
    # print(f'prune: {choose_one_to_prune}')
    #always prune the least vulenrable token type
    token_types.remove(choose_one_to_prune[-1][1])
    # print(token_types)
    #for the overall tokens



    # print(f'Max throw depth: {max_throw_depth} for {player_information[player_of_interest]["player_side"]}')
    #if the current player is on the upper side
    if player_information[player_of_interest]["player_side"] == "upper":
        #bug here
        #read in max_throw_depth
        for x in range(0, 0 + max_throw_depth):
            # print(x+4)
            #issue here for some reason 
            for coord in board_representation[x] :
                for token_type in token_types:
                    
                    #consider everything
                    if generation_type == "all":
                        possible_throws.append(("throw" , token_type, coord))

                    #consider wins 
                    if generation_type == "wins":
                        if coord in player_tokens:
                            if janken_test(token_type, player_tokens[coord]) == janken_outcome.WIN:
                                possible_throws.append(("throw" , token_type, coord))
                
    # lower side 
    else:
        for x in range (8, 8 - max_throw_depth, -1):
            for coord in board_representation[x]:
                for token_type in token_types:

                    #consider everything
                    if generation_type == "all":
                        possible_throws.append(("throw" , token_type, coord))

                    #consider wins 
                    if generation_type == "wins":
                        if coord in player_tokens:
                            if janken_test(token_type, player_tokens[coord]) == janken_outcome.WIN:
                                possible_throws.append(("throw" , token_type, coord))
  
    # [print(t) for t in possible_throws]
    # print(player_side)
    # # print(len(possible_throws))
    # print(f'Throws for {player_information[player_of_interest]["player_side"]}: {possible_throws}')
    return possible_throws




def janken_test(token_type, other_token_type):
    #determine the outcome
    if token_type == 'p' and other_token_type == 'r':
        return janken_outcome.WIN

    if token_type == 'r' and other_token_type == 's':
        return janken_outcome.WIN

    if token_type == 's' and other_token_type == 'p':
        return janken_outcome.WIN
        
    if token_type == other_token_type:
        return janken_outcome.COEXIST

    else:
        return janken_outcome.DEFEAT







# updating the board for simulation
def update_board(board_dict, player_tokens, move_set):

    #for a given move set produced by our algo
    for (current_coord, next_coord) in move_set:

        #move and reflect changes on the copy of our board 
        move_token(board_dict, player_tokens, current_coord, next_coord)


def add_token (board_dict, player_tokens, coordinates, piece, player):
    #print(coordinates)

    player_tokens[coordinates] = player

    board_dict[coordinates] = piece

    #print("# Added: {00:} to {01:} for {02:}".format(piece, coordinates, player))
    

def remove_token(board_dict, player_tokens, coordinates):
    
    #print("# Removed: {00:} from {01:} for {02:}".format(board_dict[coordinates], coordinates, player_tokens[coordinates]))

    board_dict[coordinates] = ""
    board_dict.pop(coordinates, None)

    
    player_tokens[coordinates] = ""
    player_tokens.pop(coordinates, None)
    

#check if the move did not go over the boundary
def coord_validator(coordinates):
    return abs(int(coordinates[1])) > 4 or abs(int(coordinates[2])) > 4


# moving one token to a given coordinate
def move_token(board_dict, player_tokens, coord, other_coord):

    add_token(board_dict, player_tokens, other_coord, board_dict[coord], player_tokens[coord])
    remove_token(board_dict, player_tokens, coord)

    
