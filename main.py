from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from picompare import PicCompareMethods

class GraphicsView(QWidget):
    new_file_selected = pyqtSignal(str) # 选择了新图片，需要进行计算

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setStyleSheet('border: 0px solid black; background-color:rgb(233,233,233);')

        self.setupUi()
        self.initUi()
    
    def setupUi(self):
        self.layout = QVBoxLayout(self)

        self.graph_label = QLabel()
        self.graph_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.graph_label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self.file_path_label = QLabel()
        self.file_path_label.setMaximumHeight(20)

        self.layout.addWidget(self.graph_label)
        self.layout.addWidget(self.file_path_label)
        
    def initUi(self):
        self.file_path = ""
        self.graph_label.setText('拖动图片到此处')
        self.file_path_label.setText('此处将显示图片地址')
    
    def set_image_and_filepath(self, set_image=True, set_filepath=True):
        if set_image:
            image = QPixmap()
            if image.load(self.file_path):
                self.graph_label.setPixmap(image.scaled(self.graph_label.width(), self.graph_label.height(), Qt.KeepAspectRatio))
        if set_filepath:
            self.file_path_label.setText(self.file_path)   
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        event.accept()
    
    def dropEvent(self, event):
        # 判断文件类型
        if event.mimeData().hasUrls():
            # 获取文件路径
            self.file_path = event.mimeData().urls()[0].toLocalFile()
            self.new_file_selected.emit(self.file_path)
            self.set_image_and_filepath()
    
    def resizeEvent(self, event: QResizeEvent):
        self.set_image_and_filepath(set_filepath=False)   

    def mouseReleaseEvent(self, a0: QMouseEvent) -> None:
        self.initUi()

class UI(QWidget):
    def __init__(self):
        super().__init__()
        # 初始化时先新建一个容纳
        self.pic_comparer = PicCompareMethods()

    def setupUi(self):
        # 子布局
        self.vLayoutWrap = QVBoxLayout()
        self.hLayoutGraphs = QHBoxLayout()
        self.hLayoutTexts = QHBoxLayout()
        self.vLayoutMethod = QVBoxLayout()
        # 子部件
        self.lGraphicsView = GraphicsView(self)
        self.rGraphicsView = GraphicsView(self)
        self.lTextBrowser = QTextBrowser(self)
        self.rTextBrowser = QTextBrowser(self)
        self.resultTextBrowser = QTextBrowser(self)
        self.methodComboBox = QComboBox(self)
        self.methodComboBox.addItems(PicCompareMethods.get_method_list())
        self.methodComboBox.setCurrentIndex(0)
        # 安装子部件
        self.vLayoutWrap.addLayout(self.hLayoutGraphs, 3)
        self.vLayoutWrap.addLayout(self.hLayoutTexts, 1)
        self.hLayoutGraphs.addWidget(self.lGraphicsView)
        self.hLayoutGraphs.addWidget(self.rGraphicsView)
        self.hLayoutTexts.addWidget(self.lTextBrowser)
        self.hLayoutTexts.addLayout(self.vLayoutMethod)
        self.hLayoutTexts.addWidget(self.rTextBrowser)
        self.vLayoutMethod.addWidget(self.methodComboBox)
        self.vLayoutMethod.addWidget(self.resultTextBrowser)
        # 设置窗口信息
        self.resize(800, 600)
        self.setLayout(self.vLayoutWrap)
        # 连接信号与槽
        lambda_compare_slot = lambda: self.start_compare_slot(self.methodComboBox.currentText(), self.lGraphicsView.file_path, self.rGraphicsView.file_path)
        self.lGraphicsView.new_file_selected.connect(lambda_compare_slot)
        self.rGraphicsView.new_file_selected.connect(lambda_compare_slot)
        self.methodComboBox.currentIndexChanged.connect(lambda_compare_slot)

    def start_compare_slot(self, method_name, file_path_0, file_path_1):
        self.pic_comparer.terminate()
        self.pic_comparer.wait()
        self.pic_comparer = PicCompareMethods()
        self.pic_comparer.compute_finished.connect(self.finish_compare_slot)
        self.pic_comparer.do_compare(method_name, file_path_0, file_path_1)
        
    def finish_compare_slot(self, event):
        result, lData, rData = event
        decode = lambda my_dict: '\n'.join([f"{k}: {v}" for k, v in my_dict.items()])
        self.lTextBrowser.setText(decode(lData))
        self.resultTextBrowser.setText(decode(result))
        self.rTextBrowser.setText(decode(rData))

if __name__ == '__main__':
    app = QApplication([])
    ui = UI()
    ui.setupUi()
    ui.show()
    app.exec_()