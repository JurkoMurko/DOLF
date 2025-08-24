from PyQt6.QtWidgets import QLineEdit

class MyLineEdit(QLineEdit):
    def __init__(self, str, parent):
        super().__init__(str, parent)
    
    def mousePressEvent(self, event):
        already_select_all = self.text() == self.selectedText()
        super().mousePressEvent(event)
        if not already_select_all:
            self.selectAll()
