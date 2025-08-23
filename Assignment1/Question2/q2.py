"""
Sokoban Solver using SAT (Boilerplate)
--------------------------------------
Instructions:
- Implement encoding of Sokoban into CNF.
- Use PySAT to solve the CNF and extract moves.
- Ensure constraints for player movement, box pushes, and goal conditions.

Grid Encoding:
- 'P' = Player
- 'B' = Box
- 'G' = Goal
- '#' = Wall
- '.' = Empty space
"""

from pysat.formula import CNF
from pysat.solvers import Solver

import numpy as np #additional import for assistance in padding the grid to handle out of bounds condition

# Directions for movement
DIRS = {'U': (-1, 0), 'D': (1, 0), 'L': (0, -1), 'R': (0, 1)}


class SokobanEncoder:
    def __init__(self, grid, T):
        """
        Initialize encoder with grid and time limit.

        Args:
            grid (list[list[str]]): Sokoban grid.
            T (int): Max number of steps allowed.
        """
        self.grid = grid
        arr = np.array(grid)
        padded = np.pad(arr,pad_width=1, mode='constant', constant_values='#')
        self.grid = padded.tolist()

        '''
        I used padding to force an out of bounds conditon.
        Now The player will percieve the grid environment as surrounded by walls on all 4 sides.
        
        '''


        self.T = T
        self.rows = len(self.grid)  #here I changed the definition of rows from grid to self.grid so that the padded rows are taken into account.
        self.cols = len(self.grid[0]) 

        self.goals = []
        self.boxes = []
        self.player_start = None

        # TODO: Parse grid to fill self.goals, self.boxes, self.player_start
        self._parse_grid()

        self.num_boxes = len(self.boxes)
        self.cnf = CNF()

        '''
        Here I added some constants for ease of writing
        '''

        self.c1 = self.num_boxes + 1
        self.c2 = self.c1 * self.rows
        self.c3 = self.c2 * self.cols

    def _parse_grid(self):
        """Parse grid to find player, boxes, and goals."""
        # TODO: Implement parsing logic
        for row in range(len(self.grid)):
            for elem in range(len(self.grid[row])):
                if (self.grid[row][elem] == 'G'): 
                    self.goals.append([row,elem])
                elif (self.grid[row][elem] == 'B'):
                    self.boxes.append([row,elem])
                elif (self.grid[row][elem] == 'P'):
                    self.player_start = [row ,elem]
                
                



    # ---------------- Variable Encoding ----------------
    def var_player(self, x, y, t):
        """
        Variable ID for player at (x, y) at time t.
        """
        # TODO: Implement encoding scheme
        return self.num_boxes + 1  + self.c1*x + self.c2*y + self.c3 * t
  


    def var_box(self, b, x, y, t):
        """
        Variable ID for box b at (x, y) at time t.
        """
        # TODO: Implement encoding scheme
        return b  + self.c1*x + self.c2*y + self.c3 * t


    # ---------------- Encoding Logic ----------------
    def encode(self):
        """
        Build CNF constraints for Sokoban:
        - Initial state
        - Valid moves (player + box pushes)
        - Non-overlapping boxes
        - Goal condition at final timestep
        """
        # TODO: Add constraints for:
        # 1. Initial conditions
        # 2. Player movement
        # 3. Box movement (push rules)
        # 4. Non-overlap constraints
        # 5. Goal conditions
        # 6. Other conditions

        #Constraints for initial conditions:
        self.cnf.append([self.var_player(self.player_start[0], self.player_start[1],0)])
        for index in range(self.num_boxes):
            self.cnf.append([self.var_box(index+1, self.boxes[index][0], self.boxes[index][1], 0)])
        
        #condition for player movement:
        for t in range(self.T):
            for x in range(1,self.rows-1):
                for y in range(1,self.cols-1):
                    self.cnf.append([-self.var_player(x,y,t),self.var_player(x+1,y,t+1),self.var_player(x,y-1,t+1),self.var_player(x,y+1,t+1),self.var_player(x-1,y,t+1),self.var_player(x,y,t+1)])
        
        #condition that if there is a wall, player and boxes can't move through it
        for t in range(self.T + 1):
            for x in range(self.rows):
                for y in range(self.cols):
                    if self.grid[x][y] == '#':
                        self.cnf.append([-self.var_player(x,y,t)])
                        for b in range(self.num_boxes):
                            self.cnf.append([-self.var_box(b+1,x,y,t)])
            
        #condition that at a given time, a player and box can be atmost in one place
        for t in range(self.T + 1):
            atleast_one_place_player = [] #condition that at a given time player must be in atleast one place
            for x in range(self.rows):
                for y in range(self.cols):
                    atleast_one_place_player.append(self.var_player(x,y,t))
                    for xi in range(self.rows):
                        for yi in range(self.cols):
                            if (x,y) != (xi,yi):
                                self.cnf.append([-self.var_player(x,y,t), -self.var_player(xi,yi,t)])
                                for b in range(self.num_boxes):
                                    self.cnf.append([-self.var_box(b+1,x,y,t), -self.var_box(b+1,xi,yi,t)])
            self.cnf.append(atleast_one_place_player)

        #condition that at a given time, a box can atleast be in one place
        for t in range(self.T + 1):
            for b in range(self.num_boxes):
                atleast_one_place_box = []
                for x in range(self.rows):
                    for y in range(self.cols):
                        atleast_one_place_box.append(self.var_box(b+1,x,y,t))
                self.cnf.append(atleast_one_place_box)
        
        #condition that no cell can have more than one box or both a player and a box
        for t in range(self.T + 1):
            for x in range(self.rows):
                for y in range(self.cols):
                    for b1 in range(self.num_boxes):
                        self.cnf.append([-self.var_player(x,y,t), -self.var_box(b1+1,x,y,t)])
                        for b2 in range(b1 + 1, self.num_boxes):
                            self.cnf.append([-self.var_box(b1 + 1, x, y, t), -self.var_box(b2 + 1, x, y, t)])
        
        #condition about moving boxes
        for t in range(self.T):
            for b in range(self.num_boxes):
                for x in range(1,self.rows+1):
                     for y in range(1,self.cols+1):
                         self.cnf.append([-self.var_player(x,y,t),-self.var_box(b+1,x+1,y,t),self.var_box(b+1,x+1,y,t+1),self.var_box(b+1,x+2,y,t+1)])
                         self.cnf.append([-self.var_player(x,y,t),-self.var_box(b+1,x+1,y,t),self.var_box(b+1,x+1,y,t+1),self.var_player(x+1,y,t+1)])
                         self.cnf.append([-self.var_player(x,y,t),-self.var_box(b+1,x-1,y,t),self.var_box(b+1,x-1,y,t+1),self.var_box(b+1,x-2,y,t+1)])
                         self.cnf.append([-self.var_player(x,y,t),-self.var_box(b+1,x-1,y,t),self.var_box(b+1,x-1,y,t+1),self.var_player(x-1,y,t+1)])
                         self.cnf.append([-self.var_player(x,y,t),-self.var_box(b+1,x,y+1,t),self.var_box(b+1,x,y+1,t+1),self.var_box(b+1,x,y+2,t+1)])
                         self.cnf.append([-self.var_player(x,y,t),-self.var_box(b+1,x,y+1,t),self.var_box(b+1,x,y+1,t+1),self.var_player(x,y+1,t+1)])
                         self.cnf.append([-self.var_player(x,y,t),-self.var_box(b+1,x,y-1,t),self.var_box(b+1,x,y-1,t+1),self.var_box(b+1,x,y-2,t+1)])
                         self.cnf.append([-self.var_player(x,y,t),-self.var_box(b+1,x,y-1,t),self.var_box(b+1,x,y-1,t+1),self.var_player(x,y-1,t+1)])
                         self.cnf.append([-self.var_box(b+1,x,y,t) , self.var_player(x+1,y,t) , self.var_player(x-1,y,t), self.var_player(x,y-1,t) , self.var_player(x,y+1,t) , self.var_box(b+1,x,y,t+1)])
           
        #box should be at some goal at t=T
        for b in range(self.num_boxes):
            possible = []
            for goal_index in self.goals:
                possible.append(self.var_box(b+1, goal_index[0], goal_index[1],self.T))
            self.cnf.append(possible)

        return self.cnf


def decode(model, encoder):
    """
    Decode SAT model into list of moves ('U', 'D', 'L', 'R').

    Args:
        model (list[int]): Satisfying assignment from SAT solver.
        encoder (SokobanEncoder): Encoder object with grid info.

    Returns:
        list[str]: Sequence of moves.
    """

    sequence = []
    positions = []
    for literal in model :
        if literal > 0 : 
            value = literal % encoder.c1
            if value == 0:
                value = encoder.c1
            row = int(((literal - value)%encoder.c2)/encoder.c1)
            col = int(((literal - encoder.c1*row - value)%encoder.c3)/encoder.c2)
            # time = int((literal - encoder.c2*col - encoder.c1 * row - value)/encoder.c3)
            if value == encoder.num_boxes + 1:
                positions.append([row,col])
                if len(positions) > 1:
                    for key in DIRS.keys():
                        if DIRS[key] == ((positions[-1][0] - positions[-2][0]),(positions[-1][1] - positions[-2][-1])):
                            sequence.append(key)
                            break
    #print(sequence)
    return sequence



    # TODO: Map player positions at each timestep to movement directions


def solve_sokoban(grid, T):
    """
    DO NOT MODIFY THIS FUNCTION.

    Solve Sokoban using SAT encoding.

    Args:
        grid (list[list[str]]): Sokoban grid.
        T (int): Max number of steps allowed.

    Returns:
        list[str] or "unsat": Move sequence or unsatisfiable.
    """
    encoder = SokobanEncoder(grid, T)
    cnf = encoder.encode()

    with Solver(name='g3') as solver:
        solver.append_formula(cnf)
        if not solver.solve():
            return -1

        model = solver.get_model()

        if not model:
            return -1

        return decode(model, encoder)


