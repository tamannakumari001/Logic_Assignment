"""
sudoku_solver.py

Implement the function `solve_sudoku(grid: List[List[int]]) -> List[List[int]]` using a SAT solver from PySAT.
"""

from pysat.formula import CNF
from pysat.solvers import Solver
from typing import List

def solve_sudoku(grid: List[List[int]]) -> List[List[int]]:
    """Solves a Sudoku puzzle using a SAT solver. Input is a 2D grid with 0s for blanks."""
    cnf = CNF()
    # work on optimizations..
    # row_condition = [[0]*9 for _ in range(9)]
    # col_condition = [[0]*9 for _ in range(9)]
    # block_condition = [[0]*9 for _ in range(9)]
    for i in range(9):
        for j in range(9):
            if grid[i][j]!=0:     #giving our initital grid as input
                cnf.append([(9**2)*j + 9*i + grid[i][j]])
            for val in range(1,10):     #condition that each box only contains one digit
                for other in range(val+1,10):
                    a = (9**2)*j + 9*i + val
                    b = (9**2)*j + 9*i +other
                    cnf.append([-1*a,-1*b])
                


    #condition that each box can only contain one digit.
    # for i in range(9):
    #     for j in range (9):
    #         for val in range(1,10):
    #             for other in range(val+1,10):
    #                 a = (9**2)*j + 9*i + val
    #                 b = (9**2)*j + 9*i +other
    #                 cnf.append([-1*a,-1*b])
    
    #condition that each row must contain only one occurence of each number.
    for i in range (9):
        for val in range(1,10):
            to_append = []
            for j in range(9):
                a = (9**2)*j + 9 * i + val
                to_append.append(a)
            cnf.append(to_append)

    #condition that each column must contain only one occurence of each number
    for j in range (9):
        for val in range(1,10):
            to_append = []
            for i in range(9):
                a = (9**2)*j + 9 * i + val
                to_append.append(a)
            cnf.append(to_append)    

    #condition that each 3x3 block must contain only one occurence of each member
    for i in range(0,9,3):
        for j in range(0,9,3):
            for val in range(1,10):
                to_append = []
                for k in range(3):
                    for l in range(3):
                        to_append.append((9**2)*(j+k) + 9 * (i+l) + val)
                cnf.append(to_append)
    
    output = [[0]*9 for _ in range(9)]

    with Solver(name = 'glucose3') as solver:
        solver.append_formula(cnf.clauses)
        if solver.solve():
            model = solver.get_model()
            for literal in model:
                if literal > 0:
                    val = literal % 9
                    if val == 0: val = 9
                    row = int((literal-val)%81/9)
                    col = int((literal - 9*row - val)/81)
                    output[row][col] = val
            return output
        else : 
            return None
       




    return [[1]*9 for _ in range(9)]






    # TODO: implement encoding and solving using PySAT
