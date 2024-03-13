from numpy import ndarray
from typing import Self


class Waypoint:
    """Used to create map of waypoints, similar concept to the double-linked array,
    but with a list of accessible waypoints as 'pointers' with accessible areas and position as a content """

    def __init__(self, accessible_waypoints: list[Self], accessible_areas: list, position: tuple[int, int]):
        self.accessible_waypoints = accessible_waypoints  # List of waypoints accessible through the accessible areas
        self.accessible_areas = accessible_areas  # List containing areas, one or two
        self.position = position  # Waypoint position (x, y)


class Map:
    """Built with Waypoint class elements and an Image,
    enables algorithms to find the way from Waypoint A to Waypoint B"""

    def __init__(self, image: ndarray, waypoints: list[Waypoint]):
        self.__image = image
        self.__waypoints = waypoints

    def locate_and_add_point(self, point: tuple[int, int]):
        """Should be used for adding a starting or ending point of the path.
        Locate waypoint in one of the waypoints accessible areas,
        create a list of accessible waypoints for this point and add a point as a waypoint.
        """

        # Checking if the pixel value is [255, 255, 255] (white colour)
        for pixel_value in self.__image[point[1]][point[0]]:  # Numpy would return an iterable of bool objects on __eq__
            if pixel_value != 255:
                return False

        point_area = None
        point_accessible_waypoints = []
        for waypoint in self.__waypoints:
            waypoint_areas = waypoint.accessible_areas
            if len(waypoint_areas) > 1:  # In case if it's another point, not doors
                for waypoint_area in waypoint_areas:
                    if (waypoint_area[0][0] < point[0] < waypoint_area[1][0]) and (
                            waypoint_area[0][1] < point[1] < waypoint_area[1][1]):
                        point_area = waypoint_area

        if not point_area:  # The point is not in any of the available areas, thus, calculating the path is impossible
            return False

        for waypoint in self.__waypoints:
            waypoint_areas = waypoint.accessible_areas
            for waypoint_area in waypoint_areas:
                if point_area == waypoint_area:
                    point_accessible_waypoints.append(waypoint)

        new_waypoint = Waypoint(point_accessible_waypoints, [point_area], point)
        self.__waypoints.append(new_waypoint)
        for waypoint in point_accessible_waypoints:
            waypoint.accessible_waypoints.append(new_waypoint)

        return True

    def get_waypoints(self) -> list[Waypoint]:
        """Get all waypoints from this map"""
        return self.__waypoints

    def get_image(self):
        return self.__image

    def add_waypoint(self, accessible_waypoints: list, waypoint_areas: list, waypoint_position: tuple[int, int]):
        """Add a waypoint to the waypoints list"""
        waypoint = Waypoint(accessible_waypoints, waypoint_areas, waypoint_position)
        if waypoint not in self.__waypoints:
            self.__waypoints.append(waypoint)
