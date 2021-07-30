import math
import numpy
from Pain_Peko.minimax.moves import generate_possible_swings
from Pain_Peko.player.rules import *
from Pain_Peko.minimax.moves import *
from Pain_Peko.minimax.util.hex_util import *


# evaluate a current game state
#player_information = player information literally 
def evaluate(board_dict, player_tokens, 
            previous_bd, previous_pt, 
            player_information, player_side, 
            move_made, edge_boundaries, turnNo):


    #define how many RPS and where the token locations are for each player 
    counter = {'us': { "token_composition": [0,0,0], "token_locations": []}, 
                'them': { "token_composition": [0,0,0], "token_locations": []}}

    #the magic stuff o w o
    #chibai [assume co-existance-dict is parsed in]
    evaluation_value = 0
    allied_tokens = []
    enemy_tokens = []
    player = "us" if player_side else "them"
    player_side_on_board = player_information[player]["player_side"]
    

    #chibai [can we refer to sim_cx?]
    for token in board_dict:
        if player_tokens[token] == 'us' :
            allied_tokens.append(token)

        if player_tokens[token] == 'them' :
            enemy_tokens.append(token)

    # print(f'Allied: {allied_tokens}')
    # print(f'Enemy: {enemy_tokens}')

    
    # C1. Token Difference 
    C1 = token_difference(board_dict, player_tokens, counter)
    evaluation_value += C1
    
    


    # # C2. Throw Difference
    C2 = checkThrowsAvailable(board_dict, player_tokens, player_information)
    evaluation_value += C2
    



    # C3. Throw Depth
    C3 = checkDepthOfThrow(board_dict, player_tokens, player_information)
    evaluation_value += C3
    


    # C4. Structure Composition via Clustering 
    C4 = token_structure(board_dict, player_tokens, player_information)
    evaluation_value += C4
    # print(f'C4: {evaluation_value}')


    # C5. Token Mobility
    C5 = token_mobility(board_dict, player_tokens, allied_tokens, player_information)
    evaluation_value += C5
    


    # # C6. Token Vulnerability
    C6 = token_vulnerability(board_dict, player_tokens, allied_tokens, enemy_tokens, edge_boundaries)
    evaluation_value += C6
    

    # # C7. State Authenticity
    # is there a difference in the board and have we defeat anything? Or get defeated 
    # skew 

    C7 = board_authenticity(board_dict, player_tokens, previous_bd, previous_pt, 
                            player_side, player_side_on_board, edge_boundaries)
    evaluation_value += C7

    # # C8: How desirable would this move be?
    C8 = move_desirability(previous_bd, board_dict, move_made, allied_tokens, enemy_tokens, edge_boundaries)
    evaluation_value += C8

    #consider turn number as well
    #if we are at a high turn number and we have some throws 
    if turnNo > 50 and move_made[0] == "throw":
        evaluation_value += 5 * (turnNo // 25)



    # print(f'Evaluation for {player}')
    # print(f'Move: {move_made}')
    # print(f'Token Diff C1: {C1}')
    # print(f'Throw Diff C2: {C2}')
    # print(f'Throw Depth C3: {C3}')
    # print(f'Clustering C4: {C4}')
    # print(f'Mobility: C5: {C5}')
    # print(f'Vulnerability: C6: {C6}')
    # print(f'Board Authenticity: C7: {C7}')
    # print(f'Move Desirability: C8: {C8}')
    
    
    

    #then on top of that, shove it into an additional layer of move ordering 
    # i.e. we knw


    # print(f'Final Evaluated: {evaluation_value}\n')
    return evaluation_value



# C1. Token Difference [-50,50]
def token_difference(board_dict, player_tokens, counter):
    token_count = 0

    #count enemy tokens 

    #chibai [consider co_existance, into counter]
    #if co-existance then + value [1] or [2] is us or them
    for token in board_dict:
        if board_dict[token] == "r":
            counter[player_tokens[token]]["token_composition"][0] += 1
        elif board_dict[token] == "p":
            counter[player_tokens[token]]["token_composition"][1] += 1
        elif board_dict[token] == "s":
            counter[player_tokens[token]]["token_composition"][2] += 1  

        #otherwise count for us 
        if player_tokens[token] == "us":
            counter["us"]["token_locations"].append(token)
        else:
            counter["them"]["token_locations"].append(token)


    # get values
    us = counter["us"]["token_composition"]
    them  = counter ["them"]["token_composition"]

    #rock
    token_count += us[0] * (-them[1]*20 + them[2]*20)
    #paper
    token_count += us[1]* ( -them[2]*20 + them[0]*20)
    # scissors 
    token_count += us[2]* ( -them[0]*20 + them[1]*20)

    token_count += (us[0] + us[1] + us[2] - them[0] - them[1] -them[2]) * 20

    return token_count
    

# C2. Throw Difference [Arbitrary = 5]
def checkThrowsAvailable(board_dict, player_tokens, players):

    token_us = 0
    token_them = 0

    #look up how many tokens are on board
    for token in board_dict:
        if player_tokens[token] == "us" :
            token_us += 1
        if player_tokens[token] == "them" :
            token_them += 1

    players["us"]["nTokens"] = token_us
    players["them"]["nTokens"] = token_them

    return ((9 - token_us) - (9 - token_them)) * 12 # times arbitiary value (?)
    
# C3. Throw Depth [Arbitrary = 5]
def checkDepthOfThrow(board_dict, player_tokens, players):

    #check how far you can throw on the board
    depthThrow_us = players["us"]["nTokens"]
    depthThrow_them = players["them"]["nTokens"]

    players["us"]["furthestThrowDepth"] = depthThrow_us
    players["them"]["furthestThrowDepth"] = depthThrow_them

    return (depthThrow_us - depthThrow_them) * 15 # times arbitiary value


#initialise allCluster outside the function as []
# INPUT is allied_board_dict need to filter the board_dict first as "us" and "them"
# before inputting into this function

# C4. Cluster Composition
# Part 1

# allied_ bd: [("r", (0,1), ...]
def token_structure (board_dict, player_tokens, players):


    token_structure = 0

    #allied enemy bd temp
    allied_bd = {}
    enemy_bd = {}
    co_existance_count = {}

    #clusters
    allCluster_us = []
    allCluster_them = []

    # handling here to precompute everything?
    # prevent extra processing 

    #chibai [co_existance_count, if in co-existance add to both]
    for token in board_dict :
        if player_tokens[token] == "us" :
            allied_bd[token] = board_dict[token]

        if player_tokens[token] == "them" :
            enemy_bd[token] = board_dict[token]
    

    #chibai, include in createCluster
    allCluster_us = createCluster(board_dict, allied_bd, player_tokens, players, allCluster_us)
    allCluster_them = createCluster(board_dict, enemy_bd, player_tokens, players, allCluster_them)
    
    for i in evaluateAllClusterComponent(board_dict, player_tokens, players, allCluster_us, allCluster_them) :
        token_structure += i

    return token_structure

# create clusters 
def createCluster(board_dict, allied_board_dict, new_player_tokens, players, allCluster):

    #if theres no clusters in there 
    if allCluster == [] :

        #start with one random allied token 
        if len(allied_board_dict) == 0 :
            return allCluster

        for token in allied_board_dict :

        # print(f'Random: {random_token}')
        #add to the list 
            allCluster.append([(board_dict[token], token)])

    # print(f'Cluster: {allCluster}')

    #keep track of the clusters (theyre commutive )
    
    

    #chibai
    #ASSUMPTION: since its co-existance, can we just ignore that fact?
    #and like if its ok to suicide our token to get theirs do it?

    # for all the clusters we have 
    for cluster in allCluster :       
        #for each token that exists in that cluster 

        #for all the other tokens as our ally
        if len(allied_board_dict) == 1 :
            return allCluster
        
        #for the other tokens 
        for other_token in allied_board_dict :

            #if the token is not our token that we are looking at 
            if (board_dict[other_token], other_token) not in cluster :
                
                # print(f'other_token: {(board_dict[other_token], other_token)}')

                #if the other token exists in within a radius of the token in the cluster
                # or in this case right next to the oken  

                adjacent_token_cluster = []
                for token in cluster :
                    adjacent_token_cluster += generate_adjacent_coords(token[1])
                
                if other_token in adjacent_token_cluster :
                            
                    # if it is, find the specific cluster it exists in 
                    for other_cluster in allCluster :
                                
                        #then if it exists there
                        if (board_dict[other_token], other_token) in other_cluster :

                            #combine both cluster and perform
                            # ANSCHLUSS 
                            cluster += other_cluster
                            #remove the other-cluster from allCluster as its a part of 
                            allCluster.remove(other_cluster)
                                


                    
        
    return allCluster

# Part 2
# count and evaluate each cluster component 
def evaluateAllClusterComponent(board_dict, player_tokens, players, allCluster_us, allCluster_them):

    #same index = same cluster
    evaluation_point_per_cluster = []

    # for each of our clusters
    for cluster_us in allCluster_us :

        #calculate midpoint of cluster_us
        midpoint_cluster_us = find_midpoint_in_cluster(cluster_us)
        # print(f'Midpoint_cluster_us: {midpoint_cluster_us}')

        #find nearest cluster_them
        nearest_cluster_them = []

        #arbitrary max value, can tweak [mahou suuji]
        distance = 99


        # FIND NEAREST CLUSTER TO US 
        # for each of their clusters 
        for cluster_them in allCluster_them :
            
            #calculate midpoint of cluster_them
            midpoint_cluster_them = find_midpoint_in_cluster(cluster_them)
            # print(f'Midpoint_cluster_them: {midpoint_cluster_them}')

            euclidean_distance = math.sqrt((midpoint_cluster_them[0] - midpoint_cluster_us[0])**2 + (midpoint_cluster_them[1] - midpoint_cluster_us[1])**2 )

            #compare by distance 
            if distance > euclidean_distance :

                nearest_cluster_them = cluster_them
                distance = euclidean_distance

        # create function to compare_component_cluster within cluster

        evaluation_point_per_cluster.append(compare_component_cluster(cluster_us, nearest_cluster_them))


    return evaluation_point_per_cluster

# cluster is in the format of [("r",(1,1)),("s",(1,2)), ... ]
def find_midpoint_in_cluster(cluster):

    # initialise midpoint
    # print(f'Midpoint_cluster: {cluster}')
    midpoint = [0,0]
    midpoint[0] = cluster[0][1][0]
    midpoint[1] = cluster[0][1][1]    
    # print(f'Midpoint: {midpoint}')

    #keep finding the average: python will round for us 
    for token in cluster[1:] :
        midpoint[0] = (midpoint[0] + token[1][0])/2
        midpoint[1] = (midpoint[1] + token[1][1])/2

    return (midpoint[0], midpoint[1])

# evaluates tokens within both clusters 
#chibai we might need to consider co-existance 
def compare_component_cluster(cluster_us, cluster_them):



    # use a similar algorithm as token evaluation
    token_composition_cluster_us = [0,0,0]
    us = [0,0,0]
    token_composition_cluster_them = [0,0,0]
    them = [0,0,0]
    evaluation_point = 0

    #chibai:
    # assuming we considered co-existance in cluster-us-cluster them should be ok 
    #compare ours 
    for token in cluster_us :

        # print(f'composition: {cluster_us}')

        if token[0] == 'r' :
            token_composition_cluster_us[0] += 1

        if token[0] == 's' :
            token_composition_cluster_us[1] += 1

        if token[0] == 'p' :
            token_composition_cluster_us[2] += 1

    #vs theirs
    for token in cluster_them :
        if token[0] == 'r' :
            token_composition_cluster_them[0] += 1

        if token[0] == 's' :
            token_composition_cluster_them[1] += 1

        if token[0] == 'p' :
            token_composition_cluster_them[2] += 1

    # dick measuring contest here 
    evaluation_point += token_composition_cluster_us[0] + token_composition_cluster_us[1] + token_composition_cluster_us[2] - token_composition_cluster_them[0]- token_composition_cluster_them[2]-token_composition_cluster_them[1]
    #rock
    evaluation_point += token_composition_cluster_us[0] * (-token_composition_cluster_them[1]*2 + token_composition_cluster_them[2]*2)
    #paper
    evaluation_point += token_composition_cluster_us[1] * (-token_composition_cluster_them[2]*2 + token_composition_cluster_them[0]*2)
    # scissors 
    evaluation_point += token_composition_cluster_us[2] * (-token_composition_cluster_them[0]*2 + token_composition_cluster_them[1]*2)

    
    return evaluation_point


# C5. Token Mobility [-20, 20]
# Where could we go?
# EMPTY = 2, WIN = 4 LOSE = -6
def token_mobility(board_dict, player_tokens, allied_tokens, player):

    token_mobility = 0
    
    #for all allied tokens
    for token in allied_tokens:
        #check its surroundings
        for adjacent in generate_adjacent_coords(token):

            #if we can actually swing over it cuz it has to be allied
            if adjacent in allied_tokens:

                #for each swing possibility add 2*npossibilites
                #this function already returns valid swings from defeatable enemies to empty hexes
                token_mobility = len(generate_possible_swings(board_dict, player_tokens, allied_tokens, token, "all")) * 2


            #empty spaces still count right?
            if adjacent not in board_dict:
                token_mobility += 2

            #otherwise its an enemy 
            else:

                #if the outcome we get is a good one 
                if janken_checker(board_dict, player_tokens, token, adjacent) == janken_outcome.WIN:
                    token_mobility += 4

                # punish it for losing
                elif janken_checker(board_dict, player_tokens, token, adjacent) == janken_outcome.DEFEAT:
                    token_mobility -= 6

    return token_mobility



# C6. Token Vulnerability (AKA win condition)
def token_vulnerability(board_dict, player_tokens, allied_tokens, enemy_tokens, edge_boundaries):

    overall_vulnerability_for_player = 0

    #temp allied 
    visited_allies = allied_tokens

    #draw a 2 hex wide hex around the current token 
    for token in allied_tokens:

        token_vulnerability = 0

        # retrieve a list of tokens that surround the token 
        surrounding_tokens = [found_coord for found_coord in hex_region_generator(token, 2, edge_boundaries) if found_coord in board_dict]

        #if empty or if all of them are allied 
        #chibai: co-existance might occur and it might be shown as enemy
        if len(surrounding_tokens) == 0 or all(player_tokens[coord] == "us" for coord in surrounding_tokens) :
            return token_vulnerability
    

        # otherwise go through all of them 
        for found_token in surrounding_tokens:
            
            #check how far it is
            distance = distance_in_hexes(token, found_token)

            #prevent 0 division error
            if distance == 0:
                distance = 1

            #get the possible outcome
            outcome = janken_checker(board_dict, player_tokens, token, found_token)


            vulnerability_value = 0

            # for enemies
            #chibai: co-existance might be able to be ignored here unless it can defeat our token 
            if found_token in enemy_tokens:
                
                #if you can win
                if outcome == janken_outcome.WIN:
                    vulnerability_value += 2 #push for possible wins 

                elif outcome == janken_outcome.DEFEAT:
                    vulnerability_value -= 8 #punish the values for bad choices

                #also check if theres any allied tokens of the same type as an enemy
                #e.g. r defeat s but theres a p nearby, so if theres an allied s nearby be ballsy
                #in case your r gets defeated, your s can swing and yeet them
                #so look for allied s in case 
                reinforcement_counter = allied_tokens.count(board_dict[coord] == board_dict[found_token] for coord in surrounding_tokens)

                vulnerability_value += reinforcement_counter

            #final value here 
            token_vulnerability +=  (2/ distance) * vulnerability_value/2

        #as a way of pruning, we remove allied tokens that happen to 
        # visited_allies.remove(token)
        overall_vulnerability_for_player += token_vulnerability


    return overall_vulnerability_for_player


# C7. State Authenticity
def board_authenticity(board_dict, player_tokens, previous_bd, previous_pt, 
                        player_type, player_side_on_board, board_edge):

    board_value = 0
    player = "us" if player_type else "them"
    
    #determine which dict to compare with 
    if len(board_dict) > len(previous_bd):
        board_of_focus = board_dict.copy()
        other_board = previous_bd.copy()
        larger_board = "curr"
    else:
        board_of_focus = previous_bd.copy()
        other_board = board_dict.copy()
        larger_board = "prev"

    #same length?
    if len(board_dict) == len(previous_bd): larger_board = "same"

    #identical keys?
    if np.array_equal(list(board_dict.keys()), list(previous_bd.keys())): larger_board = "identical"

    #find where the difference exists 
    difference = [token for token in board_of_focus if token not in other_board]

    #case 1: no difference in keys
    if larger_board == "identical":

        #if the values are the same even for the values for BOTH then we literally threw on ourselves, and thats stupid
        if np.array_equal(list(board_dict.values()), list(previous_bd.values())) and np.array_equal(list(player_tokens.keys()), list(previous_pt.keys())) and np.array_equal(list(player_tokens.values()), list(previous_pt.values())):
            
            #if we did throw on an exising token, did we actually kill an enemy 
            # from that and was it worth it?
            board_value -= 10
        else:
            #otherwise we might have thrown over a piece and got some spicy result 
            #token values are different
            if not np.array_equal(list(board_dict.values()), list(previous_bd.values())) and not np.array_equal(list(player_tokens.values()), list(previous_pt.values())):
                board_value += 20   #spicy shit here 

            #else failsafe
            else:
                board_value -= 10

               
                
    #case 2: slight difference        
    #we made advances somehow, lets see how good they are 
    if larger_board == "curr":

        #i forgot to implement this lol
        for token in difference:
            token_type = board_dict[token]
            token_player = player_tokens[token]

            #yes we killed something, reward!
            if board_dict[token] == player:
                board_value += 20
            #otherwise we fucked up and died 
            else:
                board_value -= 20


    #we went down a value, lets see if we died or we killed something
    #otherwise its prev
    elif larger_board == "prev":

        for token in difference:
            token_type = previous_bd[token]
            token_player = previous_pt[token]

            #yes we killed something, reward!
            if previous_pt[token] != player:
                board_value += 20

            #otherwise we fucked up and died 
            else:
                board_value -= 20
    
    # otherwise no difference, we probably just slid or something
    elif larger_board == "same":
        #find out which token it was 
        
        prev_diff_list = [token for token in previous_bd if token not in board_dict]
        curr_diff_list = [token for token in board_dict if token not in previous_bd]


        if len(prev_diff_list) > 0 and len(curr_diff_list) > 0:
            
            prev_diff = prev_diff_list[0]
            curr_diff = curr_diff_list[0]

            #get the difference 
            relative_direction = tuple(np.subtract(curr_diff, prev_diff))
            distance = distance_in_hexes(prev_diff, curr_diff)


            #did we swing or slide
            if distance == 2:
                board_value += 5  #swings are good
            else:
                board_value += 2  #slides we remain neutral

            #did we move away from our intended position?
            #if we backtracked in context [try not to punish too hard]
            if relative_direction[0] < 0:
                board_value -= 8   # we dont want to move backwards only forwards
            else:
                board_value += 2

        
    return board_value
        

    
# C8: find out if we either moved to an edge or suicided 
def move_desirability(previous_bd, board_dict, move_made, allied_bd, other_bd, edge):
    #find out which token it was 

    move_desirability = 0

    # print(f'prev: {previous_bd}, curr: {board_dict}')
    # print(f'Move: {move_made}')

    #ARE WE ON EDGE?
    #if its not on a board edge good on you
    if move_made[-1] not in edge:
        move_desirability += 10

    #not really a wise choice unless you want to be greedy
    else:
        move_desirability -= 5


    # MOVE QUALITY
    # defeated anything? suicide? co-existance?
    #check move type
    move_type = move_made[0]

    # check on previous_bd to evaluate choice 
    if move_type == "throw":

        #nerf the throw for a bit 
        move_desirability -= 8
        #check if it was thrown on an enemy
        # does the move exist in the previous_bd? 
        
        if move_made[-1] in previous_bd and move_made[-1] in board_dict:

            #chibai co:existance here, need to factor in co-exsitance to
            #two token_outcome

            #what result does it bring?
            move_desirability += two_token_outcome(previous_bd[move_made[-1]], board_dict[move_made[-1]])


        # otherwise its just a generic throw, be neutral
        else:
            move_desirability += 5
    
    # otherwise its a swing/slide
    else:
        
        #get the move types
        if len(move_made) < 3:
            return 2

        prev_coord = move_made[2]
        dest_coord = move_made[3]

        if prev_coord in board_dict:
            # if destination coord in prev_bd (i.e there is something there when we are sliding onto it)
            if dest_coord in previous_bd and prev_coord in previous_bd:
                
                #chibai co:existance here, need to factor in co-exsitance to
                #two token_outcome
                #then check the outcome 
                move_desirability = two_token_outcome(previous_bd[prev_coord], previous_bd[dest_coord])

        # otherwise we just slide normally (the location has been determined above )
        else:
            move_desirability += 5

    return move_desirability
    
    # #get the difference 
    # relative_direction = tuple(np.subtract(curr_diff, prev_diff))
    # distance = distance_in_hexes(prev_diff, curr_diff)

    # return (prev_diff, curr_diff, relative_direction, distance)


#chibai co:existance here, need to factor in co-exsitance to
#two token_outcome
def two_token_outcome(token_type, other_token_type):

    outcome = janken_test(token_type, other_token_type)


    #then tweak the value we return
    # we threw on something thats nice
    if outcome == janken_outcome.WIN:
       return 20

    if outcome == janken_outcome.DEFEAT:
        return -40

    if outcome == janken_outcome.COEXIST:
        return 10

