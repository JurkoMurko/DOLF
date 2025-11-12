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
    Qt
)
from json import dump, load
import cv2, os, ctypes, traceback, platform, uuid, sys

APP_PATH = os.path.dirname(os.path.realpath(__file__))
SETTINGS_PATH = os.path.join(APP_PATH, "app_settings.json")

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        sys.excepthook = self.custom_excepthook
        
        if platform.system() == "Windows":
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('DOLF.automatic_pictures.v5') # sets Windows task bar icon
            
        self.loadDefultValues()
        self.threadpool = QThreadPool()
        self.initUI()
        
    def loadDefultValues(self):
        if not os.path.exists(SETTINGS_PATH):
            with open(SETTINGS_PATH, 'x') as f:
                user_directory = str(os.path.expanduser('~'))
                dic = {
                "input": user_directory,
                "start time": 35,
                "end time": -10.4,
                "interval": 1,
                "defult picture folder name": "fotky"
                }
                dump(dic, f, indent=4)
        
        with open(SETTINGS_PATH, "r") as f:
            dic = load(f)
            self.input_file_path = dic['input']
            self.start_time = dic['start time']
            self.end_time = dic['end time']
            self.time_between_pics = dic['interval']
            self.output_folder_name = dic['defult picture folder name']
            
        self.input_file_directory = os.path.dirname(self.input_file_path)
        self.input_file_name = os.path.basename(self.input_file_path)
    
    def initUI(self):
        self.layout = QGridLayout()
        
        # Input File
        input_path_label_name = os.path.relpath(self.input_file_path)
        self.input_label = QLabel(input_path_label_name, self)
        self.input_button = QPushButton('Input File', self)
        self.input_button.clicked.connect(self.btn_select_input_file)
        self.layout.addWidget(self.input_label,0,1)
        self.layout.addWidget(self.input_button,0,0)

        # Interval Input
        self.interval_label = QLabel('Time Between:', self)
        self.interval_line_edit = MyLineEdit('1.0',self)   
        self.interval_line_edit.setInputMask('0.0')
        self.interval_line_edit.editingFinished.connect(self.onPicIntervalChanged)
        self.layout.addWidget(self.interval_label,1,0)
        self.layout.addWidget(self.interval_line_edit,1,1)

        # Start Time Input
        self.start_label = QLabel('Start Time:', self)
        self.start_line_edit = MyLineEdit('35.0', self)
        self.start_line_edit.setInputMask('000.0')
        self.start_line_edit.editingFinished.connect(self.onStartTimeChanged)
        self.layout.addWidget(self.start_label,2,0)
        self.layout.addWidget(self.start_line_edit,2,1)

        # Run Button
        self.pic_button = QPushButton('Take Pictures', self)
        self.pic_button.clicked.connect(self.startPYQTThread)
        self.layout.addWidget(self.pic_button,3,0)

        # Frog Pic
        self.frog_pic = QLabel(self)
        self.frog_pic.setPixmap(QPixmap(os.path.join(APP_PATH,'assets/frog.png')))
        self.layout.addWidget(self.frog_pic,3,1)
        self.frog_pic.setAlignment(Qt.AlignmentFlag.AlignRight)

        # Video Progress List
        self.thread_list={}
        
        self.setWindowTitle('DOLF')
        self.setWindowIcon(QIcon(os.path.join(APP_PATH,"assets/dolphin.ico")))
        self.setLayout(self.layout)
        self.show()

    def btn_select_input_file(self):
        path = QFileDialog.getOpenFileName(self, 'Open file', self.input_file_path)[0]
        
        if path: # doesn't run if file secection dialog is canceled
            self.input_file_path = path
            self.input_file_directory = os.path.dirname(self.input_file_path)
            self.input_file_name = os.path.basename(self.input_file_path)
            input_path_label_name = os.path.relpath(self.input_file_path)
            self.input_label.setText(input_path_label_name)
                                
    def onPicIntervalChanged(self):
        if self.interval_line_edit.text() != '.':
            self.time_between_pics = float(self.interval_line_edit.text())

    def onStartTimeChanged(self):
        if self.start_line_edit.text() != '.': 
            self.start_time = float(self.start_line_edit.text())
            print("start time changed")
        
    def progress_fn(self, thread_id, n):
        progress_str = f'{n[0]}/{n[1]}'
        self.thread_list[thread_id][0].setText(progress_str) # 0 is the index of the progress string
        
    def thread_complete(self, thread_id):
        self.thread_list[thread_id][0].deleteLater()
        self.thread_list[thread_id][1].deleteLater()
        self.layout.removeWidget(self.thread_list[thread_id][0])
        self.layout.removeWidget(self.thread_list[thread_id][1])
    
    def startPYQTThread(self):
        thread_id = uuid.uuid4()
        
        worker = Worker(
            self.takePictures,
            thread_id = thread_id,
            input_file_path = self.input_file_path, 
            output_folder_path = self.createUniqueFolder(os.path.dirname(self.input_file_path)),
            start_time = self.start_time,
            end_time = self.end_time,
            time_between_pics = self.time_between_pics
        )
        
        # Progress Label
        input_path_label_name = os.path.relpath(self.input_file_path)
        self.input_path_label = QLabel(input_path_label_name, self)
        self.progress_string_label = QLabel('0/0', self)
        self.thread_list[thread_id] = [self.progress_string_label, self.input_path_label]
        row_count = self.layout.rowCount() # must be here or it update by the second call
        self.layout.addWidget(self.input_path_label,row_count,1)
        self.layout.addWidget(self.progress_string_label,row_count,0)
        
        worker.signals.finished.connect(self.thread_complete)
        worker.signals.progress.connect(self.progress_fn)
        worker.signals.error.connect(self.custom_excepthook)
        self.threadpool.start(worker)

    def takePictures(self, thread_id, input_file_path, output_folder_path, start_time, end_time, time_between_pics, progress_callback):        
        cap = cv2.VideoCapture(input_file_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        duration = frame_count/fps

        if end_time > duration or end_time * -1 > duration or end_time == -1:
            end_time = duration
        elif end_time <= 0:
            end_time = duration + end_time
        
        start_frame = int(fps * start_time)
        stop_frame = int(fps * end_time)
        step_frame = int(fps * time_between_pics)
        
        total_num_pics = ((stop_frame - start_frame) // step_frame) +1 #idk why +1
        for n in range(start_frame, stop_frame, step_frame):
            pic_num = int((n-start_frame)/step_frame) +1 # idk why int what about frame 1 w/ step 1
            cap.set(cv2.CAP_PROP_POS_FRAMES, n) # says frame 9030 but got frame 9664; this is why end time is broken
            ret, frame = cap.read()
            cv2.imwrite(f'{output_folder_path}/{pic_num}.jpeg', frame)
            progress_callback.emit(thread_id, (pic_num, total_num_pics))
    
    def createUniqueFolder (self, parent_directory):
        output_folder_path = os.path.join(parent_directory, self.output_folder_name)
        
        # auto create folder if folder name conflicts
        for i in range(2,101):
            if os.path.isdir(output_folder_path):
                output_folder_path = os.path.join(parent_directory, self.output_folder_name) + str(i)
            else:
                break
            if i == 100:
                raise Exception("Tried >100 folder names. Folder with defult name already exists")
        
        os.makedirs(output_folder_path)
        return output_folder_path

    def closeEvent(self, event): # special named function that runs when the gui closes
        # saving settings for next opening
        with open(SETTINGS_PATH, "a+") as f:
            f.seek(0) # set cursor at files start becuase we are in open's append mode
            dic = load(f)
            dic['input'] = self.input_file_path
            dic['start time'] = self.start_time
            dic['interval'] = self.time_between_pics
            f.truncate(0) # delete file's contense
            dump(dic, f, indent=4)
            
        event.accept()
    
    def custom_excepthook(self, exc_type, exc_value, exc_traceback):
        traceback.print_exception(exc_type, exc_value, exc_traceback)
        QMessageBox.critical(self, 'ERROR', ''.join(traceback.format_exception(exc_value)))
        
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
        self.args = args 
        self.kwargs = kwargs 
        self.signals = WorkerSignals()
        self.kwargs["progress_callback"] = self.signals.progress 

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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    t = MainWindow()
    sys.exit(app.exec())  