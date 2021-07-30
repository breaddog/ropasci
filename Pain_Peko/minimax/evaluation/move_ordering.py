import math
import numpy as np
from Pain_Peko.player.rules import *
from Pain_Peko.minimax.util.hex_util import *
from Pain_Peko.minimax.evaluation.evaluation import *
from Pain_Peko.minimax.moves import *
from Pain_Peko.minimax.util.util import *



#once we get a static evaluation at a certain depth, just see what else we can do there
#this is executed at the end of our minimax to see just one step further 
def moveOutcomeEvaluation(board_dict, player_tokens, co_existance_dict, 
                        previous_bd, previous_pt, previous_cx,
                        player_information, player_side, move_made, 
                        board_representation, edge_boundaries, turnNo):

    shallow_evaluation = 0

    #setup params
    player = "us" if player_side else "them"
    player_side_on_board = player_information[player]["player_side"]

    allied_tokens = []
    enemy_tokens = []

    #get allied/enemy tokens 
    for token in board_dict:
        if player_tokens[token] == player:
            allied_tokens.append(token)
        else:
            enemy_tokens.append(token)
    

    #just do a shallow evaluation (SEE)
    #we statically evaluate the moves that the opponent can make IF we perform this move 
    #so pass on current BD 
    #this ensures that we arent just looking at the horizon but dwelling further 
    
    # #if theres any winning moves:
    win_outcomes = searchWinOutcomes(board_dict, player_tokens, co_existance_dict,
                        previous_bd, previous_pt, previous_cx,
                        player_information, player_side, move_made, allied_tokens,
                        board_representation, edge_boundaries, -math.inf, math.inf, turnNo)

    # print(f'Win outcomes: {win_outcomes}')
    shallow_evaluation += win_outcomes

    #if theres no winning outcomes set to 0 to prevent jankiness
    if math.isinf(shallow_evaluation):
        shallow_evaluation = 0


    #otherwise get an average move outcome based on the following values below
    #defeat w/o throw, stateDominance, forwardMoving, regionPriority
    average_value = 0
    evaluated = []
    #filter through the other moves 
    other_moves = []
    for move in generate_moves(board_dict, player_tokens, co_existance_dict, allied_tokens, player_information,
                                board_representation, player_side, "all"):
        
        #forwardMoving
        FM = forwardMoving(board_dict, player_tokens, move, player_side, player_information)
        # print(f'FM: {FM}')
        average_value += FM

        #if space is already occupied 
        if move[-1] in board_dict:

            average_value = dying_chances(move[1], player_tokens[move[-1]])
            
            #if the move isnt a win (as its been evaluated already)

            #state dominance
            #defeatwithoutthrow
            DWT = defeatWithoutThrow(board_dict, player_tokens, co_existance_dict, player_information, allied_tokens,
                                        player_side, board_representation, turnNo)
            # print(f'DWT: {DWT}')

            average_value += DWT

            #stateDominance
            #false hope
            FH =  falseHope(board_dict, player_tokens, move,
                                    allied_tokens, enemy_tokens, edge_boundaries)
            # print(f'FH: {FH}')
            average_value += FH
            
        evaluated.append(move)

    # print(f'Before eval: {round(average_value)}')
    #get the average 
    if len(evaluated) > 0:
        average_value /= len(evaluated)
    # print(f'AVG: {round(average_value)} Evaluated {len(evaluated)} positions')
    shallow_evaluation += round(average_value, 0)

    # print(f'Average: {average_value}')

    # print(f'Shallow: {shallow_evaluation}\n')
    #return a shallow evaluation of the state we are at 
    return shallow_evaluation
                
    
                
# get win ourcomes 
def searchWinOutcomes(board_dict, player_tokens, co_existance_dict,
                        previous_bd, previous_pt, previous_cx,
                        player_information, player_side, move, allied_tokens,
                        board_representation, edge_boundaries, alpha, beta, turnNo):

    #get an evaluation 
    evaluation = evaluate(board_dict, player_tokens,
                         previous_bd, previous_pt,
                        player_information, player_side, move, edge_boundaries, turnNo)

    #can we win from here?
    #this will eventaully stop when there are no more captures 
    win_moves = generate_moves(board_dict, player_tokens, co_existance_dict, allied_tokens, player_information,
                                board_representation, player_side, "wins")


    #no winning moves, dont add any value 
    if len(win_moves):
        #do a shallow static evaluation for those 
        return evaluation


    #otherwise recurse until alpha-beta tells us to stop 
    for move in win_moves:

        #create simulation
        sim_bd = board_dict.copy()
        sim_pt = player_tokens.copy()
        sim_player_info = player_information.copy()

        #simulate the move
        sim_move = simulate_move(sim_bd, sim_pt, sim_player_info, player_side, move)

        #do a shallow recursion
        result = searchWinOutcomes(sim_bd, sim_pt, board_dict, player_tokens, sim_player_info,
                                    player_side, move, allied_tokens, board_representation,  
                                    edge_boundaries, alpha, beta, turnNo)

        #get the result 
        evaluation = result[-1]

        #unsimulate that move
        unsimulate_move(sim_bd, sim_pt, sim_player_info, player_side, sim_move)

        
        #consider if its a good or shit move 
        if evaluation > alpha:
            alpha = evaluation
        else:
            if evaluation < beta:
                break
            return alpha

    return alpha





# can we defeat without a throw for now?
def defeatWithoutThrow(board_dict, player_tokens, co_existance_dict, player_information, allied_tokens, 
                        player_side, board_representation, turnNo):
    
    win_moves = generate_moves(board_dict, player_tokens, co_existance_dict, allied_tokens, player_information,
                                board_representation, player_side, "wins")

    #try and get a projection on this 
    win_moves = [move for move in win_moves if move[0] != 'throw']

    #if there is a chance to defeat them like this 
    # print(f'N moves with a win: {win_moves}')
    if not len(win_moves):
        return 0
    return 5



# have we moved forward for nThrows < 5
def forwardMoving(board_dict, player_tokens, move, player_side, player_information):

    player = "us" if player_side else "them"
    player_side_on_board = player_information[player]["player_side"]

    if player_information[player]["furthestThrowDepth"] < 5 :

        if move[0] != 'throw':

            # check if its us or them
            if player_side_on_board == 'upper' :

                if move[3][0] == move[2][0] - 1 :
                    return 2

            else :

                if move[3][0] == move[2][0] + 1 :
                    return 2

    return 0

# if we execute this move, will we actually die?
def falseHope(board_dict, player_tokens, move, allied_tokens, enemy_tokens, edge_boundaries):

    chances_of_not_dying  = 0

    #handle throws
    if move[0] == 'throw':

        #if we are throwing over something 
        if move[2] in board_dict:

            #get the outcome of that move 
            chances_of_not_dying += dying_chances(move[1], player_tokens[move[2]]) * 2


        #otherwise do an evaluation of the surroundings 
        #draw a 2 hex boundary 
        move_region = generate_adjacent_coords(move[-1])

        #for all the enemy tokens 
        for token in enemy_tokens:
            #if there is an enemy token there 
            if token in move_region:
                
                #enemy vs us outcome
                chances_of_not_dying += dying_chances(player_tokens[token], move[1]) 



    #otherwise swing and slides 
    else:

        #if we are swinging/sliding onto something that exists on the board
        if move[-1] in board_dict:
            
            #swings have more weight to them
            multiplier = 2 if move[0] == "swing" else 1


            chances_of_not_dying += dying_chances(move[1], player_tokens[move[-1]]) * multiplier

        #otherwise nothing much really
        else:
            
            if move[0] == "slide":
                #get move region
                move_region = generate_adjacent_coords(move[-1])

                #if its slide just check surroundings
                for token in enemy_tokens:

                    #if an enemy exists there 
                    if token in move_region:

                        #check if enemy can do anything to us 
                        chances_of_not_dying += dying_chances(player_tokens[token], move[1])

            #for swings we need to see a bit further 
            if move[0] == "swing":
                
                #radius = 1
                inner_ring = generate_adjacent_coords(move[-1])

                #radius = 2
                outer_ring = hex_boundary_getter(move[-1], 2, edge_boundaries)

                #dont overevaluate things 
                evaluated = []
                #for all evenmy tokens
                for token in enemy_tokens:
                    
                    #if it hasnt been evaluated
                    if token not in evaluated:
                            
                        #if it exists in the inner_ring
                        if token in inner_ring:

                            #find if theres another token in the second_ring that
                            #is next to it 
                            adjacent_tokens = [t for t in enemy_tokens if distance_in_hexes(t, token) == 1]

                            #if there are any 
                            if len(adjacent_tokens):
                                
                                #for each of them
                                for other_token in adjacent_tokens:
                                        
                                    #if its not us again
                                    if token != other_token:

                                        #if theyre next to each other
                                        if distance_in_hexes(token, other_token) == 1:

                                            #find out by how much we might die by
                                            chances_of_not_dying += dying_chances(player_tokens[other_token], move[1])

                                            #add to evaluated list to avoid re-evaluation
                                            evaluated.append(other_token)


                            #otherwise just evaluate it 
                            chances_of_not_dying += dying_chances(player_tokens[token], move[1])
                            evaluated.append(token)

    return chances_of_not_dying



        
def dying_chances(move, other_move):

    outcome = janken_test(move, other_move)

    #if the enemy can defeat us if we go there
    if outcome == janken_outcome.WIN:
        return - 2

    #if the enemy dies if they try
    if outcome == janken_outcome.DEFEAT:
        return 4

    #co-existance is just treated as neutral
    if outcome == janken_outcome.COEXIST:
        return  1





            


            #if its a slide 









        
                

    return None
