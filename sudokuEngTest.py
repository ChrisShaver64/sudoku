# Sudoku Engine Tester
# Written by Chris Shaver
# Created August 24, 2015 - August 30, 2015
# Uses Python3
#
# Copyright 2015 by Christopher J. Shaver
# Licensed under GNU General Public License v3: http://www.gnu.org/licenses/gpl.html
#

from sudoku import *
import math
import copy

def process_sudoku_dat( fin ):
    """Read and process each line of fin file object.
    File format:  Blanks lines ('/n') are skipped, as are line starting
    with '#' (comment lines).  First non-skipped, non-comment line is the
    first line of the puzzle, one character per cell.  Size of puzzle is
    determined by the number of characters in the first line and must be a
    square number - all other lines of this puzzle must have the same
    number of characters/cells.  Empty cells are denoted by '-', '_', ' ',
    or '0'.  After the puzzle comes the answer for that puzzle.  All cells
    of both puzzle and answer are checked for legal values.  After the answer
    is read in, use the Sudoku engine in sudoku.py to solve the puzzle and
    compare the computed solution to the supplied answer."""
    puzzle = None
    answer = None
    puzzles_solved = 0
    f_line_count = 0 # Line count of the file being processed
    for line in fin:
        f_line_count += 1
        # Skip blanks lines (newline only) and lines that start with '#' (comments)
        if line[0:1] != '\n' and line[0:1] != '#':
            line = line.rstrip('\n')
            if puzzle is None: # Time to start reading a new puzzle
                if is_square(len(line)):
                    max_val = len(line)
                    box_size = int(math.sqrt(len(line)))
                    puzzle = Sudoku(box_size)
                    p_line_count = 1 # Count of the puzzle line being processed
                    if not fill_puzzle( puzzle, line, p_line_count, f_line_count ):
                        break
                else:
                    print('Line',f_line_count,': Starting new puzzle, # of cell values not a square #')
                    break
            elif p_line_count < max_val: # Continue filling in puzzle
                if len(line) == max_val:
                    p_line_count += 1
                    if not fill_puzzle( puzzle, line, p_line_count, f_line_count ):
                        break
                else:
                    print('Line',f_line_count,': Incorrect # of values for puzzle:',len(line),'instead of expected',max_val)
                    break
            elif answer is None: # Time to start reading the answer
                if len(line) == max_val:
                    answer = Sudoku(box_size)
                    a_line_count = 1 # Count of the answer line being processed
                    if not fill_puzzle( answer, line, a_line_count, f_line_count ):
                        break
                else:
                    print('Line',f_line_count,': Incorrect # of values for answer:',len(line),'instead of expected',max_val)
            else: # Continue filling in answer, check puzzle vs. answer when full
                if len(line) == max_val:
                    a_line_count += 1
                    if not fill_puzzle( answer, line, a_line_count, f_line_count ):
                        break
                if a_line_count == max_val: # Time to solve puzzle and check answer
                    puzzle_2solve = copy.deepcopy(puzzle)
                    result = puzzle.solve()
                    if result == answer:
                        puzzles_solved += 1
                        print('Successfully solved puzzle', puzzles_solved)
                        puzzle = None
                        answer = None
                    else:
                        print('Didn\'t solve this puzzle!!!')
                        print( 'Puzzle:\n', puzzle_2solve, '\nResult:\n', result, '\nAnswer:\n', answer, sep='' )
                        break
    fin.close()

def is_square( n ):
    """Return True if n is a square of another number, False otherwise """
    return int(math.sqrt(n))**2 == n

def fill_puzzle( puzzle, line, p_line_count, f_line_count ):
    """Fill in the puzzle at line p_line_count with the values in line.
    Return True if everything succeeded, False otherwise (after printing
    out error message)"""
    col = 0
    for char in line:
        new_value = puzzle.char2value(char)
        if new_value != 0:
            if not puzzle.set_cell( new_value, p_line_count-1, col ):
                print('Line',f_line_count,'Column',col+1,': Cannot set that cell to',char)
                return False
        col += 1
    return True

if __name__ == '__main__':
    fin = open('sudoku.dat')
    process_sudoku_dat( fin )
