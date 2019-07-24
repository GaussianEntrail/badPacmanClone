# badPacmanClone
Working on some sort of poor Pac-man clone in Python 3 and Pyglet. Mostly an excuse to experiment with a "greedy" pathfinding algo.

* Maze
* Playable character with rather basic movement and collisions
* "Ghosts" that attempt to reach the Playable character's position by minimizing the distance between them and the player
* No pellets, powerups, or sound yet
* Ghosts have different speeds
* WASD keys for player movement, though you won't die or anything if the ghosts touch you yet.

a test map is being used for the game that's being loaded from a text file (test_map.txt) make sure this is in the same folder as badPac.py

To-Do:

* Procedural Maze generation
* actual gameplay
* Ghost AI differentiation/states
* collectibles
