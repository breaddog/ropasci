"""
COMP30024 Artificial Intelligence, Semester 1, 2021
Project Part B: RoPaSci 360

This script contains the entry point to the program (the code in
`__main__.py` calls `main()`). Your solution starts here!

Coded by:
Leong Tien Foong: 1025208
Stephen Iskandar: 1024303
"""

import sys
import json
import math
import time
import timeit
# If you want to separate your code into separate files, put them
# inside the `search` directory (like this one and `util.py`) and
# then import from them like this:
from .minimax.util.hex_util import hex_boundary_getter, generate_board
from .minimax.util.util import *
from .minimax.moves import *
from .minimax.minimax import minimax

from .player.rules import *




# the max number of tokens 
MAX_TOKENS = 9

#have some set of values that will determine our current standing in the game
# mirror c1-c7 as some value
influencing_constants = [0, 0, 0, 0, 0, 0]

#### SET PLAYERS
#we will call this later 

info_struct = {
                    "nThrowsRemaining": 9,
                    "tokens_defeated": 0,
                    "nTokens": 0,
                    "furthestThrowDepth": 1,
                    "player_side": ""
                    #winning_probability = nTokensItCanDefeat/nTokensSelf
                }

#create a dict of dicts 
player_information = {"us": {
                            "nThrowsRemaining": 9,
                            "tokens_defeated": 0,
                            "nTokens": 0,
                            "furthestThrowDepth": 1,
                            "player_side": ""
                            #winning_probability = nTokensItCanDefeat/nTokensSelf
                            },

                     "them": {
                            "nThrowsRemaining": 9,
                            "tokens_defeated": 0,
                            "nTokens": 0,
                            "furthestThrowDepth": 1,
                            "player_side": ""
                            #winning_probability = nTokensItCanDefeat/nTokensSelf
                    }}


# our main_board
board_dict = {}
player_tokens = {}
co_existance_dict = {}

#generate 
# if the player is at the edge force them to either go along it or
# go away from it 
board_edge = hex_boundary_getter((0,0), 4, [])

# index 0-8 that represents -4:4 offset by -4 so its
board_array = generate_board()

#one turn will consist of multiple moves
#def take_turn(board_dict, player_tokens, coord, coord_list, outcomes):
def main():

    #board_dict is the dict for the board to read
    #player_tokens keeps track of whether the piece belongs to upper or lower 

    ## __init__
    board_file = "Pain_Peko/boards/swing.json"

    #first tries to open a .json board file 
    try:
        with open(board_file) as file:
            data = json.load(file)

    #if theres any issue (i.e formatting) then exit)
    except IndexError:
        print("usage: python3 -m search path/to/swing.json", file=sys.stderr)
        sys.exit(1)

    #whos on which side 
    player_information["them"]["player_side"] = "upper"
    player_information["us"]["player_side"] = "lower"


    #READ FILE
    dict_reader(data,  player_information)
    print(f'bd: {board_dict}')
    print(f'pt: {player_tokens}')
    print(f'cf: {co_existance_dict}')
    print(f'pi: {player_information}')

    #('THROW', 's', (-4, 3))
    #('SLIDE', 'r' (-4, 3))
    move = ('THROW', 'r', (0,-1))
    other_move = ('THROW', 'p', (0,-1))
    extra_move = ('THROW', 's', (0, -1))

    

    print(f'move: {move} onto {board_dict[move[-1]]}')
    


    # print(move[-1] in board_dict)
    print(f'after bd: {board_dict}')
    print(f'after pt: {player_tokens}')
    print(f'after cf: {co_existance_dict}')
    print(f'after pi: {player_information}')


    ## get_move
    depth = 3
    move = generate_starting_move(player_information["us"]["player_side"], board_array)


    #minimax(board_dict, sim_player_tokens, board_dict, player_tokens, depth - 1, not maximisingPlayer,
                           # -alpha, -beta, move, sim_player_information, board_representation, board_edge)
    
    #get a starting time to compare 
    starting_time = int(round(time.time(), 0))

    #get our result
    result = minimax(board_dict, player_tokens, co_existance_dict, None, None, None,
                    depth, True, -math.inf, math.inf, (-5, -5), 
                    player_information, board_array, board_edge, starting_time)

    #in case we get a jank result 

    
    result = result[0]
    if result[0] == 'throw':
        final_result = (result[0].upper(), result[1], result[2])
    else:
        final_result = (result[0].upper(), result[2], result[3])

    print(f'\nWe have decided that {final_result} was the move to go')
   

    stop = timeit.default_timer()

    print(f'Time:', stop - start)
        

#update changes for one player 
def read_and_update_player_moves (move_info, moving_player):

    #when considering move:
    #THROW
    move = move_info[0]
    coord = move_info[-1]
    token_type = move_info[1]
    #the other player we are updating for
    other_player = "us" if moving_player == "them" else "them"


    # EMPTY 
    if coord not in board_dict:

        #for throws 
        if move.upper() == 'THROW':
            updateThrowInfo(None, moving_player)

        add_token(board_dict, player_tokens, move_info[-1], move_info[1], "them")

    # MOVED ONTO SOMETHING 
    # check what token there is there 
    else:
        
        other_player = player_tokens[coord]
        other_type = board_dict[coord]
        print(f'exists {token_type} {other_type}' )
        #outcome of the throw
        outcome = janken_test(token_type, other_type)
        print(outcome)

        #if throw update some other stuff 
        if move.upper() == "THROW":
            updateThrowInfo(outcome, moving_player)


        #BOARD_DICT UPDATES
        # if they defeated whatever is on that coord  
        if outcome == janken_outcome.WIN:
            
            #update co-existance board 
            updateCoexistingDict(coord, moving_player, 'remove-all')
            #remove existing one 
            remove_token(board_dict, player_tokens, coord)
            #replace token in bd and pt
            add_token(board_dict, player_tokens, coord, token_type, "them")

        #otherwise that player stupidly suicided, dont bother updating 
        elif outcome == janken_outcome.DEFEAT:
            
            #if its not a throw (i.e/swing/slide)
            if move.upper() != "THROW":
                player_information[moving_player]['nThrows'] -= 1


            player_information[other_player]['tokens_defeated'] += 1

        #otherwise its co-existance
        elif outcome == janken_outcome.COEXIST:
            updateCoexistingDict(coord, moving_player, 'add')
                    
        


#update the co-existing occurance 
def updateCoexistingDict(player_information, coord, moving_player, mode):
    
    other_player = "us" if moving_player == "them" else "them"
    #for existing ones 

    #removing one as they moved 
    if mode == 'remove-one':
        removeFromCoexistanceDict(coord, moving_player)
        # total_tokens_on_board -= 1

    #otherwise we are adding a token
    elif mode == 'add':
        addIfCoexisting(coord, moving_player)


    #otherwise defeat all
    elif mode == 'remove-all':

        #if coexisting
        if coord in co_existance_dict:
            
            usCoexist = co_existance_dict[coord][1]
            themCoexist = co_existance_dict[coord][-1]

            #then update for each value
            player_information['us']['nTokens'] -= usCoexist
            player_information['them']['nTokens'] -= themCoexist

            player_information['us']['tokens_defeated'] += themCoexist
            player_information['them']['tokens_defeated'] += usCoexist


            #remove the entry alltogether
            co_existance_dict.pop(coord, None)

            

def updateSwingSlideInfo(outcome, moving_player):

    other_player = "us" if moving_player == "them" else "them"

    #if the player won via that swing/slide 
    if outcome == janken_outcome.WIN:
        player_information[other_player]['nTokens'] -= 1
        player_information[moving_player]['tokens_defeated'] += 1

    #if that player is stupid and did a losing slide/swing 
    if outcome == janken_outcome.DEFEAT:
        player_information[moving_player]['nTokens'] -= 1
        player_information[other_player]['tokens_defeated'] += 1



#update nThrows for that player 
def updateThrowInfo(outcome, throwing_player):

    #update for that player 
    #this always updates whenever a throw happens 
    player_information[throwing_player]['nTokens'] += 1
    player_information[throwing_player]['nThrowsRemaining'] -= 1
    player_information[throwing_player]['furthestThrowDepth'] += 1

        
    #determine which player is the other one  
    other_player = "us" if throwing_player == "them" else "them"

    #if that player won
    if outcome == janken_outcome.WIN:

        #decrease their throw amount 
        player_information[other_player]['nTokens'] -= 1
        #update other player count 
        player_information[throwing_player]['tokens_defeated'] += 1
    
    #if that player lost 
    if outcome == janken_outcome.DEFEAT:

        #they wasted a throw
        player_information[throwing_player]['nTokens'] -= 1

        #we defeated one extra 
        player_information[other_player]['tokens_defeated'] += 1







                












#takes json file and turns it into a dict with (coord): value pair
def dict_reader(data,  player_information):

    #build up dict for the time being 
    for key in data:
       
        # for each token defined in the json list key values
        for token in data[key]:
            
            #if the entry exists there already
            if (token[1], token[2]) in board_dict:

                #first co-existance 
                if (token[1], token[2]) not in co_existance_dict:
                    co_existance_dict[(token[1], token[2])] = [1, 0, 0]

                    #for which player initially
                    if player_tokens[token[1], token[2]] == "us":
                        co_existance_dict[(token[1], token[2])][1] += 1
                    else:
                        co_existance_dict[(token[1], token[2])][2] += 1
                #add co-existance count
                co_existance_dict[(token[1], token[2])][0] += 1
                
                #determine for which player later
                if player_information["us"]["player_side"] == key:
                    co_existance_dict[(token[1], token[2])][1] += 1
                else:
                    co_existance_dict[(token[1], token[2])][2] += 1


            else:
                board_dict[(token[1], token[2])] = token[0]
                #player tokens store the ownership of the token
                
                #if its our side
                if player_information["us"]["player_side"] == key:
                    player_tokens[(token[1], token[2])] = "us"
                    player_information["us"]["nTokens"] += 1
                    player_information["us"]["nThrowsRemaining"] -= 1
                    player_information["us"]["furthestThrowDepth"] += 1

                #otherwise their side
                else:
                    player_tokens[(token[1], token[2])] = "them"
                    player_information["them"]["nTokens"] += 1
                    player_information["them"]["nThrowsRemaining"] -= 1
                    player_information["them"]["furthestThrowDepth"] += 1
