import numpy as np


BOARD_SIZE = 15
class Game:
    def __init__(self,tiles):
        self.tiles = tiles
        self.current_tile = self.tiles[0]
        self.turn_count = 0

        self.dice={ 1: ([0,1], None), 
                    2: ([0,1,2], 0.5), 
                    3: ([0,1,2,3], 1), 
                    4: ([-3,-1,3,5], 1)}
        
        

    def roll_dice(self, dice_id):
        self.turn_count += 1
        dice_used = self.dice[dice_id]
        trap_chance = dice_used[1]
        dice_result = dice_used[0][np.random.randint(0,len(dice_used[0]))]
        # print("dice_result", dice_result)
        #move
        if dice_result < 0:
            self.current_tile = self.current_tile.step_backwards(-dice_result)
        else: 
            self.current_tile = self.current_tile.step_forward(dice_result, is_start_tile_3 = (self.current_tile.tile_id == 3))

        
        #activate traps if needed
        self.current_tile = self.activate_trap(trap_chance)
        


    def activate_trap(self,trap_probabilty): #Note, there is no "cascade trigerring" (see instructions section 5)
        trap_type = self.current_tile.trap
        
        if trap_probabilty is None or trap_type == 0: #either safe dice or regular tile
            return self.current_tile
        
        if trap_probabilty > np.random.random(): #if trap activates
            # print("TRAP ACTIVATED, type:",trap_type)
            if trap_type == 1: #restart_trap
                return self.current_tile.step_backwards(15) #move back to beginning, cannot reactivate traps
            
            if trap_type == 2: #penalty trap
                return self.current_tile.step_backwards(3) #move back 3 spaces, cannot reactivate traps
            
            if trap_type == 3: #prison trap
                self.turn_count += 1
        return self.current_tile #No traps activated
    
    def check_win(self):
        return (self.current_tile.tile_id == 15)


    #TO REMOVE OR CHANGE
    #This function (and this function only) was written using Gemini
    def print_board(self):
        p_id = self.current_tile.tile_id
        
        # ANSI Color Codes
        RED = '\033[91m'    # Traps
        GREEN = '\033[92m'  # Current Player
        BLUE = '\033[94m'   # Goal
        RESET = '\033[0m'

        def format_tile(tid):
            tile_obj = self.tiles[tid-1]
            
            # Determine Color Priority: Player > Goal > Trap
            if tid == p_id:
                color = GREEN
                label = f"[{tid:2}]"
            elif tid == 15:
                color = BLUE
                label = f" {tid:2} "
            elif tile_obj.trap != 0:
                color = RED
                label = f" {tid:2} "
            else:
                color = RESET
                label = f" {tid:2} "
                
            return f"{color}{label}{RESET}"
        # Row 1: Main Path (1-10) + Goal (15)
        # Each tile is 4 chars wide + 1 char for arrow = 5 chars per segment
        row1 = "→".join([format_tile(i) for i in range(1, 11)]) + "→" + format_tile(15)
        
        # Row 2: Branching Arrows
        # Positioned exactly under Tile 3 and before Tile 15
        row2 = "            ↘                                     ↗"
        
        # Row 3: Fast Lane (11-14)
        # Spaced to align with the diagonal arrows
        row3 = f"            {format_tile(11)} → {format_tile(12)} → {format_tile(13)} → {format_tile(14)}"

        print("-" * 55)
        print(row1)
        print(row2)
        print(row3)
        print("-" * 55)     
     



class Tile:
    def __init__(self, id, trap):
        self.tile_id = id
        self.next_tile = [] #list of Tiles, since tile 3 needs 2 next_tiles
        self.previous_tile = None #Tile, no use for more than 1 previous tile
        self.trap = trap # 0 = ordinary square, 1 = restart, 2 = penalty (-3 tiles), 3 prison (skip turn)
    
    def step(self, nb_tiles, is_start_tile_3 = False, tile_3_rand = None):
        if nb_tiles > 0:
            return self.step_forward(nb_tiles, is_start_tile_3, tile_3_rand)
        elif nb_tiles < 0:
            return self.step_backwards(-1*nb_tiles)
        return self

    def step_forward(self, nb_tiles,is_start_tile_3 = False, tile_3_rand = None):
        #Step forward nb_tiles amount of steps
        #next_tile[0] in case of tile 3, take longest path by default
        if nb_tiles > 0:
            if is_start_tile_3:
                if tile_3_rand is None:
                    tile_3_rand = np.random.random()
                if tile_3_rand > 0.5:
                    return self.next_tile[1].step_forward(nb_tiles-1) #Branch to fast lane
                else:
                    return self.next_tile[0].step_forward(nb_tiles-1)
            return self.next_tile[0].step_forward(nb_tiles-1) 
        else:
            return self
    
    def step_backwards(self, nb_tiles):
        #Step backwards nb_tiles amount of steps
        if nb_tiles > 0:
            return self.previous_tile.step_backwards(nb_tiles-1)
        else:
            return self


def generate_board(layout, circle):
    tiles_list = [None]*15

    #initialize all tiles
    for i in range(15):
        tiles_list[i] = Tile(id=i+1, trap=layout[i])

    #Connect tiles
    for i in range(14):
        tiles_list[i].next_tile = [tiles_list[i+1]]
        tiles_list[i+1].previous_tile = tiles_list[i]

    #Special connections
    tiles_list[0].previous_tile = tiles_list[0] #First tile connects to itself
    tiles_list[2].next_tile += [tiles_list[10]] #Tile 3 add a connection to fast lane
    tiles_list[9].next_tile = [tiles_list[14]] #Override tile 10 to connect to tile 15 (not to 11)
    tiles_list[14].next_tile = [tiles_list[0]] if circle else [tiles_list[14]] #Last tile connects to self or to tile 1
    
    return tiles_list
    

def playManual(layout,circle):
    game = Game(generate_board(layout,circle))

    while(not game.check_win()):
        #TODO change to MDP
        print("----- TURN",game.turn_count,"-------")
        game.roll_dice(int(input("Enter dice choice (1:security, 2:normal, 3:risky, 4:special)\n"))) 
        game.print_board()
        print()
        
    print("You won the game in",game.turn_count,"turns!")
    #TODO change to (Expec, dice)
    return game.turn_count


def expected_value(landed_tile, trap_chance, V):
        trap_type = landed_tile.trap

        # either safe dice or regular tile
        if trap_chance is None or trap_type == 0:
            return V[landed_tile.tile_id - 1]

        # trap does not activate
        expected_val = (1 - trap_chance) * V[landed_tile.tile_id - 1]

        # trap activates
        if trap_type == 1:  # restart_trap
            trapped_tile = landed_tile.step_backwards(15)  # move back to beginning, cannot reactivate traps
            expected_val += trap_chance * V[trapped_tile.tile_id - 1]

        elif trap_type == 2:  # penalty trap
            trapped_tile = landed_tile.step_backwards(3) 
            expected_val += trap_chance * V[trapped_tile.tile_id - 1]

        elif trap_type == 3:  # prison trap, adds 1 for bonus turn wasted
            expected_val += trap_chance * (1 + V[landed_tile.tile_id - 1])

        return expected_val


# Checks if node 15 is reacheable depending on which dice are available
def check_layout_convergeance(layout, circle, dice_available = [1,2,3,4]):
    graph = np.zeros(shape=(len(layout),len(layout)))
    game = Game(generate_board(layout,circle))
    # construct_graph
    for starting_tile in game.tiles:
        for die in dice_available:
            rolls = game.dice[die][0]
            trap_chance = game.dice[die][1]
            for roll in rolls:
                if die == 2: #check path for trap and no trap
                    game.current_tile = starting_tile.step_forward(roll, is_start_tile_3 = (starting_tile.tile_id == 3))
                    graph[starting_tile.tile_id-1][game.current_tile.tile_id-1] = 1 #No trap

                    end_tile = game.activate_trap(trap_chance)
                    graph[starting_tile.tile_id-1][end_tile.tile_id-1] = 1 #Trap
                else: #Dice 1, 3 and 4
                    if roll < 0:
                        game.current_tile = starting_tile.step_backwards(-roll)
                    else: 
                        game.current_tile = starting_tile.step_forward(roll, is_start_tile_3 = (starting_tile.tile_id == 3))

                    #activate traps or not (deterministic)
                    end_tile = game.activate_trap(trap_chance)
                    graph[starting_tile.tile_id-1][end_tile.tile_id-1] = 1 #add link between two tiles in graph

    return is_connected(graph,0,14)



#Used to check if node 15 is reacheable
#Uses DFS
def is_connected(matrix, start, target, visited=None):
    if visited is None:
        visited = set()
    
    #Base Case
    if start == target:
        return True
    
    visited.add(start)
    
    #DFS
    for neighbor, connected in enumerate(matrix[start]):
        if connected == 1 and neighbor not in visited:
            # Recursive call
            if is_connected(matrix, neighbor, target, visited):
                return True    
    return False


                

                




def action(game, start_tile, dice_id, V):

    dice_rolls = game.dice[dice_id][0]
    trap_chance = game.dice[dice_id][1]

    curr_sum = 0.0


    for roll in dice_rolls:
        if start_tile.tile_id == 3 and roll > 0:
            next_tile_fast = start_tile.step(roll, True, 1)
            next_tile_slow = start_tile.step(roll, True, 0)

            curr_sum += 0.5 * expected_value(next_tile_fast, trap_chance, V)
            curr_sum += 0.5 * expected_value(next_tile_slow, trap_chance, V)
        else:
            next_tile = start_tile.step(roll)
            curr_sum += expected_value(next_tile, trap_chance, V)

    

    return 1 + curr_sum / len(dice_rolls)

def evaluate_policy(layout, circle, policy, name, max_iter=10000):
    game = Game(generate_board(layout, circle))
    V = np.ones(BOARD_SIZE)
    V[-1] = 0  # not really need this

    for it in range(max_iter):
        newV = np.copy(V)
        for tile in game.tiles:
            tile_idx = tile.tile_id - 1

            if tile.tile_id == BOARD_SIZE:
                newV[tile_idx] = 0
                continue

            if name == "uniform_random":
                newV[tile_idx] = np.mean([action(game, tile, dice_id, V) for dice_id in range(1, 5)])
            elif name == "always":
                dice_id = policy # deterministic dice
                newV[tile_idx] = action(game, tile, dice_id, V)
            else:  # optimal policy
                dice_id = policy[tile_idx]
                newV[tile_idx] = action(game, tile, dice_id, V)
            
        err = np.max(np.abs(newV - V))
        if it % 100 == 0: #ecause sometimes we have convergence problems..
            if name == 'always':
                print(f"iter={it} in evaluate policy for {name} {policy}, err={err}")
            else:
                print(f"iter={it} in evaluate policy for {name}, err={err}")
        if np.max(np.abs(newV - V)) < 0.0001:
            V = newV
            break
        V = newV
    return V[:-1]


def simulate_policy(layout, circle, policy, name, n_games=1000):
    turns = []

    for _ in range(n_games):
        game = Game(generate_board(layout, circle))
        game.current_tile = game.tiles[0]  # reset to start
        game.turn_count = 0

        while not game.check_win():
            current_tile_id = game.current_tile.tile_id
            if name == "uniform_random":
                dice_id = policy()
                game.roll_dice(dice_id)
            elif name == "always":
                dice_id = policy
                game.roll_dice(dice_id)
            else:  # optimal policy
                dice_id = policy[current_tile_id-1]
                game.roll_dice(dice_id)

        turns.append(game.turn_count)
    mean_turns = np.mean(turns)
    std_turns = np.std(turns) / np.sqrt(n_games) 

    return mean_turns, std_turns


def markovDecision(layout, circle):
    game = Game(generate_board(layout, circle))
    V = np.ones(BOARD_SIZE)
    policy = np.ones(BOARD_SIZE, dtype=int)
    stability_tol = 0.0001
    max_iterations = 10000
    V[-1] = 0  ## situation where player lands on final square

    for it in range(max_iterations):
        newV = np.copy(V)

        for tile in game.tiles:
            tile_idx = tile.tile_id - 1

            if tile.tile_id == BOARD_SIZE:
                newV[tile_idx] = 0
                continue

            currMin = np.inf
            currMindice = 1

            for i in range(1, 5):  # each dice
                startTile = tile
                endTile = tile
                currSum = 0

                dice_rolls = game.dice[i][0]
                trap_chance = game.dice[i][1]

                for roll in dice_rolls:  # each possible roll
                    if startTile.tile_id == 3 and roll > 0:
                        next_tile_fast = startTile.step(roll, True, 1)
                        next_tile_slow = startTile.step(roll, True, 0)

                        currSum += 0.5 * expected_value(next_tile_fast, trap_chance, V)
                        currSum += 0.5 * expected_value(next_tile_slow, trap_chance, V)
                    else:
                        next_tile = startTile.step(roll)
                        currSum += expected_value(next_tile, trap_chance, V)
                expectedCost = 1 + (currSum * 1.0 / len(dice_rolls))

                if expectedCost < currMin:
                    currMin = expectedCost
                    currMindice = i

            newV[tile_idx] = currMin
            policy[tile_idx] = currMindice
        err = np.max(np.abs(newV - V))
        if it % 100 == 0:
            print(f"iter={it} in markov decision, err={err}")
        if np.max(np.abs(newV - V)) < stability_tol: # Here, we need to check the global convergence of the whole states, not just one state.
            V = newV
            print("Convergence achieved after", it+1, "iterations.")
            break

        V = np.copy(newV)

    # print("The total expected number of turns is:", V)
    print("The optimal cost without last tile is:", V[:-1])
    # print("The optimal policy is:", policy)
    print("The optimal policy without last tile is:", policy[:-1])
    return [V[:-1], policy[:-1]] # We should not return the expected cost and the policy (=0) of the last tile!


def policy_uniform_random(): # Policy purely random choice of dice
    return lambda: np.random.choice([1,2,3,4])

def compare_strategies(layout, circle, n_games = 1000):
    optimal_results = markovDecision(layout, circle)
    opt_cost = optimal_results[0]
    opt_policy = optimal_results[1]

    res = {}
    res['Optimal_theoretical'] = evaluate_policy(layout, circle, opt_policy, "optimal")[0]
    res['Optimal_test'] = simulate_policy(layout, circle, opt_policy, "optimal", n_games)

    for dice_id in range(1, 5):
        converges = check_layout_convergeance(layout,circle, [dice_id])
        res[f'dice_{dice_id}_theoretical'] = evaluate_policy(layout, circle, dice_id, "always")[0] if converges else "DNF"
        res[f'dice_{dice_id}_test'] = simulate_policy(layout, circle, dice_id,"always", n_games) if converges else ("DNF","DNF")
    
    converges = check_layout_convergeance(layout,circle, [1,2,3,4])
    res['Uniform_random_theoretical'] = evaluate_policy(layout, circle, policy_uniform_random(), "uniform_random")[0] if converges else "DNF"
    res['Uniform_random_test'] = simulate_policy(layout, circle, policy_uniform_random(), "uniform_random", n_games) if converges else ("DNF","DNF")
    print("Start square expected turns (theory / empirical +- stderr)")
    print(f"optimal: {res['Optimal_theoretical']:.4f} / {res['Optimal_test'][0]:.4f} +- {res['Optimal_test'][1]:.4f}")
    for dice_id in (1, 2, 3, 4):
        th = res[f'dice_{dice_id}_theoretical']
        emp, se = res[f'dice_{dice_id}_test']
        if th == "DNF":
            print(f"dice {dice_id} only: DNF / DNF +- NA")
        else:
            print(f"dice {dice_id} only: {th:.4f} / {emp:.4f} +- {se:.4f}")
    emp, se = res['Uniform_random_test']
    if emp == "DNF":
        print(f"uniform random: DNF / DNF +- NA")
    else:
        print(
            f"uniform random: {res['Uniform_random_theoretical']:.4f} / {emp:.4f} +- {se:.4f}"
            )
    

    return res


testLayout = np.ones(15)
circle = False

#markovDecision(testLayout, circle)
#markovDecision([3,3,3,3,3,3,3,3,3,3,3,3,3,3,3],True)
# out = markovDecision([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],False)
# out = markovDecision([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],True)


# Random layouyts :
# trap = []
# trap.append(int(np.random.choice([0,3]))) # Not meaningful to have traps of type 1 or 2 on the first tile (so only 0 or 3)
# for i in range(1,14):
#     trap.append(np.random.randint(0,4)) # We need to make this more restrictive as for some layouts and some suboptimal policies (see example on whatsapp)
# trap.append(0) # Not meaningful to have traps on last tile as we won the game no matter what
# print("Trap layout:", trap)

#trap = [3,2,1,2,0,0,0,0,3,2,1,1,1,3,0]
#trap = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 2, 3, 1, 0]

traps = {
    "no_trap_layout": [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    "few_traps_layout": [0,0,3,0,0,0,3,0,0,0,0,3,0,0,0],
    "many_traps_layout": [0, 0, 1, 1, 3, 2, 1, 3, 2, 1, 1, 0, 1, 1, 0],
    "two_in_a_row_layout": [0, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0],
    "evil_fast_lane_layout": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 2, 3, 1, 0],
    "back_to_3_layout": [0,0,0,0,0,2,0,0,0,1,0,0,2,0,0],
}
for name, trap in traps.items():
    print(f"Testing layout: {name} with no circle")
    # out = markovDecision(trap, False)
    compare_strategies(trap, False)
    print("\n\n")
    print(f"Testing layout: {name} with circle")
    # out = markovDecision(trap, True)
    compare_strategies(trap, True)

#Example of a run :
#Trap layout: [0, 3, 1, 3, 1, 0, 3, 1, 3, 2, 3, 1, 3, 0, 0], n_games = 5000
# Start square expected turns (theory / empirical +- stderr)
# optimal: 11.6996 / 11.6866 +- 0.1085
# dice 1 only: 16.9999 / 16.9068 +- 0.0709
# dice 2 only: 27.4180 / 27.3798 +- 0.2806
# dice 3 only: 41.4978 / 40.4924 +- 0.4681
# dice 4 only: 13.3414 / 13.4720 +- 0.1587
# uniform random: 24.6999 / 24.7310 +- 0.2762

#check_layout_convergeance([3, 1, 1, 1, 3, 0, 2, 1, 0, 2, 0, 2, 2, 0, 0],False,[3])




"""
TEST LAYOUT FOR DIFFERENT SCENARIOS
no_trap_layout = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
few_traps_layout = [0,0,3,0,0,0,3,0,0,0,0,3,0,0,0]
many_traps_layout = [0, 0, 1, 1, 3, 2, 1, 3, 2, 1, 1, 0, 1, 1, 0]
two_in_a_row_layout = [0, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0]
evil_fast_lane_layout = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 2, 3, 1, 0]
back_to_3_layout = [0,0,0,0,0,2,0,0,0,1,0,0,2,0,0]
game = Game(generate_board([0,0,0,0,0,2,0,0,0,1,0,0,2,0,0],False))
game.print_board()
"""

"""
Extra strat? Like safe -> risky ? Or risky -> safe (like when you arrive close to the goal tile, you take safer dices, but I do not know if that is notalready the optimal strategy, and maybe we should use the current tile more.)

Experiments we could do :

Take no traps layout, the evil fast lane layout and maybe an other with traps just before the fast lane. We could compare if the optimal policy takes some aggressive choice of dice around square 3 or not (like to be sure to NOT go on the evil lane,...).



"""

