"""
COMP30024 AI Project A

File that contains functions surrounding game logic


Coded by:
Leong Tien Foong 1025208
Stephen Iskandar 1024303

Completed: 1/4/2021
"""


import math
import numpy
from enum import Enum
#returns true if move can be executed 
#returns false if move cannot be executable 

# should change the int for all the enum in case it overlapped

class move_outcome(Enum):
    VALID = 1
    EMPTY = 2
    INVALID = 3


class janken_outcome(Enum):
    WIN = 4
    DEFEAT = 5
    COEXIST = 6

class move_type(Enum):
    SWING = 7
    SLIDE = 8
    THROW = 9

class game_outcome(Enum):
    WIN = 10
    LOSE = 11
    DRAW = 12

#for now only returns if it can be defeated or not 
def janken_checker(board_dict, player_tokens, coord, other_coord):

    #test game logic
    #paper beats rock

    if other_coord not in board_dict:
        return move_outcome.EMPTY

    # print(board_dict)
    # print(player_tokens)
    if board_dict[coord].lower() == 'p' and board_dict[other_coord].lower() == 'r':
        return janken_outcome.WIN

    #rock beats scissors 
    elif board_dict[coord].lower() == 'r' and board_dict[other_coord].lower() == 's':
        return janken_outcome.WIN

    #scissors beat paper    
    elif board_dict[coord].lower() == 's' and board_dict[other_coord].lower() == 'p':
        return janken_outcome.WIN

    #same piece stacking
    elif board_dict[coord].lower() == board_dict[other_coord].lower():
        return janken_outcome.COEXIST
    
    #otherwise youll lose if you go there...
    else:
        return janken_outcome.DEFEAT

def janken_checker_throw(board_dict, player_tokens, token_type, other_coord):

    #test game logic
    #paper beats rock

    if other_coord not in board_dict:
        return move_outcome.EMPTY

        
    if token_type == 'p' and board_dict[other_coord].lower() == 'r':
        return janken_outcome.WIN

    #rock beats scissors 
    elif token_type.lower() == 'r' and board_dict[other_coord].lower() == 's':
        return janken_outcome.WIN

    #scissors beat paper    
    elif token_type.lower() == 's' and board_dict[other_coord].lower() == 'p':
        return janken_outcome.WIN

    #same piece stacking
    elif token_type.lower() == board_dict[other_coord].lower():
        return janken_outcome.COEXIST
    
    #otherwise youll lose if you go there...
    else:
        return janken_outcome.DEFEAT

# checks if the move can be done and returns the outcome
# EMPTY, INVALID or 
def move_validator(board_dict, player_tokens, curr_coord, other_coord):

    #check if empty (i.e. non existant)
    if other_coord not in board_dict:
        return move_outcome.EMPTY

    #see if you can attempt to defeat that token
    else:
        #for now its just returning if it can be defeated (i.e, owned by who etc.)
        return janken_checker(board_dict, player_tokens, curr_coord, other_coord)
        

#check if coexistance happens (which i doubt will happen with our implementation)
def token_coexistance(board_dict, player_tokens, curr_coord, other_coord):

    if janken_checker(board_dict, player_tokens, curr_coord, other_coord) == janken_outcome.COEXIST :
        return True

    return False


def win_condition_checker(board_dict, player_tokens, tokens_on_board, player):

    # flag to check if we actually lost
    lose_confirmed = 1

    ### INVINCIBLE TOKEN AND SAME TYPE ONLY
    # for each token
    for token in tokens_on_board:
        #for each other token
        for other_token in tokens_on_board:

            # if theyre not owned by the same player and its for the player of interest and not the same token
            if (player_tokens[token] != player_tokens[other_token] and player_tokens[player] == player and token != other_token):

                if (janken_checker(board_dict, player_tokens, token, other_token) == janken_outcome.WIN):
                    #if its defeatable then set the lose condition to 0;
                    lose_confirmed = 0

            #otherwise leave it be and it will never change
            # in cases where only the same type exists or we can never defeat


    return lose_confirmed


# check if all elements are the same 
def equal_elements (coord_list):

    iterator = iter(coord_list)

    try:
        first = next(coord_list)
    except StopIteration:
        return True 

    return all(first == x for x in coord_list)




###### END CASES

#check if any of the win states are done
def check_win_state(board_dict, player_tokens, player_list, enemy_list):

    #list down your win cases here
    if check_invincible_win_state(board_dict, player_tokens, player_list, enemy_list):
        return True

# nothing else can be defeated
def check_invincible_win_state(board_dict, player_tokens, player_list, enemy_list):
    win_cases = 0
    defeat_cases = 0

    for player in player_list:

        for enemy in enemy_list:

            if move_validator(board_dict, player_tokens, player, enemy) == janken_outcome.WIN:

                win_cases += 1

            elif move_validator(board_dict, player_tokens, player, enemy) == janken_outcome.DEFEAT:
                defeat_cases += 1

    #check if there is no way we can be defeated still
    return (defeat_cases == 0)
