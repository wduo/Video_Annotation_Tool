import time
import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from cv2 import *
import json
import copy
import ctypes


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
        self.temp_list = [0, 0, 0, 0]
        self.Rectangle_list = []
        self.Point_list = []
        self.drawing = 0
        self.dragging = 0
        self.dragging_point = '00'
        self.ind = -1  # Rectangle index
        self.point_ind = -1  # Point index
        self.click_or_drag = 0  # click: 0, drag: 1. To determine draw rect or point

        self.be_selected_ind = None
        self.be_del_ind = None

        self.del_current_frame_json_struct_signal = None

    def paintEvent(self, QPaintEvent):
        # print('(paintEvent)')
        QLabel.paintEvent(self, QPaintEvent)
        painter = QPainter(self)
        painter.begin(self)
        painter.setPen(QPen(QColor(255, 0, 0), 2))

        for ii in range(self.ind + 1):
            if self.be_selected_ind is not None and self.be_selected_ind < 100 and self.be_selected_ind == ii:
                # print('(paintEvent)', self.be_selected_ind)
                painter.setPen(QPen(QColor(0, 0, 255), 3))

            # rect = QRect(self.Rectangle_list[ii][0], self.Rectangle_list[ii][1],
            #              self.Rectangle_list[ii][2] - self.Rectangle_list[ii][0],
            #              self.Rectangle_list[ii][3] - self.Rectangle_list[ii][1])
            painter.drawRect(self.Rectangle_list[ii][0], self.Rectangle_list[ii][1],
                             self.Rectangle_list[ii][2] - self.Rectangle_list[ii][0],
                             self.Rectangle_list[ii][3] - self.Rectangle_list[ii][1])

            if self.be_selected_ind is not None and self.be_selected_ind < 100 and self.be_selected_ind == ii:
                painter.setPen(QPen(QColor(255, 0, 0), 2))

        painter.setPen(QPen(QColor(0, 0, 255), 9))
        for ii in range(self.point_ind + 1):
            painter.drawPoint(self.Point_list[ii][0], self.Point_list[ii][1])

        painter.end()

    def mousePressEvent(self, e):
        print('(mousePressEvent)')
        self.drawing = 1
        if not self.dragging:
            self.ind += 1
            self.Rectangle_list.append([0, 0, 0, 0])
            self.Rectangle_list[self.ind][0] = e.x()
            self.Rectangle_list[self.ind][1] = e.y()

        self.click_or_drag = 0

    def mouseReleaseEvent(self, e):
        print('(mouseReleaseEvent)')
        self.drawing = 0

        print('click_or_drag:', self.click_or_drag)
        if self.click_or_drag == 0:
            if self.Rectangle_list:  # This if judge fixed bug that when playing and clicking occur simultaneously
                self.Point_list.append(self.Rectangle_list.pop(-1)[:2])
                self.point_ind += 1
                self.ind -= 1
                self.update()
        else:
            self.click_or_drag = 0
        print('Rectangle_list:', self.Rectangle_list)
        print('Point_list:', self.Point_list)

        if e.button() == Qt.LeftButton:
            print("Left button")
        elif e.button() == Qt.RightButton:
            print("Right button")
        elif e.button() == Qt.MidButton:
            print("Wheel")

    def mouseMoveEvent(self, e):
        # print('(mouseMoveEvent)')
        self.click_or_drag = 1
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

    def reset(self):
        self.Rectangle_list = []
        self.Point_list = []
        self.drawing = 0
        self.dragging = 0
        self.dragging_point = '00'
        self.ind = -1
        self.point_ind = -1
        self.click_or_drag = 0
        self.be_selected_ind = None
        self.be_del_ind = None

    def objcct_list_be_selected_ind(self, be_selected_ind):
        self.be_selected_ind = be_selected_ind
        print('(objcct_list_be_selected_ind)', self.be_selected_ind)

    def object_list_be_del_ind(self, be_del_ind):
        self.be_del_ind = be_del_ind
        print('(object_list_be_del_ind)', self.be_del_ind)
        self.Rectangle_list.pop(be_del_ind)
        self.ind -= 1

        if not self.Rectangle_list and self.ind == -1 and self.del_current_frame_json_struct_signal:
            self.del_current_frame_json_struct_signal.signal.emit()


class VideoBox(QMainWindow):
    STATUS_INIT = 0
    STATUS_PLAYING = 1
    STATUS_PAUSE = 2

    def __init__(self, video_url=""):
        QMainWindow.__init__(self)
        CentQWidget = QWidget()
        self.setCentralWidget(CentQWidget)

        self.video_url = video_url
        self.video_file_name = "default_video_name"
        self.status = self.STATUS_INIT  # 0: init, 1:playing, 2: pause
        self.current_frame = 0
        self.fps = 20
        self.json_url = ""
        self.json_file_name = "default_json_name"
        self.json_data = []
        self.all_frame_ids = []  # ids of frames that have objects in json_data

        # menuBar, statusBar
        self.statusBar().showMessage('Ready')

        exitAction = QAction(QIcon('exit.png'), '&Exit', self)
        exitAction.setShortcut('Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(qApp.quit)

        loadVideo = QAction(QIcon('loadVideo.png'), 'Load &Video', self)
        # loadVideo.setShortcut('Ctrl+O')
        loadVideo.setShortcut('F')
        loadVideo.setStatusTip('Load video file')
        loadVideo.triggered.connect(self.Load_video)

        loadJson = QAction(QIcon('loadJson.png'), 'Load &Json', self)
        # loadJson.setShortcut('Ctrl+J')
        loadJson.setShortcut('G')
        loadJson.setStatusTip('Load json file')
        loadJson.triggered.connect(self.Load_json)

        saveAs = QAction(QIcon('loadJson.png'), '&Save as', self)
        saveAs.setShortcut('Ctrl+S')
        saveAs.setStatusTip('Save as')
        saveAs.triggered.connect(self.Save_as)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(loadVideo)
        fileMenu.addAction(loadJson)
        # fileMenu.addAction(saveAs)
        fileMenu.addAction(exitAction)

        editMenu = menubar.addMenu('&Edit')
        editMenu.addAction(loadVideo)
        editMenu.addAction(loadJson)

        helpMenu = menubar.addMenu('&Help')
        helpMenu.addAction(loadVideo)
        helpMenu.addAction(loadJson)

        # Col 0
        self.software_guide = QLabel('''
        1. Load the video file.

        2. Load the json file with the same name as the video name.
   
        If the name are different, the json file load fails.
        If do not load the json file, the bboxes and keypoints drawn on the canvas will not be saved.

        3. Draw bboxes and keypoints, modify them, and save to the corresponding json file.

        When the current frame is switched, it is automatically saved to the json file.
        
        
        Video file name:
        No load video file, press CTRL+O to load it first!

        Json file name:
        No load json file, press CTRL+J to load it first!
        ''')

        # Col 1
        # Row 1
        # self.infoLabel = QLabel('Info:')
        self.pictureLabel = VideoLable()
        self.pictureLabel.setGeometry(0, 0, 1000, 10000)
        init_image = QPixmap("icons/video_init.png")
        self.pictureLabel.setPixmap(init_image)
        # print(self.pictureLabel.geometry().width())
        # self.textLabel = QLabel('(50, 66, 200, 320, grab)\n(50, 66, 200, 320, eat)\n(50, 66, 200, 320, wandering)\n')

        # Row 2
        self.progress_label = QLabel('Video progress: ')

        self.video_slider = QSlider()
        self.video_slider.setOrientation(Qt.Horizontal)
        self.video_slider.setMinimum(0)
        self.video_slider.setMaximum(100)
        self.video_slider.setSingleStep(10)
        self.video_slider.valueChanged.connect(self.video_slider_drag)

        self.pre_button = QPushButton('Pre', self)
        self.pre_button.setIcon(QIcon('icons/pre_frame'))
        self.pre_button.setShortcut('Z')
        self.pre_button.clicked.connect(self.pre_frame)

        self.next_button = QPushButton('Next', self)
        self.next_button.setIcon(QIcon('icons/next_frame'))
        self.next_button.setShortcut('X')
        self.next_button.clicked.connect(self.next_frame)

        self.play_button = QPushButton('Play', self)
        self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.play_button.setShortcut('SPACE')
        self.play_button.clicked.connect(self.switch_status)

        self.slower_play_button = QPushButton('Slower', self)
        self.slower_play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaSeekBackward))
        self.slower_play_button.clicked.connect(self.slower_play)

        self.faster_play_button = QPushButton('Faster', self)
        self.faster_play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaSeekForward))
        self.faster_play_button.clicked.connect(self.faster_play)

        # Col 2
        self.object_table = ObjectList()

        # self.save_button = QPushButton('Save', self)
        # # self.save_button.setIcon(self.style().standardIcon(QStyle.SP_MediaSeekForward))
        # self.save_button.clicked.connect(self.save_bbox)

        # grid = QGridLayout()
        # grid.setSpacing(20)
        #
        # # Add row 1
        # grid.addWidget(self.pictureLabel, 0, 1, 2, 6)
        # # grid.addWidget(self.infoLabel, 0, 7)
        # # grid.addWidget(self.textLabel, 1, 7)
        #
        # # Add row 3
        # grid.addWidget(self.pre_button, 2, 1)
        # grid.addWidget(self.next_button, 2, 2)
        # grid.addWidget(self.play_button, 2, 3)
        # grid.addWidget(self.slower_play_button, 2, 4)
        # grid.addWidget(self.faster_play_button, 2, 5)
        # # grid.addWidget(self.save_button, 2, 6)

        # Col 0
        left_qgroupbox_1 = QGroupBox('Software guide')
        left_qvboxlayout_1_1 = QVBoxLayout()
        # left_qvboxlayout_1_1.addWidget(self.software_guide)
        left_qgroupbox_1.setLayout(left_qvboxlayout_1_1)

        left_qgroupbox_2 = QGroupBox('Video file list')
        left_qvboxlayout_2_1 = QVBoxLayout()
        left_qvboxlayout_2_1.addWidget(self.object_table)
        left_qgroupbox_2.setLayout(left_qvboxlayout_2_1)

        left_qvboxlayout = QVBoxLayout()
        left_qvboxlayout.addWidget(left_qgroupbox_1)
        left_qvboxlayout.addWidget(left_qgroupbox_2)

        # Col 1
        # Add row 1
        qgroupbox = QGroupBox('Video playing')

        qhboxlayout_1_1_1 = QHBoxLayout()
        qhboxlayout_1_1_1.addStretch()
        qhboxlayout_1_1_1.addWidget(self.pictureLabel)
        qhboxlayout_1_1_1.addStretch()

        qvboxlayout_1_1 = QVBoxLayout()
        qvboxlayout_1_1.addStretch()
        qvboxlayout_1_1.addLayout(qhboxlayout_1_1_1)
        qvboxlayout_1_1.addStretch()

        qgroupbox.setLayout(qvboxlayout_1_1)
        qhboxlayout_1 = QHBoxLayout()
        qhboxlayout_1.addWidget(qgroupbox)

        # Add row 2
        qhboxlayout_2_1 = QHBoxLayout()
        qhboxlayout_2_1.addWidget(self.progress_label, 1)
        qhboxlayout_2_1.addWidget(self.video_slider, 9)

        qhboxlayout_2_2 = QHBoxLayout()
        qhboxlayout_2_2.addStretch(1)
        qhboxlayout_2_2.addWidget(self.pre_button, 2)
        qhboxlayout_2_2.addWidget(self.next_button, 2)
        qhboxlayout_2_2.addWidget(self.play_button, 2)
        qhboxlayout_2_2.addWidget(self.slower_play_button, 2)
        qhboxlayout_2_2.addWidget(self.faster_play_button, 2)
        qhboxlayout_2_2.addStretch(1)

        qvboxlayout_2 = QVBoxLayout()
        qvboxlayout_2.addLayout(qhboxlayout_2_1)
        qvboxlayout_2.addLayout(qhboxlayout_2_2)

        # QVBoxLayout that has row 1 and row 2
        central_qvboxlayout = QVBoxLayout()
        central_qvboxlayout.addLayout(qhboxlayout_1)
        central_qvboxlayout.addLayout(qvboxlayout_2)

        # Col 2
        right_qgroupbox_1 = QGroupBox('Video info')
        right_qvboxlayout_1_1 = QVBoxLayout()
        right_qgroupbox_1.setLayout(right_qvboxlayout_1_1)

        right_qgroupbox_2 = QGroupBox('Object list')
        right_qvboxlayout_2_1 = QVBoxLayout()
        right_qvboxlayout_2_1.addWidget(self.object_table)
        right_qgroupbox_2.setLayout(right_qvboxlayout_2_1)

        right_qvboxlayout = QVBoxLayout()
        right_qvboxlayout.addWidget(right_qgroupbox_1, 2)
        right_qvboxlayout.addWidget(right_qgroupbox_2, 8)

        # Central QWidget layout
        central_layout = QHBoxLayout()
        central_layout.addLayout(left_qvboxlayout, 3)
        central_layout.addLayout(central_qvboxlayout, 8)
        central_layout.addLayout(right_qvboxlayout, 3)

        CentQWidget.setLayout(central_layout)

        # Video Timer
        self.timer = VideoTimer()
        self.timer.timeSignal.signal[str].connect(self.show_frame)

        # Video Capture
        self.playCapture = VideoCapture()

        # Be selected signal
        self.be_selected_ind_signal = CommunicateObjectList2VideoLableA()
        self.be_selected_ind_signal.signal[int].connect(self.pictureLabel.objcct_list_be_selected_ind)

        # Be selected to highlight or del signal for update pictureLabel
        self.be_selected_highlight_or_del_signal = CommunicateObjectList2VideoLableB()
        self.be_selected_highlight_or_del_signal.signal.connect(self.pictureLabel.update)

        # Be del signal
        self.be_del_ind_signal = CommunicateObjectList2VideoLableC()
        self.be_del_ind_signal.signal[int].connect(self.pictureLabel.object_list_be_del_ind)

        # object_table sender
        self.object_table.be_selected_ind_signal = self.be_selected_ind_signal
        self.object_table.be_selected_highlight_or_del_signal = self.be_selected_highlight_or_del_signal
        self.object_table.be_del_ind_signal = self.be_del_ind_signal

        # Del current frame json struct signal
        self.del_current_frame_json_struct_signal = CommunicateVideoLable2VideoBox()
        self.del_current_frame_json_struct_signal.signal.connect(self.del_current_frame_json_struct_when_no_object)

        # pictureLabel sender
        self.pictureLabel.del_current_frame_json_struct_signal = self.del_current_frame_json_struct_signal

        p_desk = QApplication.desktop()
        screennum = p_desk.screenCount()
        screen_rect = p_desk.screenGeometry(0)
        scale_factor = .9
        self.setGeometry(screen_rect.width() * .5 - screen_rect.width() * scale_factor * .5,
                         screen_rect.height() * .5 - screen_rect.height() * scale_factor * .5,
                         screen_rect.width() * scale_factor,
                         screen_rect.height() * scale_factor)
        self.setWindowTitle(' Video Annotater')
        self.setWindowIcon(QIcon('icons/icon_0.png'))
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('icons/icon_0.png')

    def pre_frame(self):
        print('(pre_frame)')
        if self.playCapture.isOpened():
            # Save objects to json if have modify or new add before new frame show
            self._save_to_json()

            # Ready for pre frame
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

            self.show_frame()

    def next_frame(self):
        print('(next_frame)')
        if self.playCapture.isOpened():
            # Save objects to json if have modify or new add before new frame show
            self._save_to_json()

            # Ready for next frame
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

            self.show_frame()

    def switch_status(self):
        print('(switch_status)')
        if self.playCapture.isOpened():
            self.timer.set_fps(self.playCapture.get(CAP_PROP_FPS))
            self.fps = self.playCapture.get(CAP_PROP_FPS)

            if self.status is VideoBox.STATUS_INIT:
                # Save objects to json if have modify or new add before new frame show
                self._save_to_json()
                # Ready for playing
                self.timer.start()
                self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
                self.play_button.setText('Pause')
            elif self.status is VideoBox.STATUS_PLAYING:
                self.timer.stop()
                self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
                self.play_button.setText('Play')
            elif self.status is VideoBox.STATUS_PAUSE:
                # Save objects to json if have modify or new add before new frame show
                self._save_to_json()
                # Ready for playing
                self.timer.start()
                self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
                self.play_button.setText('Pause')

            self.status = (VideoBox.STATUS_PLAYING,
                           VideoBox.STATUS_PAUSE,
                           VideoBox.STATUS_PLAYING)[self.status]

    def _save_to_json(self):
        if self.json_url and self.json_data:
            # Save info of new add objects to var json_data
            new_objects_count_in_current_frame = len(self.pictureLabel.Rectangle_list)
            if new_objects_count_in_current_frame:
                def coord_transform(list_ii):
                    # list_ii: [xa, ya, xb, yb] => [x1, y1, x2, y2] satisfy x1<x2, y1<y2
                    if list_ii[0] > list_ii[2]:
                        tmep_value = list_ii[0]
                        list_ii[0] = list_ii[2]
                        list_ii[2] = tmep_value
                    if list_ii[1] > list_ii[3]:
                        tmep_value = list_ii[1]
                        list_ii[1] = list_ii[3]
                        list_ii[3] = tmep_value

                # current frame have objects from json file
                if self.current_frame in self.all_frame_ids:
                    init_objects_in_current_frame = self.json_data['frames'][
                        self.all_frame_ids.index(self.current_frame)]['objects']
                    init_objects_count_in_current_frame = len(init_objects_in_current_frame)
                    # Only modify objects that load form json file
                    if new_objects_count_in_current_frame == init_objects_count_in_current_frame:
                        bboxes_maybe_modify = self.pictureLabel.Rectangle_list
                        for ii in bboxes_maybe_modify:
                            coord_transform(ii)

                    if new_objects_count_in_current_frame != init_objects_count_in_current_frame:
                        # New add objects of frame that have objects from json file before new add
                        if new_objects_count_in_current_frame > init_objects_count_in_current_frame:
                            new_add_bboxes = self.pictureLabel.Rectangle_list[init_objects_count_in_current_frame:]
                            for ii in new_add_bboxes:
                                coord_transform(ii)
                                one_object_struct = {
                                    "id": -1,
                                    "bbox": [-1, -1, -1, -1],
                                    "keypoints": [[-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                                                  [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]],
                                    "action": -1
                                }
                                new_add_objects = one_object_struct
                                new_add_objects["bbox"] = ii
                                init_objects_in_current_frame.append(new_add_objects)
                        # Del objects from frame whose objects from json file
                        if new_objects_count_in_current_frame < init_objects_count_in_current_frame:
                            pass

                # current frame have not objects from json file
                else:
                    # print('New add objects count of new frame:', new_objects_count_in_current_frame)
                    init_frames_in_json_file = self.json_data['frames']
                    one_frame_struct = {
                        "frame_id": -1,
                        "objects": []
                    }
                    new_add_frame = one_frame_struct
                    new_add_frame["frame_id"] = self.current_frame
                    insert_index = len(self.all_frame_ids)
                    for ii in range(len(self.all_frame_ids)):
                        if self.all_frame_ids[ii] > self.current_frame:
                            insert_index = ii
                            break
                    self.all_frame_ids.insert(insert_index, self.current_frame)
                    init_frames_in_json_file.insert(insert_index, new_add_frame)

                    new_add_bboxes = self.pictureLabel.Rectangle_list
                    for ii in new_add_bboxes:
                        coord_transform(ii)
                        one_object_struct = {
                            "id": -1,
                            "bbox": [-1, -1, -1, -1],
                            "keypoints": [[-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                                          [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]],
                            "action": -1
                        }
                        new_add_objects = one_object_struct
                        new_add_objects["bbox"] = ii
                        init_frames_in_json_file[self.all_frame_ids.index(self.current_frame)]['objects'].append(
                            new_add_objects)

            # Save json_data var to json file
            self._save_to_json_file()

    def _save_to_json_file(self):
        # Save json_data var to json file
        with open(self.json_url[0], 'w') as f:
            json.dump(self.json_data, f)

    def show_frame(self):
        if self.playCapture.isOpened():
            # Frame show
            self._show_frame()
            # Show bbox from json
            self._show_object_from_json()

    def _show_frame(self):
        self.current_frame = int(self.playCapture.get(1))
        self.statusBar().showMessage('fps: %s, current_frame: %s' % (self.fps, self.current_frame))
        self.pictureLabel.reset()
        if self.object_table.objects_in_current_frame:
            self.object_table.reset_object_table()
        # self.video_slider.setSliderPosition(self.current_frame)

        success, frame = self.playCapture.read()
        if success:
            height, width = frame.shape[:2]
            if frame.ndim == 3:
                rgb = cvtColor(frame, COLOR_BGR2RGB)
            elif frame.ndim == 2:
                rgb = cvtColor(frame, COLOR_GRAY2BGR)
            temp_image = QImage(rgb.flatten(), width, height, QImage.Format_RGB888)
            temp_image = temp_image.scaled(1000, 2000, 1)
            temp_pixmap = QPixmap.fromImage(temp_image)
            self.pictureLabel.setPixmap(temp_pixmap)
        else:
            print("Read failed, no frame data!")
            success, frame = self.playCapture.read()
            if not success:
                print("Play finished.")
                self.timer.stop()
                self.status = VideoBox.STATUS_INIT
                self.current_frame = 0
                self.fps = 20
                self.playCapture.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)
                self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
                self.play_button.setText('Play')

    def _show_object_from_json(self):
        if self.json_data:
            if self.current_frame in self.all_frame_ids:
                self.statusBar().showMessage(
                    'fps: %s, current_frame: %s, loaded bboxes' % (self.fps, self.current_frame))
                objects_in_current_frame = self.json_data['frames'][
                    self.all_frame_ids.index(self.current_frame)]['objects']
                object_ids = []
                bboxes = []
                object_keypoints = []
                object_actions = []
                for ii in objects_in_current_frame:
                    object_ids.append(ii['id'])
                    bboxes.append(ii['bbox'])
                    object_keypoints.append(ii['keypoints'])
                    object_actions.append(ii['action'])
                print('Frame', self.current_frame, "bbox:", bboxes)

                # Update pictureLabel
                self.pictureLabel.Rectangle_list = bboxes
                # print(self.pictureLabel.Rectangle_list)
                self.pictureLabel.ind = len(bboxes) - 1
                # print(self.pictureLabel.ind)
                self.pictureLabel.update()

                # Update object_table
                self.object_table.objects_in_current_frame = objects_in_current_frame
                # self.object_table.object_ids = object_ids
                # self.object_table.object_actions = object_actions
                self.object_table.show_pid_action()
                pass

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

    def video_slider_drag(self):
        # print('(video_slider_drag)')
        print('video_slider.value:', self.video_slider.value())
        if self.playCapture.isOpened():
            self.playCapture.set(cv2.CAP_PROP_POS_FRAMES, self.video_slider.value())

            self.show_frame()

    def Load_video(self):
        print('(Load_video)')
        self.video_url = QFileDialog.getOpenFileName(self, "Load video dialog", os.getcwd() + '/data')
        if self.video_url[0]:
            self.video_file_name = self.video_url[0].split('/')[-1]
            print("Load video:", self.video_file_name)

            self.playCapture.open(self.video_url[0])
            self.status = VideoBox.STATUS_INIT
            self.fps = self.playCapture.get(CAP_PROP_FPS)
            self.playCapture.set(cv2.CAP_PROP_POS_FRAMES, 1133)
            # self.playCapture.set(cv2.CAP_PROP_POS_FRAMES, 4633)

            self.timer.set_fps(self.fps)
            self.timer.start()

            self.json_url = ""
            self.json_file_name = "default_json_name"
            self.json_data = []

            self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
            self.play_button.setText('Pause')
            self.video_slider.setMaximum(int(self.playCapture.get(CAP_PROP_FRAME_COUNT)) - 1)

            self.status = (VideoBox.STATUS_PLAYING,
                           VideoBox.STATUS_PAUSE,
                           VideoBox.STATUS_PLAYING)[self.status]

    def Load_json(self):
        print('(Load_json)')
        if self.playCapture.isOpened():
            self.json_url = QFileDialog.getOpenFileName(self, "Load json dialog", os.getcwd() + '/jsons')
            if self.json_url[0]:
                self.json_file_name = self.json_url[0].split('/')[-1]
                if self.json_file_name == self.video_file_name + '.json':
                    print("Load json:", self.json_file_name)

                    with open(self.json_url[0], 'r') as f:
                        self.json_data = json.load(f)
                        # print("Load json:", self.json_data['frames'])
                        for frame in self.json_data['frames']:
                            self.all_frame_ids.append(frame['frame_id'])
                        print("Frames with bboxs load from json file:", self.all_frame_ids)
                else:
                    self.statusBar().showMessage('Please load correct json file!')
        else:
            self.statusBar().showMessage('Please load video file first!')

    def Save_as(self):
        print('(Save_as)')

    def del_current_frame_json_struct_when_no_object(self):
        print('(del_current_frame_json_struct_when_no_object)')
        current_frame_ind = self.all_frame_ids.index(self.current_frame)
        self.json_data['frames'].pop(current_frame_ind)
        self.all_frame_ids.pop(current_frame_ind)


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


class CommunicateObjectList2VideoLableA(QObject):
    signal = pyqtSignal(int)


class CommunicateObjectList2VideoLableB(QObject):
    signal = pyqtSignal()


class CommunicateObjectList2VideoLableC(QObject):
    signal = pyqtSignal(int)


class CommunicateVideoLable2VideoBox(QObject):
    signal = pyqtSignal()


# ======================================================
class ObjectList(QTableWidget):
    # horizontalHeader = ["PersonID", "xmin", "ymin", "xmax", "ymax", "lable"]
    horizontalHeader = ["Person ID", "Action lable"]
    action_labels = ["0", "1", "2", "3", "4", "5"]
    action_label_names = ["Paying", "Checking", "Looking", "Standing", "Walking", "Wandering"]

    def __init__(self):
        QTableWidget.__init__(self)
        self.setRowCount(0)
        self.setColumnCount(len(ObjectList.horizontalHeader))
        self.setHorizontalHeaderLabels(ObjectList.horizontalHeader)

        self.objects_in_current_frame = []
        # self.object_ids = []
        # self.object_actions = []

        self.selected_item_value = None
        self.selected_item_row = None
        self.selected_item_col = None

        self.action_qcomboboxes = []

        self.itemSelectionChanged.connect(self.item_selection_changed)
        self.itemChanged.connect(self.change_pid_value)

        self.be_selected_ind_signal = None
        self.be_selected_highlight_or_del_signal = None
        self.be_del_ind_signal = None

    def show_pid_action(self):
        if self.objects_in_current_frame:
            # assert len(self.object_ids) == len(self.object_actions)
            self.clearContents()

            rows = len(self.objects_in_current_frame)
            self.setRowCount(rows)
            for row in range(rows):
                # Pid
                self.setItem(row, 0, QTableWidgetItem(str(self.objects_in_current_frame[row]['id'])))

                # Action label
                self.action_qcomboboxes.append('-1')
                self.action_qcomboboxes[row] = QComboBox()
                self.action_qcomboboxes[row].addItems(ObjectList.action_label_names)
                self.action_qcomboboxes[row].setCurrentIndex(
                    self.objects_in_current_frame[row]['action']
                    if str(self.objects_in_current_frame[row]['action']) in ObjectList.action_labels else -1)
                self.action_qcomboboxes[row].currentIndexChanged.connect(self.change_action_label_value)
                self.setItem(row, 1, QTableWidgetItem())
                self.setCellWidget(row, 1, self.action_qcomboboxes[row])

    def reset_object_table(self):
        self.objects_in_current_frame = []
        # self.object_ids = []
        # self.object_actions = []
        self.action_qcomboboxes = []
        self.clearContents()
        self.setRowCount(0)

    def item_selection_changed(self):
        """
        Get the position and value before be changed.
        """
        selected_item = self.selectedItems()
        # For person id column
        if selected_item and isinstance(selected_item[0], QTableWidgetItem):
            # Selected_item location
            selected_item_index = self.indexFromItem(selected_item[0])
            self.selected_item_row = selected_item_index.row()
            self.selected_item_col = selected_item_index.column()

            if self.cellWidget(self.selected_item_row, self.selected_item_col):
                selected_qcombobox = self.cellWidget(self.selected_item_row, self.selected_item_col)
                selected_item_value = selected_qcombobox.currentText()
                self.selected_item_value = int(self.action_label_names.index(selected_item_value)) \
                    if selected_item_value is not '' else selected_item_value
            else:
                self.selected_item_value = int(selected_item[0].text())
        else:
            self.selected_item_value = None
            self.selected_item_row = None
            self.selected_item_col = None

        print(self.selected_item_row, self.selected_item_col, self.selected_item_value)

        if self.be_selected_ind_signal and self.be_selected_highlight_or_del_signal:
            self.be_selected_ind_signal.signal.emit(self.selected_item_row)
            self.be_selected_highlight_or_del_signal.signal.emit()

    def change_pid_value(self):
        if self.selected_item_value is not None and self.selected_item_row is not None and \
                self.selected_item_col is not None:
            new_value = self.item(self.selected_item_row, self.selected_item_col).text()
            if new_value.isdigit() or new_value == '-1':
                new_value = int(new_value)
                if self.selected_item_value != new_value:
                    self.objects_in_current_frame[self.selected_item_row]['id'] = new_value
            else:
                self.setItem(self.selected_item_row, 0, QTableWidgetItem(str(self.selected_item_value)))

    def change_action_label_value(self):
        print('(change_action_label_value)')
        if self.selected_item_value is not None and self.selected_item_row is not None and \
                self.selected_item_col is not None and self.action_qcomboboxes:
            new_value = self.action_qcomboboxes[self.selected_item_row].currentText()
            new_value_index = int(self.action_label_names.index(new_value))
            if self.selected_item_value != new_value_index:
                self.objects_in_current_frame[self.selected_item_row]['action'] = new_value_index

    def contextMenuEvent(self, *args, **kwargs):
        item_pop_menu = QMenu(self)
        item_pop_menu.clear()

        action_del_1 = QAction('Delete', self)
        action_del_1.triggered.connect(self.del_selected_item)
        action_del_2 = QAction('Delete', self)
        action_del_2.triggered.connect(self.del_selected_item)
        action_del_3 = QAction('Delete', self)
        action_del_3.triggered.connect(self.del_selected_item)

        item_pop_menu.addAction(action_del_1)
        item_pop_menu.addAction(action_del_2)
        item_pop_menu.addAction(action_del_3)
        item_pop_menu.exec(QCursor.pos())

    def del_selected_item(self):
        # print('(del_selected_item)')
        print('Delete item:', self.selected_item_row)

        if self.selected_item_row is not None:
            if self.be_del_ind_signal and self.be_selected_highlight_or_del_signal:
                self.be_del_ind_signal.signal.emit(self.selected_item_row)
                self.be_selected_highlight_or_del_signal.signal.emit()

            self.objects_in_current_frame.pop(self.selected_item_row)
            self.removeRow(self.selected_item_row)
            self.setRowCount(len(self.objects_in_current_frame))


# ======================================================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    box = VideoBox()
    box.show()
    sys.exit(app.exec_())
