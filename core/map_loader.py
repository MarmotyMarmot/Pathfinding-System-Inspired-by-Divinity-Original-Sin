import cv2

from copy import copy

from core.map import Map, Waypoint


class Area:
    """Class representing a rectangular area with connections to other areas"""
    def __init__(self, left_upper_corner: tuple, right_bottom_corner: tuple, connections: list):
        self.left_upper_corner = left_upper_corner
        self.right_bottom_corner = right_bottom_corner
        self.connections = connections
        self.middle: tuple = self.__calculate_middle()

    def __calculate_middle(self):
        x_mid = int((self.right_bottom_corner[0] + self.left_upper_corner[0]) / 2)
        y_mid = int((self.right_bottom_corner[1] + self.left_upper_corner[1]) / 2)
        return x_mid, y_mid


class Room:
    """Class representing a room which has a certain area and doors"""
    def __init__(self, area):
        self.area = area
        self.doors = []

    def add_door(self, door):
        self.doors.append(door)

    def get_doors(self):
        return self.doors


class MapLoader:
    """Class for loading the map out of the given image"""
    def __init__(self, img_path: str, door_colour: tuple = (0, 255, 0), obstacle_colour: tuple = (255, 0, 0)):
        """Class for loading map from image path and creating Map object"""
        self.__image = cv2.imread(img_path)
        self.__obstacle_colour = obstacle_colour

        self.__door_positions = self.__detect_areas(door_colour)
        self.__rooms = []
        self.__room_positions = self.__detect_areas((255, 255, 255), True)

        self.__create_rooms()
        self.__assign_doors_to_rooms()

    def __prepare_image(self):
        """Change obstacle colour to black, so it will be treated the same as a wall"""
        obstacle_pixels = cv2.inRange(self.__image, self.__obstacle_colour, self.__obstacle_colour)
        self.__image[obstacle_pixels > 0] = (0, 0, 0)
        return self.__image

    def __detect_areas(self, colour: tuple, room: bool = False, door_colour: tuple = (0, 255, 0)):
        """Detect square areas based on the borders of certain colour"""
        image_for_detection = copy(self.__image)
        obstacle_pixels = cv2.inRange(self.__image, self.__obstacle_colour, self.__obstacle_colour)
        image_for_detection[obstacle_pixels > 0] = (255, 255, 255)

        door_pixels = cv2.inRange(image_for_detection, door_colour, door_colour)
        if room:
            image_for_detection[door_pixels > 0] = (0, 0, 0)

        colour_pixels = cv2.inRange(image_for_detection, colour, colour)
        ret, green_threshold = cv2.threshold(colour_pixels, 0, 255, 0)
        contours, im2 = cv2.findContours(green_threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        area_list = []
        for contour in contours:
            x_min = contour[0][0][0]
            y_min = contour[0][0][1]
            x_max = contour[2][0][0]
            y_max = contour[2][0][1]
            if room:
                area = Area((x_min - 1, y_min - 1), (x_max + 1, y_max + 1), [])
            else:
                area = Area((x_min, y_min), (x_max, y_max), [])

            area_width = x_max - x_min
            area_height = y_max - y_min

            if room:
                # in the used map, objects have border thicker than 3 pixels,
                # and there were  detections of rooms with too small thickness
                if not (area_width < 7) and not (area_height < 7) and (
                        area_width < image_for_detection.shape[0] - 1) and (
                        area_height < image_for_detection.shape[1] - 1):
                    area_list.append(area)
            else:  # case of door, doors have 3 pixels in width/height
                area_list.append(area)

        return area_list

    def __create_rooms(self):
        """Create list of Room objects"""
        for room_area in self.__room_positions:
            self.__rooms.append(Room(room_area))

    def __assign_doors_to_rooms(self):
        """Calculate doors lying on the borders of rooms and assign them"""
        for room_pos in self.__room_positions:
            self.__rooms.append(Room(room_pos))

        for room in self.__rooms:
            for door in self.__door_positions:

                if room.area.left_upper_corner[0] == door.right_bottom_corner[0]:
                    if (door.right_bottom_corner[1] > room.area.left_upper_corner[1]) and (
                            door.left_upper_corner[1] < room.area.right_bottom_corner[1]):
                        room.add_door(door)

                elif room.area.left_upper_corner[1] == door.right_bottom_corner[1]:
                    if (door.right_bottom_corner > room.area.left_upper_corner) and (
                            door.left_upper_corner[0] < room.area.right_bottom_corner[0]):
                        room.add_door(door)

                elif room.area.right_bottom_corner[0] == door.left_upper_corner[0]:
                    if (door.right_bottom_corner[1] > room.area.left_upper_corner[1]) and (
                            door.left_upper_corner[1] < room.area.right_bottom_corner[1]):
                        room.add_door(door)

                elif room.area.right_bottom_corner[1] == door.left_upper_corner[1]:
                    if (door.right_bottom_corner > room.area.left_upper_corner) and (
                            door.left_upper_corner[0] < room.area.right_bottom_corner[0]):
                        room.add_door(door)

    def get_map(self):
        """Create full list of waypoints and return Map object"""
        waypoints = []
        for room in self.__rooms:
            accessible_area = tuple((room.area.left_upper_corner, room.area.right_bottom_corner))
            for door in room.doors:
                door_position = door.middle

                if len(waypoints) == 0:
                    waypoints.append(Waypoint([], [accessible_area], door))

                new_waypoint = True
                for waypoint in waypoints:
                    if door_position == waypoint.position:
                        new_waypoint = False
                        if accessible_area not in waypoint.accessible_areas:
                            waypoint.accessible_areas.append(accessible_area)

                if new_waypoint:
                    waypoints.append(Waypoint([], [accessible_area], door_position))

        # Adding accessible waypoints to waypoints (creating connections)
        for ind_current_waypoint, current_waypoint in enumerate(waypoints):
            areas = current_waypoint.accessible_areas
            for area in areas:
                for ind_other_waypoint, other_waypoint in enumerate(waypoints):
                    # The waypoint is different but has access to the same area
                    if (not (ind_current_waypoint == ind_other_waypoint) and
                            (area in other_waypoint.accessible_areas) and
                            (other_waypoint not in current_waypoint.accessible_waypoints)):
                        current_waypoint.accessible_waypoints.append(other_waypoint)

        return Map(self.__prepare_image(), waypoints)
