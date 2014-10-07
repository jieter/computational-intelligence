# Assignment 3

http://en.wikipedia.org/wiki/Ant_colony_optimization_algorithms

## Inleveren:

 - The source code of your (Part 1) program as a compressed archive, with a name of the
following format: `<group>_code_ACO.zip`
   Remember to keep your code ’clean’, use proper indentation, useful commentary, log2ical variable names etc. - you will need this code for part 2 and the grand challenge!
 - Route File for each Grading Maze `<group>_<maze>.txt` For example, “3_easy.txt”.
 - Report in PDF:
   `<group>_report.pdf`
   Containing your answers to the questions*. *Questions are numbered items. Bulleted items are task


## route syntax
You need to encode your results (i.e. routes) by the route length, starting location, and a
sequence of ‘actions’.
The header of the file, the total route length, is stored as an integer.
This value is equal to the number of actions. A `;` should follow this integer.
The starting point should be given by two integers: the x-coordinate and the y-coordinate, separated by a comma (`,`). A semicolon (`;`) should follow the y-coordinate.

There are four possible actions: step East, North, West or South. Those four actions are encoded using an integer:

 - `0` = East
 - `1` = North
 - `2` = West
 - `3` = South
Within the actions encoding, all characters other than `{0,1,2,3}` are invalid.
Again, each action should be followed by a semicolon. You can test the validity of the route file with the
visualizer.

A route syntax for part 1 could thus look like:

```
23;
0, 0;
3;3;3;0;0;0;3;3;2;2;3;1;
1;1;1;0;0;0;2;2;2;3;1;
```
