#A* Pathfinding Game

This is a simple pathfinding visualization game using the A* algorithm, built with Python and Pygame.

Features

Interactive grid where users can place obstacles.

Start and stop buttons to control pathfinding.

Visualization of the shortest path using A*.

Responsive and easy-to-use interface.

Requirements

Ensure you have Python installed. You also need to install Pygame:
'''
pip install pygame
'''
How to Run

Run the script using:
'''
python astar_game.py
'''
Controls

Left Click: Toggle obstacles on the grid.

Start Button: Begins A* pathfinding.

Stop Button: Clears the path.

Close Window: Exits the game.

Explanation

This program divides the screen into a 20x20 grid where the user can place obstacles. Pressing the start button initiates the A* search algorithm to find the shortest path from the top-left corner to the bottom-right corner, avoiding obstacles. The stop button clears the path but keeps the obstacles intact.
