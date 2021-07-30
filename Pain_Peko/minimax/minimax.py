import math
import random
import time
from Pain_Peko.player.rules import *
from Pain_Peko.minimax.moves import *
from Pain_Peko.minimax.util.hex_util import *
from Pain_Peko.minimax.util.util import add_token, move_token, addIfCoexisting, removeFromCoexistanceDict
from Pain_Peko.minimax.evaluation.evaluation import evaluate
from Pain_Peko.minimax.evaluation.move_ordering import moveOutcomeEvaluation



#initialise with (-5, -5) -inf
# minimax, enough said, comes with alpha-beta pruning
#add new variable called move_to_evaluate 
def minimax(board_dict, player_tokens, co_existance_dict, previous_bd, previous_pt, previous_cx,
            depth, maximisingPlayer, alpha, beta, move_made, player_information, 
            board_representation, board_edge, timeStarted, limiter, turnNo):


    # determine stuff
    current_player = "us" if maximisingPlayer else "them"
    allied_tokens = [coord for coord in board_dict if player_tokens[coord] == current_player]
    enemy_tokens = [coord for coord in board_dict if player_tokens[coord] not in allied_tokens]

    #check if any of the enemy tokens are actually co-existances with us 
    [allied_tokens.append(token) for token in enemy_tokens if token in co_existance_dict]
        

    #DEEPEST
    if depth == 0:
        value = moveOutcomeEvaluation(board_dict, player_tokens, co_existance_dict, 
                                        previous_bd, previous_pt, previous_cx,
                                        player_information, maximisingPlayer, move_made,
                                        board_representation, board_edge, turnNo)

        # print(f'Depth 0: We will return {move_made} with {value} for {current_player}\n')
        return [move_made, value]
        

    # FOCUS OVER HERE
    # for all the possible moves we can make 
    # add new variable called current_coord, generate moves related to that coordinate only 
    
    #print(f'Board Dict: {board_dict}, Player Tokens: {player_tokens}')
    move_list = generate_moves(board_dict, player_tokens, co_existance_dict, allied_tokens, 
                                player_information, board_representation, maximisingPlayer, "all")

    #if no moves
    if (len(move_list) == 0):

        #return static evaluation
        value = evaluate(board_dict, player_tokens, 
                        board_dict, player_tokens,
                        player_information, maximisingPlayer, 
                        move_made, board_edge, turnNo)
        # print(f'No moves exist at layer {depth}: we return {move_made}, {value}')
        return [move_made, value]

    #first generate some moves 
    temp_ordered_moves = []
    for move in move_list :

        sim_board_dict = board_dict.copy()
        sim_player_tokens = player_tokens.copy()
        sim_player_information = player_information.copy()
        sim_co_existance_dict = co_existance_dict.copy()


        #cb add coexist dict
        simulate_move(sim_board_dict, sim_player_tokens, sim_player_information, sim_co_existance_dict, 
                        maximisingPlayer , move, 0)
        # print(f'bd: {board_dict}')
        # print(f'sbd: {sim_board_dict}')
        #evaluate the value 
        value = evaluate(sim_board_dict, sim_player_tokens, 
                        board_dict, player_tokens,
                        sim_player_information, maximisingPlayer, 
                        move, board_edge, turnNo)

        #we cannot cut off -'ve moves in case all of them are negative 
        temp_ordered_moves.append((move, value))

    #sort them
    temp_ordered_moves.sort(key=lambda x:x[-1], reverse=True)

    #if we are going through too many moves, just choose the desirable ones
    if len(temp_ordered_moves) > 200:
        temp_ordered_moves = temp_ordered_moves[:int(len(temp_ordered_moves)/8)]
    elif len(temp_ordered_moves) > 100:
        temp_ordered_moves = temp_ordered_moves[:int(len(temp_ordered_moves)/4)]
    elif len(temp_ordered_moves) > 50:
        temp_ordered_moves = temp_ordered_moves[:int(len(temp_ordered_moves)/2)]


    #then format 
    ordered_moves = []
    [ordered_moves.append(move) for (move, value) in temp_ordered_moves]
        
    #try to shuffle that selection in hopes of getting better pruning
    random.shuffle(ordered_moves)
    # print(ordered_moves)
    i = 0
    #depending on which player our best_value will be different
    best_move = move_made
    worst_move = move_made

    # MINIMAX
    for move in ordered_moves:
        
        #get out of recursion loop
        #if we are running out of time
        if limiter:
            current_time = int(round(time.time(), 2))
            if current_time - timeStarted > 1.2:
                
                #we still need to return a legit move
                if best_move == (-5, -5):
                    best_move = move
                #return static evaluation ASAP
                value = evaluate(sim_board_dict, sim_player_tokens, 
                            board_dict, player_tokens,
                            sim_player_information, maximisingPlayer, 
                            best_move, board_edge, turnNo)
                #maybe do one quick alpha beta here 
                if maximisingPlayer:
                    if value > alpha:
                        alpha = value
                    return [best_move, alpha]

                else:
                    if beta < value:
                        beta = value
                    return [best_move, beta]
                
            

        #get simulated boards
        sim_board_dict = board_dict.copy()
        sim_player_tokens = player_tokens.copy()
        sim_player_information = player_information.copy()
        sim_co_existance_dict = co_existance_dict.copy()

        i += 1

        
        #simulate the move
        sim_move = simulate_move(sim_board_dict, sim_player_tokens, sim_player_information, sim_co_existance_dict, 
                                maximisingPlayer, move, depth)

        # generated move will be passed on as move_to_evaluate 

        #otherwise go ahead and minimax
        #just add the sim_cx argument 
        result = minimax(sim_board_dict.copy(), sim_player_tokens.copy(), sim_co_existance_dict.copy(), 
                            board_dict.copy(), player_tokens.copy(), co_existance_dict.copy(), 
                            depth - 1, not maximisingPlayer, 
                            alpha, beta, move, sim_player_information.copy(), 
                            board_representation, board_edge, timeStarted, limiter, turnNo)
              

        #undo the move for consistency
        #cb alter it 
        unsimulate_move(sim_board_dict, sim_player_tokens, sim_player_information, sim_co_existance_dict, maximisingPlayer, sim_move, depth)

        #reverse 
        evaluation = result[-1]
        # print(f'\nMove to execute {move} generated at depth {depth}')
        # print(f'Eval: {evaluation}, Alpha: {alpha}, Beta: {beta}')



        # if its for us 
        if maximisingPlayer:
            #set alpha 
            if evaluation > alpha:
               alpha = evaluation
               best_move = move
            else:
                if evaluation < beta:
                    # beta = evaluation
                    break
                # print(f'too good')
                return [best_move, alpha]
            

        #minimising player 
        else:

            #beta set 
            if evaluation < beta:
                beta = evaluation
                best_move = move
            # we have a bigger value 
            else:
                if evaluation > alpha:
                    # alpha = evaluation
                    break
                # print(f'too good')
                return [best_move, beta]

        

    # decide for which player to return for 
    # print(f'Returning: {best_move} {alpha} {beta}')
    if maximisingPlayer:
        return [best_move, alpha]
    return [best_move, beta]


              
def simulate_move(sim_board_dict, sim_player_tokens, sim_player_information, sim_co_existance_dict, maximisingPlayer, move, depth):
    #execute move
    #print(f'Depth is currently {depth}')
    current_player = "us" if maximisingPlayer else "them"
    opponent = "them" if maximisingPlayer == "us" else "us"


    #throw
    if (move[0] == "throw"):
        # if win

        #guarantee throw anyway
        sim_player_information[current_player]['nTokens'] += 1
        # sim_player_information[current_player]['nThrowsRemaining'] -= 1
        sim_player_information[current_player]['furthestThrowDepth'] += 1

        #check outcome
        outcome = janken_checker_throw(sim_board_dict, sim_player_tokens, move[1], move[2])
        
        #if we win
        if outcome == janken_outcome.WIN:
            # print(f'A win has been found by {move[0]}, {move[1]} onto {move[2]}')
            sim_player_information[opponent]['nTokens'] -= 1

            #the move we want to simulate and add info on how to redo it 
            move_return = (move[0], move[1], move[2], "defeat", sim_board_dict[move[2]])

            #move_type, token_type, coord, outcome, 'what was there before'
            temp = [move[0], move[1], move[2], "defeat", sim_board_dict[move[2]]]
            # print(f'throw win: {temp}, {move}')

            #make the changes
            if move[2] in sim_co_existance_dict :
                sim_co_existance_dict.pop(move[2])
            #bd, pt, coord, piece, player
            add_token(sim_board_dict, sim_player_tokens, move[2], move[1], current_player)
            # remove_token(sim_board_dict, sim_player_tokens, move[2])

            # print(f"debug bd: {sim_board_dict}")

            move = move_return
            #print(f'Returning: {move}')
            return move
        
        #if we co-exist add to sim_co_exist
        #cb add coexist dict to check if throw on existing hex with same type
        elif outcome == janken_outcome.COEXIST:

            addIfCoexisting(sim_board_dict, sim_player_tokens, sim_co_existance_dict, move[2], current_player)

            return move

        elif outcome == janken_outcome.DEFEAT:
            # print(f'A win has been found by {move[0]}, {move[1]} onto {move[2]}')
            sim_player_information[current_player]['nTokens'] -= 1
            #the move we want to simulate and add info on how to redo it 
            move_return = (move[0], move[1], move[2], "suicide", sim_board_dict[move[2]])

            # print(f"debug bd: {sim_board_dict}")

            move = move_return
            #print(f'Returning: {move}')
            return move

        #or if empty
        else:

            #print(f'empty but check {move}')
            add_token(sim_board_dict, sim_player_tokens, move[2], move[1], current_player)
            #print(f'Returning: {move}')
            return move

    #swing/slide
    else:
        outcome = janken_checker(sim_board_dict, sim_player_tokens, move[2], move[3])

        if outcome == janken_outcome.WIN:
            sim_player_information[opponent]['nTokens'] -= 1
            # sim_player_information[current_player]['tokens_defeated'] += 1

             #move_type, token_type, coord, outcome, 'what was there before'
            move_return = (move[0], move[1], move[2], move[3], "defeat", sim_board_dict[move[3]])
            
            
            
            if move[3] in sim_co_existance_dict :
                sim_co_existance_dict.pop(move[3])


            remove_token(sim_board_dict, sim_player_tokens, move[3])
            move_token(sim_board_dict, sim_player_tokens, move)
            move = move_return
            #print(f'Returning: {move}')
            return move

        elif outcome == janken_outcome.DEFEAT:
            # print(f'A win has been found by {move[0]}, {move[1]} onto {move[2]}')
            sim_player_information[current_player]['nTokens'] -= 1
            #the move we want to simulate and add info on how to redo it 
            move_return = (move[0], move[1], move[2], move[3], "suicide", sim_board_dict[move[3]])

            # print(f"debug bd: {sim_board_dict}")
            remove_token(sim_board_dict, sim_player_tokens, move[2])
            move = move_return
            #print(f'Returning: {move}')
            return move
        
        #if we co-exist add to sim_co_exist
        #cb add coexist dict to check if throw on existing hex with same type
        elif outcome == janken_outcome.COEXIST:
            
            addIfCoexisting(sim_board_dict, sim_player_tokens, sim_co_existance_dict, move[3], current_player)

            move_token(sim_board_dict, sim_player_tokens, move)

            return move
        #same as above 
        else:
            move_token(sim_board_dict, sim_player_tokens, move)
            # print(f'Returning: {move}')
            return move


def unsimulate_move(sim_board_dict, sim_player_tokens, sim_player_information, sim_co_existance_dict, maximisingPlayer, move, depth):
    current_player = "us" if maximisingPlayer else "them"
    other_player = "them" if maximisingPlayer else "us"

    # (“throw”, type, coord, defeat, defeated_type)
    # if the move was a throw 
    # print(f'move to unsimulate: {move}')
    if move[0] == 'throw':

        #for each throw in general
        sim_player_information[current_player]["nTokens"] -= 1
        # sim_player_information[current_player]['nThrowsRemaining'] += 1
        sim_player_information[current_player]['furthestThrowDepth'] -= 1
        
        #defeated other token or us
        if len(move) > 3:

            # print(f'debug throw: {move}')
            #move_type, token_type, coord, outcome, 'what was there before'

            if move[3] == "defeat" :
                #revert the move    
                sim_board_dict[move[2]] = move[-1]
                sim_player_tokens[move[2]] = other_player

                #add a token back 
                sim_player_information[other_player]["nTokens"] += 1
                #revert our defeat count 
                # sim_player_information[current_player]["tokens_defeated"] -= 1
            elif move[3] == "suicide" :
                sim_player_information[current_player]["nTokens"] += 1


        #generic throw
        else:
            # (“throw”, type, coord)
            #then reflect sim_cx dict if needed 
            #if the coordinate was in the co-existance dict 
            if move[-1] in sim_co_existance_dict:

                #the first token will always be shown there
                removeFromCoexistanceDict(sim_board_dict, sim_player_tokens, sim_co_existance_dict, 
                                            move[-1], current_player)

                                        

            else:
                #just remove that move
                sim_board_dict[move[-1]] = ''
                sim_board_dict.pop(move[-1], None)
                sim_player_tokens[move[-1]] = ''
                sim_player_tokens.pop(move[-1], None)

            

        

    #otherwise do for generic swing/slide
    else:
        # (move_type, type, curr_coord, next_coord , defeat, defeated_type) 
        if len(move) > 4:

            #for coexistance
            if move[4] == "coexist":
                
                #remove from current position
                removeFromCoexistanceDict(sim_board_dict, sim_player_tokens, sim_co_existance_dict, move[3], current_player)

                #if previous coord leads to co-existance also (sneaky sneaky)
                if move[2] in sim_co_existance_dict and sim_player_tokens[move[2]] == move[1]:
                    
                    #add to next position
                    addIfCoexisting(sim_board_dict, sim_player_tokens, sim_co_existance_dict, move[2], current_player)

                #otherwise just do normally 
                else:
                    #move that token back 
                    sim_board_dict[move[2]] = sim_board_dict[move[3]]
                    sim_player_tokens[move[2]] = sim_player_tokens[move[3]]

            elif move[4] == "suicide":
                sim_board_dict[move[2]] = move[1]
                sim_player_tokens[move[2]] = current_player

            #for empty slides and stuff
            else:
                #move that token back 
                sim_board_dict[move[2]] = sim_board_dict[move[3]]
                sim_player_tokens[move[2]] = sim_player_tokens[move[3]]

                #reintroduce the defeated token 
                sim_board_dict[move[3]] = move[-1]
                sim_player_tokens[move[3]] = other_player

                #decrease defeat count
                # sim_player_information[current_player]['tokens_defeated'] -=1
                #increase other player's token count 
                sim_player_information[other_player]['nTokens'] += 1

        #otherwise generic move to an empty square
        else:
            #move that token back
            sim_board_dict[move[2]] = sim_board_dict[move[3]]
            sim_player_tokens[move[2]] = sim_player_tokens[move[3]]

            #remove token from previous position
            sim_board_dict.pop(move[3], None)
            sim_player_tokens.pop(move[3], None)


