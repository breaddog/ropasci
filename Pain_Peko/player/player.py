from Pain_Peko.minimax.util.hex_util import hex_boundary_getter, generate_board
from Pain_Peko.minimax.minimax import minimax
from Pain_Peko.minimax.moves import generate_starting_move, move_outcome, janken_test, generate_moves, generate_possible_throws
from Pain_Peko.player.rules import *
from Pain_Peko.minimax.util.util import *
from Pain_Peko.minimax.evaluation.evaluation import evaluate

import random
import math
import time
class Player:

    # for the evaluation functions 
    influencing_constants = [0, 0, 0, 0, 0, 0]

    #create a dict of dicts 
    #create a dict of dicts 
    player_information = {"us": {
                                "nThrowsRemaining": 9,
                                "tokens_defeated": 0,
                                "nTokens": 0,
                                "furthestThrowDepth": 0,
                                "player_side": ""
                                #winning_probability = nTokensItCanDefeat/nTokensSelf
                                },

                        "them": {
                                "nThrowsRemaining": 9,
                                "tokens_defeated": 0,
                                "nTokens": 0,
                                "furthestThrowDepth": 0,
                                "player_side": ""
                                #winning_probability = nTokensItCanDefeat/nTokensSelf
                        }}


    # our main_board
    board_dict = {}
    player_tokens = {}
    co_existance_dict = {}

    throw_count = 0
    #total tokens on board
    total_tokens_on_board = 0
    turn_no = 1



    #board edge and board 
    board_edge = [] 
    board_array = [] 



    def __init__(self, player):
        """
        Called once at the beginning of a game to initialise this player.
        Set up an internal representation of the game state.

        The parameter player is the string "upper" (if the instance will
        play as Upper), or the string "lower" (if the instance will play
        as Lower).
        """
        other_player = "lower" if player == "upper" else "upper"
        
        #set our sides 
        self.player_information["us"]["player_side"] = player
        self.player_information["them"]["player_side"] = other_player

        #create our board edge and board representation
        self.board_edge = hex_boundary_getter((0,0), 4, [])
        self.board_array = generate_board()




    def action(self):
        """
        Called at the beginning of each turn. Based on the current state
        of the game, select an action to play this turn.
        """


        #have we just started?
        if self.player_information["us"]["nTokens"] == 0:
            move = generate_starting_move(self.player_information["us"]["player_side"], self.board_array)
            return move

        #otherwise do minimax 
        
        #start off with some shallow depth:
        if self.turn_no < 5:
            depth = 3
        else:
            depth = 2
        
        #set a constraint for search depth
        if self.total_tokens_on_board < 6:
            depth = 3
        elif self.total_tokens_on_board < 10:
            depth = 2
        else:
            depth = 1
        
        #have a time reference
        starting_time = int(round(time.time(), 0))
        #salvage result from minimax
        result = minimax(self.board_dict.copy(), self.player_tokens.copy(), self.co_existance_dict.copy(),
                        None, None, None, depth, True, -math.inf, math.inf,
                        (-5, -5), self.player_information.copy(), self.board_array, self.board_edge, 
                        starting_time, True, self.turn_no)

        #tidy it up
        result = result[0]
        #in case we get a bad move redo but make it very shallow
        if len(result) == 1 or result == (-5, -5):
            #force it to return a usable move
            counter = 0
            while (len(result) == 1) or (result == (-5, -5)):
                result = minimax(self.board_dict.copy(), self.player_tokens.copy(), self.co_existance_dict.copy(),
                            None, None, None, 1, True, -math.inf, math.inf,
                            (-5, -5), self.player_information.copy(), self.board_array, self.board_edge, 
                            starting_time, False, self.turn_no)
                result = result[0]
                counter += 1
                
                #if its taking too long
                if counter > 2: 
                    #generate one random possible move to use 
                    allied_tokens = [token for token in self.player_tokens if self.player_tokens[token] == "us"]
                    move_list = generate_moves(self.board_dict, self.player_tokens, self.co_existance_dict, allied_tokens,
                                                self.player_information, self.board_array, True, "all")
                    
                    
                    #if there are no moves
                    if len(move_list) == 0:
                        #check if we can just throw something 
                        if self.player_information['us']['nThrowsRemaining'] > 0:
                            throws = generate_possible_throws(self.board_dict, self.player_tokens, self.co_existance_dict, self.player_information, "us",
                                                            self.player_information["us"]["player_side"], self.board_array, "all" )
                            #just choose a random one
                            result = random.choice(throws)
                    
                    else:
                        result = random.choice(move_list)
                    break

        #otherwise clean it up
        if result[0] == 'throw':
            final_result = (result[0].upper(), result[1], result[2])
        else:
            final_result = (result[0].upper(), result[2], result[3])
        # return final result 
        return final_result

    
    def update(self, opponent_action, player_action):
        """
        Called at the end of each turn to inform this player of both
        players' chosen actions. Update your internal representation
        of the game state.
        The parameter opponent_action is the opponent's chosen action,
        and player_action is this instance's latest chosen action.
        """
        #format
        #throw, type, location
        #swing/slide, prev, next
        self.turn_no += 1


        #format the moves by adding the token type
        opponent_action = self.add_token_type_to_index_one(opponent_action)
        player_action =self.add_token_type_to_index_one(player_action)

    
        
        #if were moving towards the same coord and it exists on the board for now 
        if (opponent_action[-1] == player_action[-1]):
            
            #check if theres a three way tie 
            if opponent_action[-1] in self.board_dict:
                #list them down 
                composition = [self.board_dict[opponent_action[-1]], opponent_action[1], player_action[1]]
            
                #if theres three unique tokens there 
                if len(composition) == len(set(composition)):
                    self.three_way_checking(opponent_action, player_action)
                else:
                    self.two_token_situation(opponent_action, player_action)
                
            #otherwise business as usual
            else:
                self.two_token_situation(opponent_action, player_action)


        #otherwise if its swapping positions 
        elif opponent_action[2] == player_action[-1] and opponent_action[-1] == player_action[2]:

            #set for both 
            add_token(self.board_dict, self.player_tokens, opponent_action[-1], opponent_action[1], 'them')
            self.player_tokens[opponent_action[-1]] = 'them'
            
            add_token(self.board_dict, self.player_tokens, player_action[-1], player_action[1], 'us')
            self.player_tokens[player_action[-1]] = "us"

        #redo this entire segment
        #CB PAIN
        else:
            self.update_board_with_moves(player_action, "us")
            #move them
            self.update_board_with_moves(opponent_action, "them")
            #them move for us
            
    


    def two_token_situation(self, opponent_action, player_action):
        #otherwise something is happening there 
        #see us vs them who wins on the overlapping section 
        if janken_test(player_action[1], opponent_action[1]) == janken_outcome.WIN:
            winning_player = "us"
        elif janken_test(player_action[1], opponent_action[1]) == janken_outcome.DEFEAT:
            winning_player = "them"
        else:
            winning_player = "us"

        #execute changes for one of the only
        if winning_player == "us":
            #update for us 
            self.same_coord_move_handler(player_action, opponent_action, winning_player)
        else:
            #update for them
            self.same_coord_move_handler(opponent_action, player_action, winning_player)




    def add_token_type_to_index_one(self, move):
        if move[0] != "THROW":
            move = (move[0], self.board_dict[move[1]], move[1], move[2])
        return move
    

    def same_coord_move_handler(self, winning_action, losing_action, winning_player):

        other_player = "them" if winning_player == "us" else "us"
        #update for winning_player
        self.update_board_with_moves(winning_action, winning_player)

        #if opponent did a throw
        if losing_action[0] == "THROW":
            #ignore and just decrement 
            self.updateThrowInfo(janken_outcome.DEFEAT, other_player)

        #otherwise they messed up their swing/slide, remove their token
        else:
            remove_token(self.board_dict, self.player_tokens, losing_action[2])


    #check if theres a three way showdown
    #WORKS
    def three_way_checking(self, opponent_action, player_action):
        #first check move type

        
            
            #ignore going on and just remove whatever is there
            #co-existance dict 
            updateCoexistingDict(player_action[-1], janken_outcome.DEFEAT, 
                                player_tokens[player_action[-1]], 'remove-all')
            
            #if its a throw decrement the throws
            if opponent_action[0] == "THROW":
                updateThrowInfo(janken_outcome.DEFEAT, "them")
            else:
                #increment tokens_defeated 
                self.player_information['us']['tokens_defeated'] += 1


            if player_action[0] == "THROW":
                updateThrowInfo(janken_outcome.DEFEAT, "us")
            else:
                self.player_information['them']['tokens_defeated'] += 1

            #decrement for the player whose token was there originally 
            other_player = "us" if self.player_tokens[player_action[-1]] == "them" else "them"


            self.player_information[other_player]['tokens_defeated'] += 1

            #remove the coord thats there 
            self.board_dict.pop(player_action[-1])
            self.player_tokens.pop(player_action[-1])


    ##read and update for both players 
    def update_board_with_moves(self, move_info, moving_player):

        move = move_info[0]
        token_type = move_info[1]
        coord = move_info[-1]

        other_player = "us" if moving_player == "them" else "them"

        #TOKEN DOESNT EXIST THERE 
        #if the destination coord is empty
        if coord not in self.board_dict:
            #if we are throwing onto a new coord 
            if move == "THROW":
                #update our board_dict
                self.updateThrowInfo(None, moving_player)
            #otherwise its a swing/slide 
            else:
                #remove previous isntance of token
                remove_token(self.board_dict, self.player_tokens, move_info[2])
            #add the token there 
            add_token(self.board_dict, self.player_tokens, coord, token_type, moving_player)
            self.player_tokens[coord] = moving_player

        #SOMETHING THERE
        #otherwise theres something there
        else:
            #existing stuff 
            existing_type = self.board_dict[coord]
            exisitng_player = self.player_tokens[coord]

            #get the outcome 
            outcome = janken_test(token_type, existing_type)

            #if its a win
            if outcome == janken_outcome.WIN:
                #if its a throw
                if move == "THROW":
                    #update throw status
                    self.updateThrowInfo(None, moving_player)
                #otherwise its a swing/slide
                else:
                    remove_token(self.board_dict, self.player_tokens, move_info[2])
                    # self.player_tokens.pop(move_info[2])

                #if its in the coexistance_dict
                if coord in self.co_existance_dict:
                    #update we won over taht 
                    self.updateCoexistingDict(coord, moving_player, 'remove-all')
                
                #add the token there 
                add_token(self.board_dict, self.player_tokens, move_info[-1], move_info[1], moving_player)
                self.player_tokens[move_info[-1]] = moving_player


                self.player_information[moving_player]['tokens_defeated'] += 1


            #if they died 
            elif outcome == janken_outcome.DEFEAT:
                #if its a throw ignore it 
                if move == "THROW":
                    self.updateThrowInfo(None, moving_player)
                    self.player_information[moving_player]['nTokens'] -= 1
                #swing/slide
                else:
                    #remove from previous location
                    remove_token(self.board_dict, self.player_tokens, move_info[2])
                
                #the enemy has defeated a token without knowing it 
                self.player_information[other_player]['tokens_defeated'] += 1

            #co-existance
            elif outcome == janken_outcome.COEXIST :
                remove_token(self.board_dict, self.player_tokens, move_info[2])
                self.updateCoexistingDict(coord, moving_player, 'add')


        

    #update the co-existing occurance 
    def updateCoexistingDict(self, coord, moving_player, mode):
        
        other_player = "us" if moving_player == "them" else "them"
        #for existing ones 

        #removing one as they moved 
        if mode == 'remove-one':

            if coord in self.co_existance_dict:
                removeFromCoexistanceDict(self.board_dict, self.player_tokens, self.co_existance_dict,
                                        coord, moving_player)
                self.total_tokens_on_board -= 1

        #otherwise we are adding a token
        elif mode == 'add':
            
            addIfCoexisting(self.board_dict, self.player_tokens, self.co_existance_dict, 
                            coord, moving_player)
            self.total_tokens_on_board += 1


        #otherwise defeat all
        elif mode == 'remove-all':

            #if coexisting
            if coord in self.co_existance_dict:
                
                usCoexist = self.co_existance_dict[coord][1]
                themCoexist = self.co_existance_dict[coord][-1]

                #then update for each value
                self.player_information['us']['nTokens'] -= usCoexist
                self.player_information['them']['nTokens'] -= themCoexist

                self.player_information['us']['tokens_defeated'] += themCoexist
                self.player_information['them']['tokens_defeated'] += usCoexist


                self.total_tokens_on_board -= (usCoexist + themCoexist)
                #remove the entry alltogether
                self.co_existance_dict.pop(coord, None)

                
    #update info for slides 
    def updateSwingSlideInfo(self, outcome, moving_player):

        other_player = "us" if moving_player == "them" else "them"

        #if the player won via that swing/slide 
        if outcome == janken_outcome.WIN:
            self.player_information[other_player]['nTokens'] -= 1
            self.player_information[moving_player]['tokens_defeated'] += 1

        #if that player is stupid and did a losing slide/swing 
        if outcome == janken_outcome.DEFEAT:
            self.player_information[moving_player]['nTokens'] -= 1
            self.player_information[other_player]['tokens_defeated'] += 1


    #update nThrows for that player 
    def updateThrowInfo(self, outcome, throwing_player):

        #update for that player 
        #this always updates whenever a throw happens 
        self.player_information[throwing_player]['nTokens'] += 1
        # self.player_information[throwing_player]['nThrowsRemaining'] -= 1
        # if self.player_information[throwing_player]['nThrowsRemaining'] < 0:
        #     self.player_information[throwing_player]['nThrowsRemaining'] = 0
        self.player_information[throwing_player]['furthestThrowDepth'] += 1

        if throwing_player == "us":
            if self.throw_count < 9:
                self.throw_count += 1
            self.player_information['us']['nThrowsRemaining'] = 9 - self.throw_count
            
        #determine which player is the other one  
        other_player = "us" if throwing_player == "them" else "them"

        #if that player won
        if outcome == janken_outcome.WIN:

            #decrease their throw amount 
            self.player_information[other_player]['nTokens'] -= 1
            #update other player count 
            self.player_information[throwing_player]['tokens_defeated'] += 1
        
        #if that player lost 
        if outcome == janken_outcome.DEFEAT:

            #they wasted a throw
            self.player_information[throwing_player]['nTokens'] -= 1

            #we defeated one extra 
            self.player_information[other_player]['tokens_defeated'] += 1

    





                







