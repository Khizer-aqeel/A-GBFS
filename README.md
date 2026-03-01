# A-GBFS
Objective:
The goal of this project is to develop a Dynamic Pathfinding Agent capable of navigating a grid-based
environment. You must implement Informed Search Algorithms that can navigate a grid where obstacles
appear randomly while the agent is in motion, necessitating real-time path detection and re-planning.
1. Environment Specifications
The agent will operate within a grid system that must support the following features:
• Dynamic Grid Sizing: The application must allow the user to define the grid dimensions (Rows \times
Columns).
• Fixed Start & Goal: At the start of every episode (static or dynamic), the Start Node and Goal Node
must be clearly identified and known to the agent. Even if the map changes, the destination remains
fixed unless explicitly moved by the user.
• Random Map Generation: A function to generate a maze with a user-defined obstacle density (e.g.,
30% wall coverage).
• Interactive Map Editor: Users must be able to manually place or remove obstacles (walls) by clicking
on the grid.
• Constraint: The implementation must handle any valid configuration; the use of static .txt map files
is prohibited.
2. Algorithmic Implementation
Implement the following search strategies to find the path from the Start node to the Goal node:
• Greedy Best-First Search (GBFS): Uses only the heuristic evaluation f(n) = h(n).
• A* Search: Uses the combined evaluation function f(n) = g(n) + h(n), where g(n) is the path cost from
the start to node n.
• Heuristic Functions:

• GUI Selection: The interface must allow the user to toggle between these heuristics and algorithms
before starting the search.
3. Dynamic Obstacles and Re-planning
To simulate real-world navigation, implement a Dynamic Mode:
• Spawning Logic: When enabled, new obstacles should spawn on the grid with a small probability at
every time step while the agent is in transit.
• Re-planning Mechanism: If a newly spawned obstacle obstructs the current path, the agent must
detect the collision and immediately calculate a new path to the target from its current position.
• Efficiency: Re-calculation should be optimized; avoid resetting the entire search if the obstacle is not
on the current path.
4. Mandatory Visualization & Metrics
The project requires a Graphical User Interface (GUI) developed in Tkinter, Pygame, or a similar library.
Console-only outputs are not acceptable.

• Visual Elements:
o Frontier Nodes: Highlight nodes currently in the priority queue (e.g., Yellow).
o Visited Nodes: Highlight nodes that have been explored/expanded (e.g., Red or Blue).
o Final Path: Highlight the calculated optimal path (e.g., Green).
• Real-Time Metrics Dashboard:
o Nodes Visited: Total count of expanded nodes.
o Path Cost: The total length of the final path.
o Execution Time: Total time taken to compute the solution (in milliseconds).
