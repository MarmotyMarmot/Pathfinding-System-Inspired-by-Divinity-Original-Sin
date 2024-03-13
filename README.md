# Pathfinding System Inspired by Divinity: Original Sin
This project aims to replicate the pathfinding system found in popular games such as Divinity: Original Sin, using the A* algorithm. The system is designed to find the most efficient path between two points on a map, taking into account obstacles and terrain.

## Features
- __A* Algorithm Implementation:__ The project utilizes the A* algorithm to calculate the shortest path between waypoints.
- __Dual-Stage Pathfinding:__ Unlike traditional implementations, this system employs the A* algorithm twice – first at major waypoints (such as doors), and then on pixels between each waypoint for finer granularity.
- __Map Loader:__ Includes a loader class that enables loading maps and waypoints from a single image file, making it easy to integrate custom maps.
- __Rectangular Area Limitation:__ The system assumes that areas (rooms) on the map are rectangular. While this simplifies the implementation, it's important to note this limitation.
- __User Interface:__ The project comes with a simple user interface built with PyQt6, allowing users to load maps and set start and end points for route calculation with just a few clicks.

## Usage
1. Clone the repository to your local machine.
2. Ensure you have Python installed.
3. Install the required dependencies using pip install -r requirements.txt.
4. Run the programme using python main.py.
5. Use the UI to load your map and set start and end points for pathfinding.

## UI
![UI](https://github.com/MarmotyMarmot/Pathfinding-System-Inspired-by-Divinity-Original-Sin/assets/45321229/e27ead99-e03d-4f2d-9b7e-eefbc0a6b888)


## Exemplary Map
![map](https://github.com/MarmotyMarmot/Pathfinding-System-Inspired-by-Divinity-Original-Sin/assets/45321229/c8271283-a65b-416c-bafd-eed19df321c8)


## Future Plans
The project aims to maintain its focus on Python implementation. However, contributions and experiments, such as the C++ implementation, are welcome.

## Contributing
Contributions are welcome! If you'd like to contribute to the project, please fork the repository, make your changes, and submit a pull request.

## Licence
This project is licenced under the MIT License - see the LICENSE file for details. You are free to use, modify, and distribute this project for any purpose.
