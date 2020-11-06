from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow, QAction, QDialog,\
    QFileDialog, QTableWidgetItem
from PyQt5.QtGui import QIcon

import os
import queue
from functools import reduce

from .UI_Compressor import Ui_Compressor
from .CompressStatus import CompressStatus
from .CompressThread import CompressThread
from .VideoItem import VideoItem


class Compressor(QMainWindow):
    DIRNAME = os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))))
    COMPRESS_DEFAULT_OUTPUT = os.path.abspath(DIRNAME+'/compressed_files')
    QUEUE_COMPRESS = queue.Queue()
    VIDEO_OBJECTS = {}
    THREADS = []
    COMPRESS_SETTINGS = {
        'bitrate': 7000,
        'quality': 1080,
        'codec': {'container': 'mp4'}
    }
    CODECS = {'mp4': 'libx264',
              'ogg': 'libtheora',
              'mp3': 'libmp3lame',
              'webm': 'libvpx'}
    QUALITY = {'1080p': 1080,
               '720p': 720,
               '576p': 576,
               '460p': 460}

    def __init__(self):
        super().__init__()
        self.ui = Ui_Compressor()
        loadFile = QAction(
            QIcon(self.DIRNAME+'/src/resources/icons/file.png'), 'Загрузить видео', self)
        loadFile.setShortcut('Ctrl+L')
        self.toolbar = self.addToolBar('Exit')
        loadFile.setStatusTip('Загрузить файл')
        loadFile.triggered.connect(self.loadFileDialog)
        self.toolbar.addAction(loadFile)
        self.ui.setupUi(self)
        self.ui.spinBox.setValue(7000)
        self.ui.pathToolButton.clicked.connect(self.directoryOutput)
        self.ui.pushButton.clicked.connect(self.startCompress)
        self.ui.pathEdit.setText(self.DIRNAME+'\\compressed_files')
        self.setFixedSize(824, 480)

    def loadFileDialog(self):
        video_files = QFileDialog.getOpenFileNames(self, 'Open file', '/',
            'Video files (*.mpg *.mkv *.mov *.wmv *.avi *.webm *.mp4)')[0]

        if(len(video_files)):
            for path in video_files:
                self.addList(VideoItem(path=path))

    def directoryOutput(self):
        video = QFileDialog()
        video.setFileMode(QFileDialog.DirectoryOnly)
        directory = video.getExistingDirectory(self,
                                               'Выберите дерикторию', directory=self.COMPRESS_DEFAULT_OUTPUT)
        self.COMPRESS_DEFAULT_OUTPUT = directory
        self.ui.pathEdit.setText(directory)

    def initThread(self):   
        for i in range(4):
            thread = CompressThread(self.QUEUE_COMPRESS,
                output=self.COMPRESS_DEFAULT_OUTPUT,
                **self.COMPRESS_SETTINGS)
            self.THREADS.append(thread)
            thread.progress.connect(self.__updateProgress,
                                    QtCore.Qt.QueuedConnection)
            thread.end_progress.connect(
                self.__stopThread, QtCore.Qt.QueuedConnection)
            thread.start()

    def startCompress(self):
        for thread in self.THREADS:
            thread.quit()
            
        self.COMPRESS_SETTINGS = {
            'bitrate': self.ui.spinBox.value(),
            'quality': self.QUALITY[self.ui.comboBox_2.currentText()],
            'codec': {
                'lib': self.CODECS[self.ui.comboBox.currentText()],
                'container': self.ui.comboBox.currentText()}
        }
        self.initThread()
        for video in self.VIDEO_OBJECTS.values():
            if(video.getStatus() != CompressStatus.COMPLETE):
                self.QUEUE_COMPRESS.put(
                    {'id': video.getIDitem(), 'filename': video.getPathFile()})
                video.setStatus(CompressStatus.PROCESS)
                self.ui.tableWidget.setItem(
                    video.getIDitem(), 4, QTableWidgetItem(video.getStatus()))

    def addList(self, item):
        num_rows = self.ui.tableWidget.rowCount()
        self.ui.tableWidget.insertRow(num_rows)
        self.ui.tableWidget.setItem(
            num_rows, 0, QTableWidgetItem(item.getFilename()))
        self.ui.tableWidget.setItem(
            num_rows, 1, QTableWidgetItem(item.getStatus()))
        self.ui.tableWidget.setItem(
            num_rows, 2, QTableWidgetItem(item.getDuration()))
        self.ui.tableWidget.setItem(
            num_rows, 3, QTableWidgetItem(item.getSize()))
        self.ui.tableWidget.setItem(
            num_rows, 4, QTableWidgetItem(item.getStatus()))
        item.setIDitem(num_rows)
        self.VIDEO_OBJECTS[num_rows] = item
        # self.ui.tableWidget.resizeColumnsToContents()

    def __updateProgress(self, id, progressValue):
        print("THREAD: {}. PROGRESS: {}".format(id, progressValue))
        size_videos = len(self.VIDEO_OBJECTS)
        self.VIDEO_OBJECTS[id].setProgress(progressValue)
        changeValue = reduce(lambda prev, el: prev+el.getProgress(),
                             self.VIDEO_OBJECTS.values(), 0)//size_videos
        self.ui.progressBar.setValue(changeValue)

    def __stopThread(self, id):
        self.VIDEO_OBJECTS[id].setStatus(CompressStatus.COMPLETE)
        self.ui.tableWidget.setItem(id, 4, QTableWidgetItem(
            self.VIDEO_OBJECTS[id].getStatus()))
