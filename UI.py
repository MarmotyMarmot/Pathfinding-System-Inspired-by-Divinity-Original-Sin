import time

from numpy import ndarray
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLabel, QPushButton, QFileDialog
from PyQt6.QtGui import QPixmap, QImage, QMouseEvent

from core.path_maker import PathMaker
from core.map_loader import MapLoader


class MapImage(QLabel):
    """QLabel containing the image, used to easily determine the mouse click position in relation to the image"""
    def __init__(self):
        super().__init__()
        self.__img_path = ''
        self.set_pixmap_from_path(self.__img_path)

        self.__click_count = 0
        self.__start_point = None
        self.__end_point = None

    def set_pixmap_from_path(self, img_path):
        """Setting the pixmap from the given path"""
        if img_path != '':
            self.__img_path = img_path
            map_pixmap = QPixmap(img_path)
            self.setPixmap(map_pixmap)

    def clear(self):
        """Returning to the original image"""
        self.set_pixmap_from_path(self.__img_path)
        self.__click_count = 0

    def mousePressEvent(self, click_event: QMouseEvent):
        """Counting to two clicks in the event area and calculating the path, overriding the default mousePressEvent"""
        if self.__click_count == 0:
            self.__start_point = click_event.pos()
            self.__click_count += 1

        elif self.__click_count == 1:
            self.__end_point = click_event.pos()
            self.__click_count += 1

            start_point = (self.__start_point.x(), self.__start_point.y())
            end_point = (self.__end_point.x(), self.__end_point.y())

            loader = MapLoader(self.__img_path)  # Load the map
            map_from_image = loader.get_map()  # Get the waypoint/door map

            # Add the points and confirm that they're in the "blank" space
            start_confirmation = map_from_image.locate_and_add_point(start_point)
            end_confirmation = map_from_image.locate_and_add_point(end_point)

            if start_confirmation and end_confirmation:
                door_waypoints = map_from_image.get_waypoints()  # Get the door map with start and end points
                map_img = map_from_image.get_image()  # Get the preprocessed image

                maker = PathMaker(map_img, door_waypoints)
                pixel_path, image = maker.make_path()  # Calculate the path based on the waypoints and the image
                pixmap = q_pixmap_from_cv_img(image)
                self.setPixmap(pixmap)
            else:
                self.__click_count = 0


class MapInterface(QDialog):
    """Window containing QLabel which displays a map, a clear button and a choose map button"""
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PathFinding UI")
        self.__layout_setup()
        self.show()

    def __layout_setup(self):
        """Setting up the layout"""
        box_layout = QVBoxLayout()
        form_layout = QFormLayout()

        self.__map_label = MapImage()
        clear_button = QPushButton("Clear")
        choose_button = QPushButton("Choose the map")

        clear_button.clicked.connect(self.__map_label.clear)
        choose_button.clicked.connect(self.__choose_image)

        form_layout.addRow(self.__map_label)
        form_layout.addRow(clear_button)
        form_layout.addRow(choose_button)
        box_layout.addLayout(form_layout)
        self.setLayout(box_layout)

    def __choose_image(self):
        """Choosing the image from the pc memory"""
        self.__map_label.clear()
        file_name = QFileDialog.getOpenFileName(
            self,
            "Open File",
            "${HOME}",
            "Image Files (*.png *.jpg *.bmp)",
        )
        self.__map_label.set_pixmap_from_path(file_name[0])


def q_pixmap_from_cv_img(cv_img: ndarray) -> QPixmap:
    """Convert numpy.ndarray to QPixmap
    :arg cv_img: cv2 image (numpy.ndarray) in BGR format
    :returns: PyQt6 QPixmap"""
    height, width, channel = cv_img.shape
    bytes_per_line = 3 * width
    q_image = QImage(cv_img.data, width, height, bytes_per_line, QImage.Format.Format_BGR888)
    return QPixmap.fromImage(q_image)
