import sys
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (QWidget, QGridLayout,
                             QLabel, QPushButton, QLineEdit, QApplication)
from cv2 import VideoCapture


class Example(QWidget):

    def __init__(self):
        super().__init__()

        self.initUI()

        self.playCapture = VideoCapture()


    def initUI(self):
        grid = QGridLayout()
        # grid.setSpacing(10)

        # Row 1
        video_label = QLabel('video')
        video_label.setGeometry(0, 0, 900, 500)
        init_image = QPixmap("video_lable.jpg").scaled(video_label.width(), video_label.height())
        video_label.setPixmap(init_image)

        # Row 2
        pre = QPushButton('Pre', self)
        next = QPushButton('Next', self)
        save = QPushButton('Save', self)

        # Row 3
        start = QPushButton('Start', self)
        end = QPushButton('End', self)

        # Row 4
        label_action = QLabel('Action:')
        frame_start = QLineEdit(self)
        bar = QLabel('-')
        frame_end = QLineEdit(self)
        arrow = QLabel('->')
        select_action = QLabel('action')
        save_action = QPushButton('Save_action', self)

        # Add row 1
        grid.addWidget(video_label, 1, 0, 1, 7)

        # Add row 2
        grid.addWidget(pre, 2, 1)
        grid.addWidget(next, 2, 2)
        grid.addWidget(save, 2, 3)

        # Add row 3
        grid.addWidget(start, 3, 1)
        grid.addWidget(end, 3, 2)

        # Add row 4
        grid.addWidget(label_action, 4, 0)
        grid.addWidget(frame_start, 4, 1)
        grid.addWidget(bar, 4, 2)
        grid.addWidget(frame_end, 4, 3)
        grid.addWidget(arrow, 4, 4)
        grid.addWidget(select_action, 4, 5)
        grid.addWidget(save_action, 4, 6)

        self.setLayout(grid)
        self.setGeometry(200, 200, 1200, 800)
        self.setWindowTitle('video')
        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
