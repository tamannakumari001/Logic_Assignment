"""
sudoku_solver.py

Implement the function `solve_sudoku(grid: List[List[int]]) -> List[List[int]]` using a SAT solver from PySAT.
"""

from pysat.formula import CNF
from pysat.solvers import Solver
from typing import List

def solve_sudoku(grid: List[List[int]]) -> List[List[int]]:
    """Solves a Sudoku puzzle using a SAT solver. Input is a 2D grid with 0s for blanks."""

    # TODO: implement encoding and solving using PySAT
    cnf = CNF()

    # Encoding all given numbers
    for i in range(9):
        for j in range(9):
            if (grid[i][j] != 0 ):
                box_no = i*9 + j
                cnf.append([box_no*9+grid[i][j]])


    # Encoding rows, columns and 3x3 grid condition
    for num in range(9):
        cell = 0
        for i in range(9):
            row_encode = []
            col_encode = []
            box_encode = []

            if(i%3==0):
                cell = 9*i+1
            else:
                cell = cell - 17

            for j in range(9):
                row_encode.append((9*i+j)*9+num+1)
                col_encode.append((i+9*j)*9+num+1)

                box_encode.append((cell-1)*9+num+1)

                if j==8:
                    continue
                if((j+1)%3==0):
                    cell += 7
                else:
                    cell += 1

            cnf.append(row_encode)
            cnf.append(col_encode)
            cnf.append(box_encode)

 
    # Encoding blocking two numbers in same block
    for i in range(81):
        for j in range(9):
            for k in range(j+1,9):
                cnf.append([-(i*9+j+1), -(i*9+k+1)])        

   
    model = None
    with Solver(name='glucose3') as solver:
        solver.append_formula(cnf.clauses)
        if solver.solve():
            model = solver.get_model()
            for i in range(81):
                for j in range(9):
                    if model[i*9+j] > 0:
                        row = i//9
                        column = i - row*9
                        grid[row][column] = j+1
            return grid
        else:
            return [[]]

    return [[]]