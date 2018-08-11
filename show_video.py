import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from cv2 import *


class VideoLable(QLabel, QPainter):
    def __init__(self):
        QLabel.__init__(self)
        self.Rectangle_list = [0, 0, 0, 0]  # x1,y1,x2,y2
        self.dragging = 0
        self.exist_rects = 0
        self.coord_range = 5

    def paintEvent(self, QPaintEvent):
        QLabel.paintEvent(self, QPaintEvent)
        painter = QPainter(self)
        painter.setPen(QColor(255, 0, 0))
        painter.begin(self)
        painter.drawRect(self.Rectangle_list[0], self.Rectangle_list[1],
                         self.Rectangle_list[2] - self.Rectangle_list[0],
                         self.Rectangle_list[3] - self.Rectangle_list[1])
        print("DrawRectangle")
        painter.end()

    def mousePressEvent(self, e):
        # if e.x() == self.Rectangle_list[2] and e.y() == self.Rectangle_list[3]:
        #     self.dragging = 1  # rb
        # elif e.x() == self.Rectangle_list[0] and e.y() == self.Rectangle_list[1]:
        #     self.dragging = 2  # lt
        # elif e.x() == self.Rectangle_list[3] and e.y() == self.Rectangle_list[2]:
        #     self.dragging = 3  # rt
        # elif e.x() == self.Rectangle_list[0] and e.y() == self.Rectangle_list[3]:
        #     self.dragging = 4  # lb
        # else:
        if self.exist_rects == 0:
            self.Rectangle_list[0] = e.x()
            self.Rectangle_list[1] = e.y()
        if e.button() == Qt.RightButton:
            self.Rectangle_list = [0, 0, 0, 0]
            self.dragging = 0
            self.exist_rects = 0
            self.update()

    def mouseReleaseEvent(self, e):
        self.dragging = 0
        self.exist_rects = 1
        if e.button() == Qt.LeftButton:
            print("左键")
        elif e.button() == Qt.RightButton:
            print("右键")
        elif e.button() == Qt.MidButton:
            print("点击滚轮")

    def mouseMoveEvent(self, e):
        if self.exist_rects:
            if abs(e.x() - self.Rectangle_list[2]) < self.coord_range and \
                    abs(e.y() - self.Rectangle_list[3]) < self.coord_range:
                self.dragging = 1
            elif abs(e.x() - self.Rectangle_list[0]) < self.coord_range and \
                    abs(e.y() - self.Rectangle_list[1]) < self.coord_range:
                self.dragging = 2
            elif abs(e.x() - self.Rectangle_list[2]) < self.coord_range and \
                    abs(e.y() - self.Rectangle_list[1]) < self.coord_range:
                self.dragging = 3
            elif abs(e.x() - self.Rectangle_list[0]) < self.coord_range and \
                    abs(e.y() - self.Rectangle_list[3]) < self.coord_range:
                self.dragging = 4
            else:
                self.dragging = 0
            print(self.dragging)

        if self.dragging == 0:
            self.setCursor(Qt.ArrowCursor)
        else:
            self.setCursor(Qt.CrossCursor)

        if self.dragging == 2:
            # lt
            self.Rectangle_list[0] = e.x()
            self.Rectangle_list[1] = e.y()
        elif self.dragging == 3:
            # rt
            self.Rectangle_list[3] = e.x()
            self.Rectangle_list[2] = e.y()
        elif self.dragging == 4:
            # lb
            self.Rectangle_list[0] = e.x()
            self.Rectangle_list[3] = e.y()
        else:
            # dragging=0 & rb
            self.Rectangle_list[2] = e.x()
            self.Rectangle_list[3] = e.y()
        self.update()


class VideoBox(QWidget):
    def __init__(self, video_url=""):
        QWidget.__init__(self)
        self.video_url = video_url

        # Row 1
        self.pictureLabel = VideoLable()
        self.pictureLabel.setGeometry(0, 0, 900, 550)
        init_image = QPixmap("images/video_init.jpg").scaled(self.pictureLabel.width(),
                                                             self.pictureLabel.height())
        self.pictureLabel.setPixmap(init_image)

        # Row 2
        self.pre = QPushButton('Pre', self)
        self.pre.clicked.connect(self.pre_frame)
        self.next = QPushButton('Next', self)
        self.next.clicked.connect(self.next_frame)
        self.save_bbox = QPushButton('Save', self)
        self.save_bbox.clicked.connect(self.save_bbox_method)

        grid = QGridLayout()
        grid.setSpacing(10)

        # Add row 1
        grid.addWidget(self.pictureLabel, 1, 0, 1, 7)

        # Add row 2
        grid.addWidget(self.pre, 2, 1)
        grid.addWidget(self.next, 2, 2)
        grid.addWidget(self.save_bbox, 2, 3)

        self.setLayout(grid)

        # video 初始设置
        self.playCapture = VideoCapture()
        self.current_frame = int(self.playCapture.get(1))
        print('current_frame: %s' % self.current_frame)

        self.playCapture.open(self.video_url)

        self.setGeometry(500, 100, 1000, 800)
        self.setWindowTitle('Toggle button')

    def pre_frame(self):
        self.current_frame -= 1
        self.playCapture.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)
        print('pre_frame, current_frame: %s' % self.current_frame)
        self.show_frame()

    def next_frame(self):
        self.current_frame += 1
        self.playCapture.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)
        print('next_frame, current_frame: %s' % self.current_frame)
        self.show_frame()

    def show_frame(self):
        success, frame = self.playCapture.read()
        if success:
            height, width = frame.shape[:2]
            if frame.ndim == 3:
                rgb = cvtColor(frame, COLOR_BGR2RGB)
            elif frame.ndim == 2:
                rgb = cvtColor(frame, COLOR_GRAY2BGR)

            temp_image = QImage(rgb.flatten(), width, height, QImage.Format_RGB888)
            temp_image = temp_image.scaled(900, 700, 1)
            temp_pixmap = QPixmap.fromImage(temp_image)
            self.pictureLabel.setPixmap(temp_pixmap)

    def save_bbox_method(self):
        print('save_bbox_method')

    # def paintEvent(self, QPaintEvent):
    #     painter = QPainter(self)
    #     painter.setPen(QColor(166, 66, 250))
    #     painter.begin(self)
    #     painter.drawRect(self.Rectangle_list[0], self.Rectangle_list[1], self.Rectangle_list[2],
    #                      self.Rectangle_list[3])
    #     print("DrawRectangle")
    #     painter.end()
    #
    # def mousePressEvent(self, e):
    #     self.Rectangle_list[0] = e.x()
    #     self.Rectangle_list[1] = e.y()
    #     if e.button() == Qt.RightButton:
    #         self.Rectangle_list = [0, 0, 0, 0]
    #         self.update()
    #
    # def mouseReleaseEvent(self, e):
    #     if e.button() == Qt.LeftButton:
    #         print("左键")
    #     elif e.button() == Qt.RightButton:
    #         print("右键")
    #     elif e.button() == Qt.MidButton:
    #         print("点击滚轮")
    #
    # def mouseMoveEvent(self, e):
    #     self.Rectangle_list[2] = e.x() - self.Rectangle_list[0]
    #     self.Rectangle_list[3] = e.y() - self.Rectangle_list[1]
    #     self.update()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    box = VideoBox("images/06_20180725_171007.mp4")
    box.show()
    sys.exit(app.exec_())
