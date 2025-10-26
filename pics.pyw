from PyQt6.QtWidgets import (
    QFileDialog,
    QApplication, 
    QPushButton, 
    QLabel, 
    QWidget, 
    QMessageBox, 
    QGridLayout, 
    QLineEdit
    )
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import (
    QObject,
    QRunnable,
    QThreadPool,
    pyqtSignal,
    pyqtSlot,
)
from sys import exit, argv
from json import dump, load
import cv2, os, ctypes, traceback, sys, platform
from PyQt6.QtCore import Qt
import uuid

APP_PATH = os.path.dirname(os.path.realpath(__file__)) + '/'

class MyLineEdit(QLineEdit):
    def __init__(self, str, parent):
        super().__init__(str, parent)
    
    def mousePressEvent(self, event):
        already_select_all = self.text() == self.selectedText()
        super().mousePressEvent(event)
        if not already_select_all:
            self.selectAll()

class Worker(QRunnable):
    def __init__(self, fn, thread_id, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.thread_id = thread_id
        self.args = args # Arguments to pass to the callback function
        self.kwargs = kwargs # Keywords to pass to the callback function
        self.signals = WorkerSignals()
        self.kwargs["progress_callback"] = self.signals.progress # Add the callback to our kwargs

    @pyqtSlot()
    def run(self):
        try:
            self.fn(self.thread_id, *self.args, **self.kwargs)
        except Exception:
            exctype, value, tb = sys.exc_info()
            self.signals.error.emit(exctype, value, tb)
        finally:
            self.signals.finished.emit(self.thread_id)

class WorkerSignals(QObject):
    finished = pyqtSignal(uuid.UUID)
    error = pyqtSignal(object,object,object) 
    progress = pyqtSignal(uuid.UUID, tuple)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        sys.excepthook = self.custom_excepthook
        
        if platform.system() == "Windows":
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('DOLF.automatic_pictures.v5') # sets Windows task bar icon
    
        with open(APP_PATH+"app_settings.json", "r") as f:
            dic = load(f)
            self.inPath = dic['input']
            self.start_time = dic['start time']
            self.end_time = dic['end time']
            self.time_between_pics = dic['interval']
            self.outFolderName = dic['defult picture folder name']
        
        # self.time_between_pics = 1
        # self.start_time = 35
        # self.end_time = ''

        self.threadpool = QThreadPool()
        self.initUI()
        
    def initUI(self):
        self.layout = QGridLayout()
        
        # Input File
        self.input_label = QLabel(self.inPath, self)
        self.input_button = QPushButton('In File', self)
        self.input_button.clicked.connect(self.btn_select_input_file)
        self.layout.addWidget(self.input_label,0,1)
        self.layout.addWidget(self.input_button,0,0)

        # Interval Input
        self.interval_label = QLabel('Time Between:', self)
        self.interval_line_edit = MyLineEdit('1.0',self)   
        self.interval_line_edit.setInputMask('0.0')
        self.interval_line_edit.textChanged[str].connect(self.onTimeBetweenChanged)
        self.layout.addWidget(self.interval_label,1,0)
        self.layout.addWidget(self.interval_line_edit,1,1)

        # Start Time Input
        self.start_label = QLabel('Start Time:', self)
        self.start_line_edit = MyLineEdit('35.0', self)
        self.start_line_edit.setInputMask('000.0')
        self.start_line_edit.textChanged[str].connect(self.onStartTimeChanged)
        self.layout.addWidget(self.start_label,2,0)
        self.layout.addWidget(self.start_line_edit,2,1)

        # Run Button
        self.pic_button = QPushButton('Take Pictures', self)
        self.pic_button.clicked.connect(self.pyqt_tread)
        self.layout.addWidget(self.pic_button,3,0)

        # Frog Pic
        self.frog_pic = QLabel(self)
        self.frog_pic.setPixmap(QPixmap(APP_PATH+'assets/frog.png'))
        self.layout.addWidget(self.frog_pic,3,1)
        self.frog_pic.setAlignment(Qt.AlignmentFlag.AlignRight)

        # Video Progress List
        self.thread_list={}
        self.in_progress_list = []
        self.p_progress_list = []
        
        self.setWindowTitle('Auto Pic')
        self.setWindowIcon(QIcon(APP_PATH+"assets/dolphin.ico"))
        self.setLayout(self.layout)
        self.show()
 
    def onTimeBetweenChanged(self):
        self.time_between_pics = self.interval_line_edit.text()

    def onStartTimeChanged(self):
        self.start_time = self.start_line_edit.text()

    def btn_select_input_file(self):
        if self.inPath == '':
            self.inPath = os.path.expanduser('~') + '/Desktop' 
        fname = QFileDialog.getOpenFileName(self, 'Open file', self.inPath)
        if fname[0]: # so if you cancel the dialog code doesn't run
            self.inPath = fname[0]
            self.input_label.setText(str(self.inPath))

            # saving file path selection for next opening of file dialog
            with open(APP_PATH+"app_settings.json", "r") as f:
                dic = load(f)
            
            dic['input'] = self.inPath
                
            with open(APP_PATH+'app_settings.json', 'w') as f:
                dump(dic, f, indent=4)
    
    def progress_fn(self, thread_id, n):
        progress_str = f'{n[0]}/{n[1]}'
        self.thread_list[thread_id][0].setText(progress_str) # 0 is the index of the progress string
        
    def thread_complete(self, thread_id):
        self.thread_list[thread_id][0].deleteLater()
        self.thread_list[thread_id][1].deleteLater()
        self.layout.removeWidget(self.thread_list[thread_id][0])
        self.layout.removeWidget(self.thread_list[thread_id][1])
        
    def print_output(self, s):
        print(s)
    
    def pyqt_tread(self):
        if self.inPath == '':
            raise FileExistsError("Input File Not Selected")
        
        # handels conflicting folder names
        i = 2
        out_dir_path = os.path.join(os.path.dirname(self.inPath), self.outFolderName) # For example C:/urs/fotky2
        output_dir_defult_name = out_dir_path # For example C:/usr/fotky
        while os.path.isdir(out_dir_path):
            if i < 100: # max for the while loop
                out_dir_path = output_dir_defult_name + f'{i}'
                i += 1
            else:
                raise Exception("Tried >100 folder names. Folder with defult name already exists")
            
        thread_id = uuid.uuid4()
        
        worker = Worker(
            self.takePictures,
            thread_id = thread_id,
            inputPath = self.inPath, 
            outputFolderName = out_dir_path,
            startTime = float(self.start_time),
            endTime = float(self.end_time),
            seccondsInterval = float(self.time_between_pics)
        )
        worker.signals.finished.connect(self.thread_complete)
        worker.signals.progress.connect(self.progress_fn)
        worker.signals.error.connect(self.custom_excepthook)
        self.threadpool.start(worker)
        
        # Progress Label
        self.input_path_label = QLabel(self.inPath, self) # EX: C:/user/video/video.mov
        self.progress_string_label = QLabel('0/0', self) # '0/34'
        self.thread_list[thread_id] = [self.progress_string_label, self.input_path_label]
        row_count = self.layout.rowCount()
        self.layout.addWidget(self.input_path_label,row_count,1)
        self.layout.addWidget(self.progress_string_label,row_count,0)

    def takePictures(self, thread_id, inputPath, outputFolderName, startTime, endTime, seccondsInterval, progress_callback):
        cap = cv2.VideoCapture(inputPath)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        duration = frame_count/fps
        
        picFolderPath = os.path.join(os.path.dirname(inputPath), outputFolderName) # copy
        os.makedirs(picFolderPath)

        if endTime == '' or endTime > duration or endTime*-1 > duration:
            endTime = duration
        
        if float(endTime) <= 0:
            endTime = duration + float(endTime)
        
        # rounding might be where the small end time error comes from
        start_frame = round(fps * float(startTime))
        stop_frame = round(fps * float(endTime))
        step_frame = round(fps * float(seccondsInterval))
        
        total_num_pics = ((stop_frame - start_frame) // step_frame) +1 #idk why +1
        for n in range(start_frame, stop_frame, step_frame):
            pic_num = int((n-start_frame)/step_frame) +1 # idk why int what about frame 1 w/ step 1
            cap.set(cv2.CAP_PROP_POS_FRAMES, n) # says frame 9030 but got frame 9664; this is why end time is broken
            ret, frame = cap.read()
            cv2.imwrite(f'{picFolderPath}/{pic_num}.jpeg', frame)
            progress_callback.emit(thread_id, (pic_num, total_num_pics))
            
    def custom_excepthook(self, exc_type, exc_value, exc_traceback):
        traceback.print_exception(exc_type, exc_value, exc_traceback)
        QMessageBox.critical(self, 'ERROR', ''.join(traceback.format_exception(exc_value)))

app = QApplication(argv)
t = MainWindow()
exit(app.exec())  