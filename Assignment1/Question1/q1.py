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

    #condition that each box can only contain one digit.
    for i in range(9):
        for j in range (9):
            for val in range(1,10):
                for other in range(val,10):
                    a = (9**2)*j + 9*i + val
                    b = (9**2)*j + 9*i +other
                    cnf.append(-a,-b)
    

    # TODO: implement encoding and solving using PySAT
