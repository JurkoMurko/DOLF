from PyQt6.QtWidgets import (QFileDialog, QApplication, QPushButton, 
                             QLabel, QProgressBar, QWidget, QLineEdit)
from PyQt6.QtGui import QPixmap
from sys import exit, argv
from moviepy.editor import VideoFileClip
from json import load
import ffmpeg

import time
import datetime

class ExampleWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.time_between_pics = 0.5
        self.start_time = 0
        self.end_time = -1
        
        with open('defult_settings.json', 'r') as f:
            dic = load(f)
            self.inPath = dic['input']
            self.outPath = dic['output']

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

        qle = QLineEdit(str(0.5), self)
        ql = QLabel('Time Between:', self)
        ql.move(20, 100)
        qle.setGeometry(110,98,40,20)
        qle.textChanged[str].connect(self.onChanged)

        qle2 = QLineEdit(str(''), self)
        ql2 = QLabel('Start Time', self)
        ql2.move(170, 100)
        qle2.setGeometry(230,98,40,20)
        qle2.textChanged[str].connect(self.onChanged2)

        qle3 = QLineEdit(str(''), self)
        ql3 = QLabel('End Time', self)
        ql3.move(290, 100)
        qle3.setGeometry(380,98,40,20)
        qle3.textChanged[str].connect(self.onChanged3)

        self.btn_pic = QPushButton('Take Pictures', self)
        self.btn_pic.move(20, 150)
        self.btn_pic.clicked.connect(self.takePictures) 

        self.pbar = QProgressBar(self)
        self.pbar.setGeometry(100, 150, 200, 40)
        self.pbar.hide()

        pixmap = QPixmap('small_frog.png')
        lbl = QLabel(self)
        lbl.setPixmap(pixmap)
        lbl.move(450,100)

        self.setGeometry(300, 300, 550, 200)
        self.setWindowTitle('Auto Pic')
        self.show()

    def onChanged(self, num):
        self.time_between_pics = num

    def onChanged2(self, num):
        if self.start_time == '' or self.start_time < 0:
                self.start_time = 0
        self.start_time = num

    def onChanged3(self, num):
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

    def takePictures4xSLOWER(self):
        if self.inPath != None:
            start = time.time()
            
            clip = VideoFileClip(self.inPath)
            self.start_time = int(self.start_time)
            self.end_time = int(self.end_time)
            
            if self.end_time == -1 or self.end_time > clip.duration:
                self.end_time = clip.duration
                
            interval_length = self.end_time - self.start_time
            self.pbar.show()
            
            curentTime = self.start_time
            i = 1
            while curentTime < self.end_time:
                self.pbar.setValue(int(100 * (curentTime - self.start_time) / interval_length))
                clip.save_frame(f"{self.outPath}\\pic_{i}.jpeg", curentTime)
                curentTime += float(self.time_between_pics)
                i += 1
                
            self.pbar.setValue(0)
            self.pbar.hide()
            
            time_elapsed = time.time() - start
            form = datetime.timedelta(seconds=time_elapsed)
            print('The Program Took: ', form)
            print(clip.duration/time_elapsed)
            
    def takePictures(self):
        if self.inPath != None:
            self.start_time = int(self.start_time)
            self.end_time = int(self.end_time)
            
            duration = ffmpeg.probe(self.inPath)["format"]["duration"]

            if self.end_time == -1 or self.end_time > duration:
                self.end_time = duration
                        
            vid = ffmpeg.input(self.inPath, ss=self.start_time, to=self.end_time)
            vid = ffmpeg.filter(vid, 'fps', 1/int(self.time_between_pics))
            out = ffmpeg.output(vid, '%03d.jpeg')
            out = out.global_args('-hide_banner')
            ffmpeg.run(out, overwrite_output=True)
                
def main():
    app = QApplication(argv)
    t = ExampleWidget()
    exit(app.exec())

if __name__ == '__main__':
    main()
