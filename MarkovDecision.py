import numpy as np

def markovDecision(layout,circle):

    # Start with the game constants like how the dices work

    # I suggest we make a dictionnary, each dice has associated to it a tuple, which contains two informations : a list of tuples with where it may lead and its probabilities, and the trap probability.
    # Example of first dice, security dice, we may move of 0 or 1  square with both probability 0.5, and there is no trap possible so I put None.
    dices = {1: ([(0,0.5),(1,0.5)], None), 2: ([(0,1/3),(1,1/3),(2,1/3)], 0.5), 3: ([(0,1/4),(1,1/4),(2,1/4),(3,1/4)], 1), 4: ([(-3,1/4),(-1,1/4),(3,1/4),(5,1/4)], 1)}

    # Next, I would say we create what happens when there is a trap (so the three types), 
    # and wemust be careful because there are two types of games 
    # (like circle and 'start when arriving at goal') and there is a trick at position 3. 
    # If I understand correctly, the goal is to define the transitions probabilities 
    # for each state and each dice? like dice 1 : all the transitions probabilities 
    # for each state, dice 2 : all the transition probabilities for each state, etc...