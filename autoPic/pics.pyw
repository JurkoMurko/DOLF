from PyQt6.QtWidgets import (QFileDialog, QApplication, QPushButton, QLabel, QProgressBar, QWidget, QLineEdit)
from PyQt6.QtGui import QPixmap, QIcon
from sys import exit, argv
from json import load
import threading
import cv2
import os
import ctypes

APP_PATH = 'C:\\Users\jurko\Projects\Video Editor\\autoPic\\' # There has to be a better way

class ExampleWidget(QWidget):
    def __init__(self):
        super().__init__()

        myappid = 'DOLF.automatic_pictures.v5' # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    
        self.time_between_pics = 1
        self.start_time = 35
        self.end_time = ''
        
        with open(APP_PATH+"defult_settings.json", "r") as f: # you shouldn't have to edit a json
            dic = load(f)
            self.inPath = dic['input']
            self.start_time = dic['start time']
            self.end_time = dic['end time']
            self.outFolderName = dic['defult picture folder name']

        self.initUI()
        
    def initUI(self):
        self.btn_in = QPushButton('In File', self)
        self.btn_in.move(20, 20)
        self.btn_in.clicked.connect(self.btn_select_input_file)
        self.la_in = QLabel(self.inPath + ' '*100, self)
        self.la_in.move(100, 22)

        qle = QLineEdit(str(self.time_between_pics), self)
        ql = QLabel('Time Between:', self)
        ql.move(20, 100)
        qle.setGeometry(110,98,40,20)
        qle.textChanged[str].connect(self.onTimeBetweenChanged)

        qle2 = QLineEdit(str(self.start_time), self)
        ql2 = QLabel('Start Time:', self)
        ql2.move(170, 100)
        qle2.setGeometry(230,98,50,20)
        qle2.textChanged[str].connect(self.onStartTimeChanged)

        self.btn_pic = QPushButton('Take Pictures', self)
        self.btn_pic.move(20, 150)
        self.btn_pic.clicked.connect(self.btn_take_pics) #(self.btn_take_pics) # lambda function could be cleaner
 
        self.qlp = QLabel('progress:', self)
        self.qlp.move(100, 150)
        self.qlp.hide()

        pixmap = QPixmap(APP_PATH+'small_frog.png')
        lbl = QLabel(self)
        lbl.setPixmap(pixmap)
        lbl.move(450,100)

        self.setGeometry(300, 300, 550, 200)
        self.setWindowTitle('Auto Pic')
        self.setWindowIcon(QIcon(APP_PATH+"Icon-Cute-Dolphin.ico"))
        self.show()
 
    def onTimeBetweenChanged(self, num):
        self.time_between_pics = num

    def onStartTimeChanged(self, num):
        if type(self.start_time) == type('') or self.start_time < 0:
            self.start_time = 0
        self.start_time = int(num)

    def btn_select_input_file(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file', self.inPath)
        
        if fname[0]:
            self.inPath = fname[0]
            self.la_in.setText(str(self.inPath))
            
        # with open(APP_PATH+"defult_settings.json", "w") as f: # you shouldn't have to edit a json
        #     dic = load(f)
        #     self.inPath = dic['input']
        #     self.start_time = dic['start time']
        #     self.end_time = dic['end time']
        #     self.outFolderName = dic['defult picture folder name']
    
    def btn_take_pics(self): # This is for the gui to stay responsive not a speed optimization
        t1 = threading.Thread(target=self.takePictures)
        t1.start()

    def takePictures(self):
        if self.inPath != None:
            # setup
            self.qlp.show()
            
            cap = cv2.VideoCapture(self.inPath)
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count/fps
            
            picFolderPath = os.path.join(os.path.dirname(self.inPath), self.outFolderName)
            os.makedirs(picFolderPath, exist_ok=True)

            if self.end_time == '' or int(self.end_time) > duration or int(self.end_time)*-1 > duration:
                self.end_time = duration
            
            if int(self.end_time) <= 0:
                self.end_time = duration + int(self.end_time)
            
            start_frame = round(fps * self.start_time)
            stop_frame = round(fps * self.end_time)
            step_frame = round(fps * self.time_between_pics)

            # main
            f_n = 0
            for n in range(start_frame, stop_frame, step_frame):
                cap.set(cv2.CAP_PROP_POS_FRAMES, n)
                ret, frame = cap.read()
                cv2.imwrite(f'{picFolderPath}/{n}.jpeg', frame)
                w = (stop_frame-start_frame) / step_frame
                
                f_n+=1
                total_frames = int((stop_frame - start_frame) / step_frame)
                
                self.qlp.setText(f'{f_n} / {total_frames}')
            self.qlp.hide()            
                
if __name__ == '__main__':
    app = QApplication(argv)
    t = ExampleWidget()
    exit(app.exec())