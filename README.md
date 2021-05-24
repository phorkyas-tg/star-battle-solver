# star-battle-solver

![Python Version][python-image]

A small star battle solver with a rudimentary gui.

## Manual

the solver can be used for different StarBattle grid sizes and stars per row/column/area, but it 
is only tested with a 9x9 TwoStarBattle grid. The gui provides a 9x9 TwoStarBattle grid. There 
are different buttons that can be used:

###[NEW] 

Clear the current grid.

###[SAVE] 
You can create and save levels in the editor. After selecting a single or multiple 
cells (a cell is selected if it has a blue highlight, by holding CTRL you can select/deselect 
further cells) you can assign an alphanumeric name by pressing a key on the keyboard. The 
selected cells are now representing a connected area. You need to assign 9 areas with a 
minimum size of 3. Press SAVE - the solver checks if the grid is plausible. If everything is 
correct you can save the level as a json file.

###[LOAD] 
By pressing this button you can load levels.

###[STEP] 
This button only appears after saving or loading a level! 
The solver computes the next solution step. It checks all single rows/columns/areas for 
forced solutions, after that it checks multiple rows/columns. If this does not work the solver 
trys to find doubles and triples and as a last resort it trys to break the puzzle via brute force.
Every solution will be documented in the log field.

###[SOLVE] 
This button only appears after saving or loading a level! Execute steps until the grid is solved 
or there is no solution.

[python-image]: https://badgen.net/badge/python/3.7/blue
