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
        
        

    def roll_die(self, die_id):
        self.turn_count += 1
        die_used = self.dice[die_id]
        trap_chance = die_used[1]
        die_result = die_used[0][np.random.randint(0,len(die_used[0]))]
        print("Die_result", die_result)
        #move
        if die_result < 0:
            self.current_tile = self.current_tile.step_backwards(-die_result)
        else: 
            self.current_tile = self.current_tile.step_forward(die_result, is_start_tile_3 = (self.current_tile.tile_id == 3))

        
        #activate traps if needed
        self.current_tile = self.activate_trap(trap_chance)
        


    def activate_trap(self,trap_probabilty): #Note, there is no "cascade trigerring" (see instructions section 5)
        trap_type = self.current_tile.trap
        
        if trap_probabilty is None or trap_type == 0: #either safe dice or regular tile
            return self.current_tile
        
        if trap_probabilty > np.random.random(): #if trap activates
            print("TRAP ACTIVATED, type:",trap_type)
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
        game.roll_die(int(input("Enter die choice (1:security, 2:normal, 3:risky, 4:special)\n"))) 
        game.print_board()
        print()
        
    print("You won the game in",game.turn_count,"turns!")
    #TODO change to (Expec, Dice)
    return game.turn_count



def markovDecision(layout, circle):
    game = Game(generate_board(layout, circle))
    V = np.ones(BOARD_SIZE)
    policy = np.ones(BOARD_SIZE, dtype=int)
    stability_tol = 0.0001
    unstable = True
    V[-1] = 0  ## situation where player lands on final square

    def expected_value(landed_tile, trap_chance):
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

    while unstable:
        newV = np.copy(V)

        for tile in game.tiles:
            tile_idx = tile.tile_id - 1

            if tile.tile_id == BOARD_SIZE:
                newV[tile_idx] = 0
                continue

            currMin = np.inf
            currMinDice = 1

            for i in range(1, 5):  # each dice
                startTile = tile
                endTile = tile
                currSum = 0

                die_rolls = game.dice[i][0]
                trap_chance = game.dice[i][1]

                for roll in die_rolls:  # each possible roll
                    if startTile.tile_id == 3 and roll > 0:
                        next_tile_fast = startTile.step(roll, True, 1)
                        next_tile_slow = startTile.step(roll, True, 0)

                        currSum += 0.5 * expected_value(next_tile_fast, trap_chance)
                        currSum += 0.5 * expected_value(next_tile_slow, trap_chance)
                    else:
                        next_tile = startTile.step(roll)
                        currSum += expected_value(next_tile, trap_chance)
                expectedCost = 1 + (currSum * 1.0 / len(die_rolls))

                if expectedCost < currMin:
                    currMin = expectedCost
                    currMinDice = i

            newV[tile_idx] = currMin
            policy[tile_idx] = currMinDice

            if abs(newV[tile_idx] - V[tile_idx]) < stability_tol:
                unstable = False

        V = np.copy(newV)

    print(V)
    print(policy)
    return V, policy


testLayout = np.ones(15)
circle = False

#markovDecision(testLayout, circle)



#markovDecision([3,3,3,3,3,3,3,3,3,3,3,3,3,3,3],True)
markovDecision([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],False)
markovDecision([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],True)