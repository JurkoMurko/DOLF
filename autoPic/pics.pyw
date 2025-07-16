from PyQt6.QtWidgets import (QFileDialog, QApplication, QPushButton, QLabel, QProgressBar, QWidget, QLineEdit)
from PyQt6.QtGui import QPixmap
from sys import exit, argv
from json import load
import ffmpeg
import threading
import cv2
import os

APP_PATH = 'C:\\Users\jurko\Projects\Video Editor\\autoPic\\' # There has to be a better way

class ExampleWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.time_between_pics = 1
        self.start_time = 35
        self.end_time = ''
        
        with open(APP_PATH+"defult_settings.json", "r") as f: # you shouldn't have to edit a json
            dic = load(f)
            self.inPath = dic['input']
            self.outPath = dic['output']
            self.start_time = dic['start time']
            self.end_time = dic['end time']

        self.initUI()
        
    def initUI(self):
        self.btn_in = QPushButton('In File', self)
        self.btn_in.move(20, 20)
        self.btn_in.clicked.connect(self.inFunct)
        self.la_in = QLabel(self.inPath + ' '*100, self)
        self.la_in.move(100, 22)

        self.btn_out = QPushButton('Out Folder', self)
        self.btn_out.move(20, 60)
        self.btn_out.clicked.connect(self.outFunct)
        self.la_out = QLabel(self.outPath + ' '*100, self)
        self.la_out.move(100, 62)

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

        qle3 = QLineEdit(str(self.end_time), self)
        ql3 = QLabel('End Time:', self)
        ql3.move(300, 100)
        qle3.setGeometry(360,98,60,20)
        qle3.textChanged[str].connect(self.onEndTimeChanged)

        self.btn_pic = QPushButton('Take Pictures', self)
        self.btn_pic.move(20, 150)
        self.btn_pic.clicked.connect(self.makePicThread) 
 
        self.pbar = QProgressBar(self)
        self.pbar.setGeometry(100, 150, 200, 40)
        self.pbar.hide()

        pixmap = QPixmap(APP_PATH+'small_frog.png')
        lbl = QLabel(self)
        lbl.setPixmap(pixmap)
        lbl.move(450,100)

        self.setGeometry(300, 300, 550, 200)
        self.setWindowTitle('Auto Pic')
        self.show()

    def onTimeBetweenChanged(self, num):
        self.time_between_pics = num

    def onStartTimeChanged(self, num):
        if self.start_time == '' or self.start_time < 0:
            self.start_time = 0
        self.start_time = num

    def onEndTimeChanged(self, num):
        self.end_time = num

    def inFunct(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file', self.inPath)

        if fname[0]:
            self.inPath = fname[0]
            self.la_in.setText(str(self.inPath))

    def outFunct(self):
        fname = QFileDialog.getExistingDirectory(self, 'Select Folder', self.outPath)

        if fname:
            self.outPath = fname
            self.la_out.setText(str(self.outPath))
    
    def makePicThread(self):
        t1 = threading.Thread(target=self.takePicturesCV2)
        t1.start()
        
    def takePictures(self):
        if self.inPath != None:       
            duration = float(ffmpeg.probe(self.inPath)["format"]["duration"])

            if self.end_time == '' or int(self.end_time) > duration or int(self.end_time)*-1 > duration:
                self.end_time = duration
            
            if int(self.end_time) <= 0:
                self.end_time = duration + int(self.end_time)
                        
            vid = ffmpeg.input(self.inPath, ss=int(self.start_time), to=self.end_time)
            vid = ffmpeg.filter(vid, 'fps', 1/float(self.time_between_pics))
            out = ffmpeg.output(vid, f'{self.outPath}/%03d.jpeg')
            out = out.global_args('-hide_banner')
            try:
                ffmpeg.run(out, overwrite_output=True)
            except ffmpeg._run.Error as e:
                print(e)

    def takePicturesCV2(self):
        if self.inPath != None:       
            duration = float(ffmpeg.probe(self.inPath)["format"]["duration"])

            if self.end_time == '' or int(self.end_time) > duration or int(self.end_time)*-1 > duration:
                self.end_time = duration
            
            if int(self.end_time) <= 0:
                self.end_time = duration + int(self.end_time)
                
            cap = cv2.VideoCapture(self.inPath)

            if not cap.isOpened():
                raise Exception('HELP! cv2 input video file issue')

            # os.makedirs(os.path.join(self.outPath, 'fotky'), exist_ok=True)
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            start_frame = round(fps * self.start_time)
            stop_frame = round(fps * self.end_time)
            step_frame = round(fps * self.time_between_pics)

            for n in range(start_frame, stop_frame, step_frame):
                cap.set(cv2.CAP_PROP_POS_FRAMES, n)
                ret, frame = cap.read()
                cv2.imwrite(f'{self.outPath}/{n}.jpeg', frame)
            
                
if __name__ == '__main__':
    app = QApplication(argv)
    t = ExampleWidget()
    exit(app.exec())