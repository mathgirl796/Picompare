from PyQt5.QtCore import QObject
import cv2
import numpy as np
import traceback
from PIL import Image, ImageSequence
from skimage.metrics import structural_similarity
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class PicCompareMethods(QThread):
    """
    添加新的图片格式：在`_read_image`中添加对应的格式支持，相信你一看就能懂
    添加新的评估方法：新建类似`_method_ssim`的函数(即_method_开头加上方法名)，按它的格式emit三个字典，无需返回值
    """
    _prefix = '_method_'
    compute_finished = pyqtSignal(list)

    def __init__(self) -> None:
        super(PicCompareMethods, self).__init__()

    @staticmethod
    def get_method_list():
        return [name[len(__class__._prefix):] for name in dir(__class__) if name.startswith(__class__._prefix)]
    
    def do_compare(self, method_name, file_path_1, file_path_2):
        self.method = getattr(PicCompareMethods, PicCompareMethods._prefix + method_name)
        self.file_path_1 = file_path_1
        self.file_path_2 = file_path_2
        self.start()

    def run(self):
        self.method(self, self.file_path_1, self.file_path_2)

    def _read_image(self, file_path):
        image = Image.open(file_path)
        if image.format == 'GIF':
            frames = [frame for frame in ImageSequence.Iterator(image)]
            if not frames:
                raise Exception()
            return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        else:
            return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)


    def _method_ssim(self, file_path_1, file_path_2):
        im1, im2 = None, None
        err_result = [{}, {}, {}]
        # 读取图片
        if not file_path_1 or not file_path_2:
            return
        try:    im1 = self._read_image(file_path_1)
        except: err_result[1]['error'] = f'cv2 cannot open file "{file_path_1}"'
        try:    im2 = self._read_image(file_path_2)
        except: err_result[2]['error'] = f'cv2 cannot open file "{file_path_2}"'

        # 读取完成
        if im1 is None or im2 is None:
            # 读取失败
            self.compute_finished.emit(err_result)
        else:
            # 读取成功
            self.compute_finished.emit([{'status': f'computing "{file_path_1}" with "{file_path_2}"'}, {}, {}])
            try:
                score = structural_similarity(im1, im2, channel_axis=2)
                self.compute_finished.emit([{'ssim': score}, {}, {}])
            except:
                self.compute_finished.emit([{'error': traceback.format_exc()}, {}, {}])


if __name__ == '__main__':
    pass