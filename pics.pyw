from PyQt6.QtWidgets import QFileDialog,QApplication, QPushButton, QLabel, QWidget, QMessageBox
from PyQt6.QtGui import QPixmap, QIcon
from sys import exit, argv
from json import dump, load
import threading, cv2, os, ctypes, traceback, sys
from classes.MyLineEdit import MyLineEdit

APP_PATH = os.path.dirname(os.path.realpath(__file__)) + '/'

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        sys.excepthook = self.custom_excepthook # Assign the custom function to sys.excepthook
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('DOLF.automatic_pictures.v5') # sets Windows task bar icon
    
        self.time_between_pics = 1
        self.start_time = 35
        self.end_time = ''
        
        with open(APP_PATH+"app_settings.json", "r") as f: # you shouldn't have to edit a json
            dic = load(f)
            self.inPath = dic['input']
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

        self.qle = MyLineEdit(str(self.time_between_pics), self)
        self.ql = QLabel('Time Between:', self)
        self.ql.move(20, 100)
        self.qle.setGeometry(110,98,40,20)
        self.qle.textChanged[str].connect(self.onTimeBetweenChanged)

        self.qle2 = MyLineEdit(str(self.start_time), self)
        self.ql2 = QLabel('Start Time:', self)
        self.ql2.move(170, 100)
        self.qle2.setGeometry(230,98,50,20)
        self.qle2.textChanged[str].connect(self.onStartTimeChanged)

        self.btn_pic = QPushButton('Take Pictures', self)
        self.btn_pic.move(20, 150)
        self.btn_pic.clicked.connect(self.mk_pic_thread)
 
        self.qlp = QLabel('progress:', self)
        self.qlp.move(100, 150)
        self.qlp.hide()

        self.pixmap = QPixmap(APP_PATH+'assets/frog.png')
        self.lbl = QLabel(self)
        self.lbl.setPixmap(self.pixmap)
        self.lbl.move(450,100)

        self.setGeometry(300, 300, 550, 200)
        self.setWindowTitle('Auto Pic')
        self.setWindowIcon(QIcon(APP_PATH+"assets/dolphin.ico"))
        self.show()
 
    def onTimeBetweenChanged(self, num):
        if num == '':
            self.time_between_pics = 1
        else:
            self.time_between_pics = num

    def onStartTimeChanged(self, num):
        if num == '' or self.start_time < 0:
            self.start_time = 0
        else:
            self.start_time = num

    def btn_select_input_file(self):
        if self.inPath == '':
            self.inPath = os.path.expanduser('~') + '/Desktop' # opens file dialog at current home path + desktop
        fname = QFileDialog.getOpenFileName(self, 'Open file', self.inPath)
        if fname[0]: # so if you cancel the dialog code doesn't run
            self.inPath = fname[0]
            self.la_in.setText(str(self.inPath))

            # saving file path selection for next opening of file dialog
            with open(APP_PATH+"app_settings.json", "r") as f:
                dic = load(f)
            
            dic['input'] = self.inPath
                
            with open(APP_PATH+'app_settings.json', 'w') as f:
                dump(dic, f, indent=4)
    
    def mk_pic_thread(self): # This is for the gui to stay responsive not a speed optimization
        if self.inPath != None:
            self.qlp.show()
            vars = {
                'inputPath':self.inPath, 
                'outputFolderName':self.outFolderName,
                'startTime' : self.start_time,
                'endTime' : self.end_time,
                'seccondsInterval' : self.time_between_pics
            }
            t1 = threading.Thread(target=self.takePictures, kwargs=vars)
            t1.start()
            self.qlp.setText('Working')

    @staticmethod
    def takePictures(inputPath, outputFolderName, startTime, endTime, seccondsInterval):
        cap = cv2.VideoCapture(inputPath)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count/fps
        
        picFolderPath = os.path.join(os.path.dirname(inputPath), outputFolderName)
        os.makedirs(picFolderPath, exist_ok=True)

        if endTime == '' or int(endTime) > duration or int(endTime)*-1 > duration:
            endTime = duration
        
        if int(endTime) <= 0:
            endTime = duration + int(endTime)
        
        start_frame = round(fps * float(startTime))
        stop_frame = round(fps * float(endTime))
        step_frame = round(fps * float(seccondsInterval))
        
        for n in range(start_frame, stop_frame, step_frame):
            cap.set(cv2.CAP_PROP_POS_FRAMES, n)
            ret, frame = cap.read()
            cv2.imwrite(f'{picFolderPath}/{n}.jpeg', frame)
        
    def custom_excepthook(self, exc_type, exc_value, exc_traceback):
        traceback.print_exception(exc_type, exc_value, exc_traceback)
        QMessageBox.critical(self, 'ERROR', ''.join(traceback.format_exception(exc_value)))

app = QApplication(argv)
t = MainWindow()
exit(app.exec())  