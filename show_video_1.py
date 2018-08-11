import time
import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from cv2 import *
import json


class VideoRectangle:
    def __init__(self, x1=0, y1=0, x2=0, y2=0):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2


base_rectangle_list = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0],
                       [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0],
                       [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0],
                       [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0],
                       [0, 0, 0, 0]]  # [[x1,y1,x2,y2], ...]


class VideoLable(QLabel, QPainter):
    def __init__(self):
        QLabel.__init__(self)
        self.setMouseTracking(True)
        self.Rectangle_list = base_rectangle_list
        self.drawing = 0
        self.dragging = 0
        self.dragging_point = '00'
        self.ind = -1
        # self.moving = 0

    def paintEvent(self, QPaintEvent):
        QLabel.paintEvent(self, QPaintEvent)
        painter = QPainter(self)
        painter.setPen(QColor(255, 0, 0))
        painter.begin(self)
        for ii in range(self.ind + 1):
            rect = QRect(self.Rectangle_list[ii][0], self.Rectangle_list[ii][1],
                         self.Rectangle_list[ii][2] - self.Rectangle_list[ii][0],
                         self.Rectangle_list[ii][3] - self.Rectangle_list[ii][1])
            painter.drawRect(rect)
        # print("(paintEvent)")
        painter.end()

    def mousePressEvent(self, e):
        print('(mousePressEvent)')
        self.drawing = 1
        if not self.dragging:
            self.ind += 1
            self.Rectangle_list[self.ind][0] = e.x()
            self.Rectangle_list[self.ind][1] = e.y()

    def mouseReleaseEvent(self, e):
        print('(mouseReleaseEvent)')
        self.drawing = 0
        # self.moving = 0
        if e.button() == Qt.LeftButton:
            print("Left button")
        elif e.button() == Qt.RightButton:
            print("Right button")
        elif e.button() == Qt.MidButton:
            print("Wheel")

    def mouseMoveEvent(self, e):
        # print('(mouseMoveEvent)')
        # self.moving = 1
        if not self.drawing:
            self.dragging = 0
            dist = 10
            for ii in range(self.ind + 1):
                if abs(e.x() - self.Rectangle_list[ii][2]) < dist and abs(e.y() - self.Rectangle_list[ii][3]) < dist:
                    self.dragging = 1
                    self.dragging_point = str(ii) + str(1)
                elif abs(e.x() - self.Rectangle_list[ii][0]) < dist and abs(e.y() - self.Rectangle_list[ii][1]) < dist:
                    self.dragging = 1
                    self.dragging_point = str(ii) + str(2)
                elif abs(e.x() - self.Rectangle_list[ii][2]) < dist and abs(e.y() - self.Rectangle_list[ii][1]) < dist:
                    self.dragging = 1
                    self.dragging_point = str(ii) + str(3)
                elif abs(e.x() - self.Rectangle_list[ii][0]) < dist and abs(e.y() - self.Rectangle_list[ii][3]) < dist:
                    self.dragging = 1
                    self.dragging_point = str(ii) + str(4)

            if not self.dragging:
                self.dragging_point = '00'
                self.setCursor(Qt.ArrowCursor)
            else:
                self.setCursor(Qt.CrossCursor)

            # print(self.dragging_point)

        if self.drawing:
            if self.dragging:
                for ii in range(self.ind + 1):
                    if self.dragging_point == str(ii) + str(1):
                        self.Rectangle_list[ii][2] = e.x()
                        self.Rectangle_list[ii][3] = e.y()
                    elif self.dragging_point == str(ii) + str(2):
                        self.Rectangle_list[ii][0] = e.x()
                        self.Rectangle_list[ii][1] = e.y()
                    elif self.dragging_point == str(ii) + str(3):
                        self.Rectangle_list[ii][2] = e.x()
                        self.Rectangle_list[ii][1] = e.y()
                    elif self.dragging_point == str(ii) + str(4):
                        self.Rectangle_list[ii][0] = e.x()
                        self.Rectangle_list[ii][3] = e.y()
            if not self.dragging:
                self.Rectangle_list[self.ind][2] = e.x()
                self.Rectangle_list[self.ind][3] = e.y()
            self.update()
        # print(self.Rectangle_list[2], self.Rectangle_list[3])


class VideoBox(QMainWindow):
    STATUS_INIT = 0
    STATUS_PLAYING = 1
    STATUS_PAUSE = 2

    def __init__(self, video_url=""):
        QMainWindow.__init__(self)
        CentQWidget = QWidget()
        self.setCentralWidget(CentQWidget)

        self.video_url = video_url
        self.status = self.STATUS_INIT  # 0: init, 1:playing, 2: pause
        self.current_frame = 0
        self.fps = 20
        self.json_url = ""
        self.json_data = []
        self.all_frame_ids = []

        # menuBar, statusBar
        self.statusBar().showMessage('Ready')

        exitAction = QAction(QIcon('exit.png'), '&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(qApp.quit)

        loadVideo = QAction(QIcon('loadVideo.png'), '&Load video', self)
        loadVideo.setShortcut('Ctrl+O')
        loadVideo.setStatusTip('Load video')
        loadVideo.triggered.connect(self.Load_video)

        loadJson = QAction(QIcon('loadJson.png'), '&Load json', self)
        loadJson.setShortcut('Ctrl+J')
        loadJson.setStatusTip('Load json')
        loadJson.triggered.connect(self.Load_json)

        saveAs = QAction(QIcon('loadJson.png'), '&Save as', self)
        saveAs.setShortcut('Ctrl+S')
        saveAs.setStatusTip('Save as')
        saveAs.triggered.connect(self.Save_as)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(loadVideo)
        fileMenu.addAction(loadJson)
        fileMenu.addAction(saveAs)
        fileMenu.addAction(exitAction)

        editMenu = menubar.addMenu('&Edit')
        editMenu.addAction(loadVideo)
        editMenu.addAction(loadJson)

        helpMenu = menubar.addMenu('&Help')
        helpMenu.addAction(loadVideo)
        helpMenu.addAction(loadJson)

        # Row 1
        self.infoLabel = QLabel('Info:')
        self.pictureLabel = VideoLable()
        self.pictureLabel.setGeometry(0, 0, 900, 550)
        init_image = QPixmap("images/video_init.png")
        self.pictureLabel.setPixmap(init_image)
        self.textLabel = QLabel('(50, 66, 200, 320, grab)\n(50, 66, 200, 320, eat)\n(50, 66, 200, 320, wandering)\n')

        # Row 2
        self.pre_button = QPushButton('Pre', self)
        self.pre_button.setIcon(QIcon('images/pre_frame'))
        self.pre_button.clicked.connect(self.pre_frame)
        self.next_button = QPushButton('Next', self)
        self.next_button.setIcon(QIcon('images/next_frame'))
        self.next_button.clicked.connect(self.next_frame)
        self.play_button = QPushButton('Play', self)
        self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.play_button.clicked.connect(self.switch_status)
        self.slower_play_button = QPushButton('Slower', self)
        self.slower_play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaSeekBackward))
        self.slower_play_button.clicked.connect(self.slower_play)
        self.faster_play_button = QPushButton('Faster', self)
        self.faster_play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaSeekForward))
        self.faster_play_button.clicked.connect(self.faster_play)

        self.save_button = QPushButton('Save', self)
        # self.save_button.setIcon(self.style().standardIcon(QStyle.SP_MediaSeekForward))
        self.save_button.clicked.connect(self.save_bbox)

        grid = QGridLayout()
        grid.setSpacing(20)

        # Add row 1
        grid.addWidget(self.pictureLabel, 0, 1, 2, 6)
        # grid.addWidget(self.infoLabel, 0, 7)
        # grid.addWidget(self.textLabel, 1, 7)

        # Add row 3
        grid.addWidget(self.pre_button, 2, 1)
        grid.addWidget(self.next_button, 2, 2)
        grid.addWidget(self.play_button, 2, 3)
        grid.addWidget(self.slower_play_button, 2, 4)
        grid.addWidget(self.faster_play_button, 2, 5)
        grid.addWidget(self.save_button, 2, 6)

        CentQWidget.setLayout(grid)

        # Video Timer
        self.timer = VideoTimer()
        self.timer.timeSignal.signal[str].connect(self.show_frame)

        # Video Capture
        self.playCapture = VideoCapture()

        # Paint json bbox Signal
        # self.paintJson = Communicate()
        # self.paintJson.signal[str].connect(self.pictureLabel.paintEvent)

        self.setGeometry(500, 100, 1000, 800)
        self.setWindowTitle(' Video Annotater')
        self.setWindowIcon(QIcon('images/icon_0.png'))

    def pre_frame(self):
        print('(pre_frame)')
        if self.playCapture.isOpened():
            self.timer.set_fps(self.playCapture.get(CAP_PROP_FPS))
            self.fps = self.playCapture.get(CAP_PROP_FPS)
            if self.status is VideoBox.STATUS_PLAYING:
                self.timer.stop()
                self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
                self.play_button.setText('Play')
                self.status = (VideoBox.STATUS_PLAYING,
                               VideoBox.STATUS_PAUSE,
                               VideoBox.STATUS_PLAYING)[self.status]
            self.current_frame -= 1
            if self.current_frame < 0:
                self.current_frame = 0
            self.playCapture.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)
            # print('pre_frame, current_frame: %s' % self.current_frame)
            # self.statusBar().showMessage('pre_frame, current_frame: %s' % self.current_frame)
            self.show_frame()

    def next_frame(self):
        print('(next_frame)')
        if self.playCapture.isOpened():
            self.timer.set_fps(self.playCapture.get(CAP_PROP_FPS))
            self.fps = self.playCapture.get(CAP_PROP_FPS)
            if self.status is VideoBox.STATUS_PLAYING:
                self.timer.stop()
                self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
                self.play_button.setText('Play')
                self.status = (VideoBox.STATUS_PLAYING,
                               VideoBox.STATUS_PAUSE,
                               VideoBox.STATUS_PLAYING)[self.status]
            self.current_frame += 1
            self.playCapture.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)
            # print('next_frame, current_frame: %s' % self.current_frame)
            # self.statusBar().showMessage('next_frame, current_frame: %s' % self.current_frame)
            self.show_frame()

    def switch_status(self):
        print('(switch_status)')
        if self.playCapture.isOpened():
            self.timer.set_fps(self.playCapture.get(CAP_PROP_FPS))
            self.fps = self.playCapture.get(CAP_PROP_FPS)
            if self.status is VideoBox.STATUS_INIT:
                # self.playCapture.open(self.video_url)
                self.timer.start()
                self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
                self.play_button.setText('Pause')
            elif self.status is VideoBox.STATUS_PLAYING:
                self.timer.stop()
                self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
                self.play_button.setText('Play')
            elif self.status is VideoBox.STATUS_PAUSE:
                self.timer.start()
                self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
                self.play_button.setText('Pause')

            self.status = (VideoBox.STATUS_PLAYING,
                           VideoBox.STATUS_PAUSE,
                           VideoBox.STATUS_PLAYING)[self.status]

    def show_frame(self):
        if self.playCapture.isOpened():
            self.current_frame = int(self.playCapture.get(1))
            self.statusBar().showMessage('fps: %s, current_frame: %s' % (self.fps, self.current_frame))
            self.pictureLabel.Rectangle_list = base_rectangle_list
            self.pictureLabel.ind = -1
            success, frame = self.playCapture.read()
            if success:
                height, width = frame.shape[:2]
                if frame.ndim == 3:
                    rgb = cvtColor(frame, COLOR_BGR2RGB)
                elif frame.ndim == 2:
                    rgb = cvtColor(frame, COLOR_GRAY2BGR)
                temp_image = QImage(rgb.flatten(), width, height, QImage.Format_RGB888)
                temp_image = temp_image.scaled(950, 750, 1)
                temp_pixmap = QPixmap.fromImage(temp_image)
                self.pictureLabel.setPixmap(temp_pixmap)
            else:
                print("read failed, no frame data")
                success, frame = self.playCapture.read()
                if not success:
                    print("play finished")
                    self.reset()
                    self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaStop))
                return
        else:
            print("open file or capturing device error, init again")
            self.reset()

        if self.json_data:
            if self.current_frame in self.all_frame_ids:
                self.statusBar().showMessage('fps: %s, current_frame: %s, load bbox' % (self.fps, self.current_frame))
                all_objects = self.json_data['frames'][self.all_frame_ids.index(self.current_frame)]['objects']
                bboxes = []
                for ii in all_objects:
                    bboxes.append(ii['bbox'])
                print('Frame', self.current_frame, "bbox:", bboxes)

                self.pictureLabel.Rectangle_list = bboxes
                # print(self.pictureLabel.Rectangle_list)
                self.pictureLabel.ind = len(bboxes) - 1
                # print(self.pictureLabel.ind)
                self.pictureLabel.update()

    def reset(self):
        self.timer.stop()
        self.playCapture.release()
        self.status = VideoBox.STATUS_INIT
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

    def slower_play(self):
        print('(slower_play)')
        if self.playCapture.isOpened():
            self.fps *= .5
            self.timer.set_fps(self.fps)

    def faster_play(self):
        print('(faster_play)')
        if self.playCapture.isOpened():
            self.fps *= 2
            self.timer.set_fps(self.fps)

    def save_bbox(self):
        print('(save_bbox)')

    def Load_video(self):
        print('(Load_video)')
        self.video_url = QFileDialog.getOpenFileName(self, "Load video dialog", os.getcwd() + '/data')
        print("Load video:", self.video_url[0].split('/')[-1])
        if self.video_url[0]:
            self.playCapture.open(self.video_url[0])
            self.fps = self.playCapture.get(CAP_PROP_FPS)
            self.timer.set_fps(self.fps)
            self.playCapture.set(cv2.CAP_PROP_POS_FRAMES, 1133)
            self.timer.start()
            self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
            self.play_button.setText('Pause')
            self.status = (VideoBox.STATUS_PLAYING,
                           VideoBox.STATUS_PAUSE,
                           VideoBox.STATUS_PLAYING)[self.status]

    def Load_json(self):
        print('(Load_json)')
        if self.playCapture.isOpened():
            self.json_url = QFileDialog.getOpenFileName(self, "Load json dialog", os.getcwd() + '/jsons')
            if self.json_url[0]:
                with open(self.json_url[0], 'r') as f:
                    self.json_data = json.load(f)
                    # print("Load json:", self.json_data['frames'])
                    for frame in self.json_data['frames']:
                        self.all_frame_ids.append(frame['frame_id'])
                    print("Frames with bboxs load from json file:", self.all_frame_ids)
        else:
            self.statusBar().showMessage('Load video first!')

    def Save_as(self):
        print('(Save_as)')


class Communicate(QObject):
    signal = pyqtSignal(str)


class VideoTimer(QThread):

    def __init__(self, frequent=20):
        QThread.__init__(self)
        self.stopped = False
        self.frequent = frequent
        self.timeSignal = Communicate()
        self.mutex = QMutex()

    def run(self):
        with QMutexLocker(self.mutex):
            self.stopped = False
        while True:
            if self.stopped:
                return
            self.timeSignal.signal.emit("1")
            time.sleep(1 / self.frequent)

    def stop(self):
        with QMutexLocker(self.mutex):
            self.stopped = True

    def is_stopped(self):
        with QMutexLocker(self.mutex):
            return self.stopped

    def set_fps(self, fps):
        self.frequent = fps


if __name__ == "__main__":
    app = QApplication(sys.argv)
    box = VideoBox()
    box.show()
    sys.exit(app.exec_())
