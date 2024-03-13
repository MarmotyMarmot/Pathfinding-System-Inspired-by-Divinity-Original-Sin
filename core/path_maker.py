import cv2

from numpy import ndarray

from core.map import Waypoint
from core.map_loader import Area


class Node:
    """Node class containing
    parent: Node, position: tuple and children: list objects"""
    def __init__(self, parent, position: tuple, children: list):
        self.parent = parent
        self.children = children
        self.position = position

        self.g = 0  # Distance between the current node and the start node
        self.h = 0  # Distance between the current node and the end node
        self.f = 0  # g + h

    def __eq__(self, other):
        return self.position == other.position


class PathMaker:
    """Class for calculation of the most optimal path between two points on the map. Uses the A* algorithm."""
    def __init__(self, image: ndarray, waypoint_list: list[Waypoint]):
        # For conversion and visual representation
        self.__mazeImg = image
        self.__mazeImgGrey = cv2.cvtColor(self.__mazeImg, cv2.COLOR_BGR2GRAY)

        # For the algorithm
        self.__mazeArray = cv2.threshold(self.__mazeImgGrey, 128, 255, cv2.THRESH_BINARY)[1]
        self.__waypoint_list = waypoint_list

    def make_path(self):
        """Calculate the path between two points"""
        # Calculating the path using the waypoint map
        waypoint_path = self.__astar_for_waypoints(len(self.__waypoint_list) - 2, len(self.__waypoint_list) - 1)
        pixel_path = []
        for ind_w, waypoint in enumerate(waypoint_path):
            if ind_w < len(waypoint_path) - 1:
                # Calculating the path between each waypoint on the waypoint path (on pixels)
                pixel_path += self.__astar_for_pixels(waypoint, waypoint_path[ind_w + 1])
        return pixel_path, self.__mazeImg

    def __draw_point(self, pos: tuple, color: tuple):
        self.__mazeImg = cv2.circle(self.__mazeImg, pos, radius=0, color=color, thickness=-1)

    def __astar_for_waypoints(self, startPos, endPos):
        start = Node(None, self.__waypoint_list[startPos].position,
                     self.__waypoint_list[startPos].accessible_waypoints)
        end = Node(None, self.__waypoint_list[endPos].position,
                   self.__waypoint_list[endPos].accessible_waypoints)

        open_list = []  # Points with undiscovered, seemingly profitable connections
        closed_list = []  # Points with discovered and/or unprofitable connections
        open_list.append(start)

        while len(open_list) > 0:

            current_door = open_list[0]
            current_index = 0
            for index, item in enumerate(open_list):
                if item.f < current_door.f:
                    current_door = item
                    current_index = index

            open_list.pop(current_index)
            closed_list.append(current_door)

            if current_door == end:  # Found the destination
                path = []
                current = current_door
                while current is not None:
                    path.append(current.position)
                    current = current.parent
                return path[::-1]  # Finished

            if current_door.children == [None]:
                continue

            for child in current_door.children:

                pos = child.position
                if isinstance(pos, Area):
                    pos = pos.middle

                if current_door.parent and pos == current_door.parent.position:
                    continue

                child = Node(current_door, pos, child.accessible_waypoints)

                if len([closed_child for closed_child in closed_list if closed_child == child]) > 0:
                    continue

                child.g = (current_door.g + ((child.position[0] - current_door.position[0]) ** 2)
                           + ((child.position[1] - current_door.position[1]) ** 2))
                child.h = ((child.position[0] - end.position[0]) ** 2) + ((child.position[1] - end.position[1]) ** 2)
                child.f = child.g + child.h

                if len([open_node for open_node in open_list if
                        child.position == open_node.position and child.g > open_node.g]) > 0:
                    continue

                open_list.append(child)

    def __astar_for_pixels(self, startPos: tuple, endPos: tuple):
        # Convert from x, y to y, x because of the way of accessing list[y][x]
        start = Node(None, (startPos[1], startPos[0]), [])
        end = Node(None, (endPos[1], endPos[0]), [])

        open_list = []  # Points with undiscovered, seemingly profitable connections
        closed_list = []  # Points with discovered and/or unprofitable connections
        open_list.append(start)

        while len(open_list) > 0:
            current_node = open_list[0]
            current_index = 0
            for index, item in enumerate(open_list):
                if item.f < current_node.f:
                    current_node = item
                    current_index = index

            open_list.pop(current_index)
            closed_list.append(current_node)

            if current_node == end:  # Found the destination
                path = []
                current = current_node
                while current is not None:
                    self.__draw_point((current.position[1], current.position[0]), color=(0, 0, 255))
                    path.append(current.position)
                    current = current.parent
                path = path[::-1]
                return path  # Finished

            children = []
            for new_position in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                node_position = (current_node.position[0] + new_position[0], current_node.position[1] + new_position[1])
                h = len(self.__mazeArray)
                w = len(self.__mazeArray[0])

                if ((node_position[0] >= h) or (node_position[0] < 0) or
                        (node_position[1] > (w - 1)) or (node_position[1] < 0)):
                    continue

                if self.__mazeArray[node_position[0]][node_position[1]] != 255:  # 255 meaning the obstacle
                    continue

                children.append(Node(current_node, node_position, []))

            for child in children:

                if len([closed_child for closed_child in closed_list if closed_child == child]) > 0:
                    continue

                child.g = current_node.g + 1
                child.h = ((child.position[0] - end.position[0]) ** 2) + ((child.position[1] - end.position[1]) ** 2)
                child.f = child.g + child.h

                if len([open_node for open_node in open_list if
                        child.position == open_node.position and child.g > open_node.g]) > 0:
                    continue

                self.__draw_point((child.position[1], child.position[0]), color=(0, 255, 0))
                open_list.append(child)
