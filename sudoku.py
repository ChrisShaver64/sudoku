# Sudoku Solver
# Written by Chris Shaver
# Created August 5, 2015 - August 20, 2015
# Uses Python3, Tkinter
# Supports both text mode and GUI mode
#
# Copyright 2015 by Christopher J. Shaver
# Licensed under GNU General Public License v3: http://www.gnu.org/licenses/gpl.html
#
# Future possible improvements:
# -- Add the ability to edit (change cells) of GUI puzzle, improve usability
# -- Add a file interface, to do large-scale testing of Sudoku engine
# -- Enhance GUI to support 4x4 puzzles, and possibly larger
# -- Enhance CLI to support up to 8x8 size puzzles
# -- Python2.7 version?

import tkinter
from tkinter.constants import *
import copy

class Cell(object):
    """A single cell inside a box inside the Sudoku board.
    Attributes:
    value: the integer value of this cell (0 if not yet determined)
    possible: a list of integers that are possible values for this cell
    max_val: maximum numeric value of a cell"""
    def __init__(self, value=0, max_val=9):
        self.value = value
        self.possible = []
        self.max_val = max_val
        if value==0:
            for i in range(1, max_val+1):
                self.possible.append(i)

    def __str__(self):
        if self.value==0:
            return '_'
        if self.value<10:
            return '%.1d' % (self.value)
        if self.value<36:
            return chr(self.value + 55) # Represent 10-35 aa A-Z
        if self.value<65:
            return chr(self.value + 61) # Represent 36-64 as a-z, {, |, }
        else: return '*' # Give up for values > 64

    def set(self, value):
        self.__init__(value, self.max_val)

    def remove_from_possible(self, value):
        if value in self.possible:
            self.possible.remove(value)

class Sudoku(object):
    """A representation of the entire Soduko puzzle.
    Attributes:
    box_size: the size of this Soduko puzzle (# of interior boxes along a side)
          typical is 3, for a 3x3 puzzle
    max_val: maximum numeric value of a call (equals box_size squared)
    cells_filled: a count of the number of cells that are filled
    cell: a list of lists (2 dimensional array) of Cell objects representing
          each cell
    """
    def __init__(self, box_size=3):
        self.box_size = box_size
        self.max_val = box_size**2
        self.cells_filled = 0
        self.cell = []
        for row in range(self.max_val):
            self.cell.append([])
            for col in range(self.max_val):
                new_cell = Cell(0, self.max_val)
                self.cell[row].append(new_cell)

    def __str__(self):
        result = []
        for row in self.cell:
            for cell in row:
                result.append(str(cell)+' ')
            result.append('\n')
        return ''.join(result)

    def populate(self):
        """Needs to be expanded to handle non-numeric input for 4x4 through
        8x8 puzzle sizes"""
        for row in range(self.max_val):
            print('Enter the values in Row #', row+1, ' (_ for no value): ', sep='', end='')
            new_row = input()
            if len(new_row) != self.max_val:
                print('You didn\'t enter the correct number of values - aborting')
                return
            else:
                for col in range(self.max_val):
                    if new_row[col] != '_':
                        new_value = int(new_row[col])
                        if not self.set_cell(new_value, row, col):
                            print('Cannot set the cell at Row #',row+1,' Column #',col+1,' to ',new_value, sep='')
                print(self)
    
    def set_cell(self, value, row, col):
        """Check cell[row][col] to see if it can possibly be set to the
        supplied value. If not, return False.  If so, set it to
        that value and remove that value from the possible values in that
        row, column and box, and return True."""
        if value not in self.cell[row][col].possible:
            return False
        else:
            self.cell[row][col].set(value)
            self.cells_filled += 1
            self.remove_value_from_possibles(value, row, col)
            return True

    def remove_value_from_possibles(self, value, row, col):
        # First remove this value from the possible cell values in this row
        for c in range(self.max_val):
            self.cell[row][c].remove_from_possible(value)
        # Next remove this value from the possible cell values in this column
        for r in range(self.max_val):
            self.cell[r][col].remove_from_possible(value)
        # Finally, remove this value from the possible cell values in this box
        # First, find the upper left corner of the box containing this cell
        box_row = row // self.box_size * self.box_size
        box_col = col // self.box_size * self.box_size
        for r in range(box_row, box_row+self.box_size):
            for c in range(box_col, box_col+self.box_size):
                self.cell[r][c].remove_from_possible(value)

    def find_one_possible(self):
        """Search all cells and return the row & column of the first cell
        found which only has one possible value.  If none, return None"""
        for row in range(self.max_val):
            for col in range(self.max_val):
                if len(self.cell[row][col].possible) == 1:
                    return (row, col)
        return (None, None)

    def find_lowest_possibles(self):
        """Search all cells and return the row & column of the empty cell which
        has the lowest number of possible values"""
        low_row = -1
        low_col = -1
        low_poss = self.max_val + 1
        for row in range(self.max_val):
            for col in range(self.max_val):
                len_possible = len(self.cell[row][col].possible)
                if len_possible > 0 and len_possible < low_poss:
                    low_row = row
                    low_col = col
                    low_poss = len_possible
        return (low_row, low_col)

    def fill_in_all_knowns(self):
        """Keep searching through all cells, filling in all cells that
        only have one possible value, until there are no more. When done,
        the puzzle will either be done or there will be choices to be made
        in cells with more than one possible value."""
        row, col = self.find_one_possible()
        while(row != None):
            value = self.cell[row][col].possible[0]
            self.set_cell(value, row, col)
            row, col = self.find_one_possible()

    def reached_dead_end(self):
        """Return True if a dead end has been reached in filling out this
        puzzle, False if there are still possible moves.  A dead end is
        reached when there is at least one valueless cell that has no
        possible values to put in it."""
        for r in range(self.max_val):
            for c in range(self.max_val):
                if self.cell[r][c].value==0 and len(self.cell[r][c].possible)==0:
                    return True
        return False

    def solved(self):
        """Return True if the puzzle is solved (i.e. all cells have values),
        False if there are still empty cells."""
        for r in range(self.max_val):
            for c in range(self.max_val):
                if self.cell[r][c].value==0:
                    return False
        return True

    def solve(self):
        puzzles = []
        puzzles.append(copy.deepcopy(self))
        while(len(puzzles)):
            puzzle = puzzles.pop()
            puzzle.fill_in_all_knowns()
            if puzzle.solved():
                puzzles = []
            elif puzzle.reached_dead_end() and len(puzzles)==0:
                puzzle = None #No solution was found
            elif puzzle.reached_dead_end():
                continue
            else:
                row, col = puzzle.find_lowest_possibles()
                for value in puzzle.cell[row][col].possible:
                    forked_puzzle = copy.deepcopy(puzzle)
                    forked_puzzle.set_cell(value, row, col)
                    puzzles.append(forked_puzzle)
        return puzzle

class SudokuGui():
    """Creates and manages the GUI window for the Sudoku puzzle.
    Attributes:
    puzzle = the Sudoku puzzle itself
    gui_frame = the frame containing all the widgets that make up the GUI window
    clear_button: a Tkinter widget for the clear button
    solve_button: a Tkinter widget for the solve button
    canvas: a Tkinter canvas widget for displaying everything else
    x: x pixel coordinate for the upper left corner of the puzzle border
    y: y pixel coordinate for the upper left corner of the puzzle border
    xk: x pixel coordinate for the upper left corner of the kaypad
    yk: y pixel coordinate for the upper left corner of the keypad
    cell_pix: number of pixels for each cell in the puzzle
    cell_rtag: a list of lists (2 dimensional array) of Tkinter tags
               for each cell's rectangle (needed to change the fill color)
    cell_vtag: a list of lists (2 dimensional array) of Tkinter tags
               for each cell's displayed value
    sel_row: the row number of the selected cell (None if none is selected)
    sel_col: the column number of the selected cell (None if none is selected)
    error_message: a Tkinter item for the error message (a line of text)
    """
    def __init__(self, x=160, y=20, cell_pix=40, box_size=3):
        self.puzzle = Sudoku(box_size)
        self.gui_frame = tkinter.Frame(gui, relief=RIDGE, borderwidth=2)
        self.gui_frame.pack(fill=BOTH,expand=1)
        self.clear_button = tkinter.Button(self.gui_frame,text="Clear",command=self.clear_pressed)
        self.clear_button.pack(side=TOP)
        self.solve_button = tkinter.Button(self.gui_frame,text="Solve",command=self.solve_pressed)
        self.solve_button.pack(side=BOTTOM)
        self.canvas = tkinter.Canvas(self.gui_frame, bg='white', width=540, height=400)
        self.canvas.pack()
        self.canvas.focus_set()
        self.canvas.bind('<ButtonPress-1>', self.process_click)
        self.canvas.bind('<Key>', self.check_key)
        self.x = x
        self.y = y
        self.xk = 20
        self.yk = y + cell_pix*box_size
        self.cell_pix = cell_pix
        self.cell_rtag = []
        self.cell_vtag = []
        self.sel_row = None
        self.sel_col = None
        self.draw_puzzle_grid()
        self.draw_keypad()
        self.display_instructions()      

    def draw_puzzle_grid(self):
        """ Draw the puzzle cells, saving cell/recetangle and text/value tags for later use"""
        for row in range(self.puzzle.max_val):
            self.cell_rtag.append([])
            self.cell_vtag.append([])
            for col in range(self.puzzle.max_val):
                xcell = self.x + col*self.cell_pix
                ycell = self.y + row*self.cell_pix
                item = self.canvas.create_rectangle(xcell,ycell,xcell+self.cell_pix,ycell+self.cell_pix, width=2)
                self.cell_rtag[row].append(item)
                item = self.canvas.create_text(xcell+self.cell_pix/2,ycell+self.cell_pix/2, font=('TkTextFont',24), text=' ')
                self.cell_vtag[row].append(item)
        # Draw a wider clear rectangle around each puzzle box, for visual clarity
        box_pix = self.cell_pix*self.puzzle.box_size
        for row in range(self.puzzle.box_size):
            for col in range(self.puzzle.box_size):
                xbox = self.x + col*box_pix
                ybox = self.y + row*box_pix
                self.canvas.create_rectangle(xbox,ybox,xbox+box_pix,ybox+box_pix, width=4)

    def draw_keypad(self):
        for row in range(self.puzzle.box_size):
            for col in range(self.puzzle.box_size):
                value = row*self.puzzle.box_size + col + 1
                xcell = self.xk + col*self.cell_pix
                ycell = self.yk + row*self.cell_pix
                item = self.canvas.create_rectangle(xcell,ycell,xcell+self.cell_pix,ycell+self.cell_pix, width=2)
                text = self.canvas.create_text(xcell+self.cell_pix/2,ycell+self.cell_pix/2, font=('TkTextFont',24), text=str(value))
        box_pix = self.puzzle.box_size*self.cell_pix
        self.canvas.create_rectangle(self.xk,self.yk,self.xk+box_pix,self.yk+box_pix, width=4)

    def display_instructions(self):
        self.canvas.create_text(80,50, text='Instructions')
        self.canvas.create_text(80,80, text='Click puzzle cell then')
        self.canvas.create_text(80,100, text='type or click value.')
        self.error_message = self.canvas.create_text(80,300, text='', fill='red')

    def process_click(self, event):
        """Given canvas pixels coordinates x and y, select the corresponding
        cell if the puzzle was clicked. If the keypad was clicked, set the
        selected cell to the value clicked.  If both the puzzle and keypad were
        missed, deselect the previously selected cell."""
        self.clear_error_message()
        x = event.x
        y = event.y
        if x<self.x or x>=self.x+self.cell_pix*self.puzzle.max_val or y<self.y or y>=self.y+self.cell_pix*self.puzzle.max_val:
            # User clicked outside the puzzle image - check if keypad was clicked
            if x<self.xk or x>=self.xk+self.cell_pix*self.puzzle.box_size or y<self.yk or y>=self.yk+self.cell_pix*self.puzzle.box_size:
                # User also clicked outside the keypad
                self.deselect_cell()
            else:
                # User clicked the keypad - set selected cell to that value
                row = (y-self.yk) // self.cell_pix
                col = (x-self.xk) // self.cell_pix
                value = row*self.puzzle.box_size + col + 1
                self.process_key(str(value))
        else:
            self.deselect_cell()
            self.sel_row = (y-self.y) // self.cell_pix
            self.sel_col = (x-self.x) // self.cell_pix
            self.canvas.itemconfig(self.cell_rtag[self.sel_row][self.sel_col], fill='yellow')

    def deselect_cell(self):
        if self.sel_row != None:
            self.canvas.itemconfig(self.cell_rtag[self.sel_row][self.sel_col], fill='white')
            self.sel_row = None
            self.sel_col = None

    def check_key(self, event):
        self.clear_error_message()
        self.process_key(event.char)

    def process_key(self, char):
        """Valid keys for 3x3 puzzle are 1-9
        Will need to be expanded to support 4x4 and larger puzzles
        Clearing or changing a previously set cell is difficult, as
        when the cell was originally set that value was removed from
        the possible list for all affected cells - so it would need
        to be added back in! Implement only 'clear entire puzzle' for now."""
        if self.sel_row!=None:
            if self.puzzle.cell[self.sel_row][self.sel_col].value!=0:
                # User is trying to change a cell that already has a value
                # Disallow for now, print error message
                self.canvas.itemconfig(self.error_message, text='Cannot change cell')
            else:
                if char.isnumeric() and char!='0':
                    value = int(char)
                    if self.puzzle.set_cell(value, self.sel_row, self.sel_col):
                        self.canvas.itemconfig(self.cell_vtag[self.sel_row][self.sel_col], text=char)
                    else:
                        self.canvas.itemconfig(self.error_message, text='Cannot set cell to '+char)

    def clear_error_message(self):
        self.canvas.itemconfig(self.error_message, text='')

    def clear_pressed(self):
        self.clear_error_message()
        self.deselect_cell()
        box_size = self.puzzle.box_size
        self.puzzle = Sudoku(box_size)
        for row in range(self.puzzle.max_val):
            for col in range(self.puzzle.max_val):
                self.canvas.itemconfig(self.cell_vtag[row][col], text=' ', fill='black')

    def solve_pressed(self):
        self.clear_error_message()
        self.deselect_cell()
        puzzle_2solve = copy.deepcopy(self.puzzle)
        solution = self.puzzle.solve()
        if solution == None:
            self.canvas.itemconfig(self.error_message, text='No solution')
        else:
            for row in range(self.puzzle.max_val):
                for col in range(self.puzzle.max_val):
                    if puzzle_2solve.cell[row][col].value == 0:
                        self.canvas.itemconfig(self.cell_vtag[row][col], text=str(solution.cell[row][col].value), fill='green')


if __name__ == '__main__':
    print('This is a Sudoku puzzle solver')
    a = input('Launch GUI (y/n)? ')
    if a=='Y' or a=='y': # GUI mode
        gui = tkinter.Tk()
        gui.title('Sudoku Solver')
        sgui = SudokuGui()
        gui.mainloop()
    else: # Text mode
        puzzle = Sudoku()
        print(puzzle)
        puzzle.populate()
        solution = puzzle.solve()
        if solution == None:
            print('No solution')
        else:
            print('Puzzle has been solved!')
            print(solution)
