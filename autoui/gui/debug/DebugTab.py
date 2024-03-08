from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QGridLayout, QSplitter

from autoui.gui.debug.FrameWidget import FrameWidget
from autoui.gui.debug.InfoWidget import InfoWidget
from autoui.gui.debug.LoggerWidget import LoggerWidget


class DebugTab(QWidget):
    def __init__(self):
        super().__init__()

        self.mainLayout = QGridLayout()
        self.setLayout(self.mainLayout)

        # Top row setup with horizontal splitter
        self.topSplitter = QSplitter(Qt.Horizontal)
        self.topSplitter.setMinimumHeight(300)
        self.info_widget = InfoWidget()
        self.info_widget.setFixedWidth(200)
        self.frame_widget = FrameWidget()
        self.rightTextEdit = FrameWidget()
        self.topSplitter.addWidget(self.info_widget)
        self.topSplitter.addWidget(self.rightTextEdit)

        # Bottom row setup
        self.logger = LoggerWidget()

        # Main splitter to handle top and bottom rows
        self.mainSplitter = QSplitter(Qt.Vertical)
        self.mainSplitter.addWidget(self.topSplitter)
        self.mainSplitter.addWidget(self.logger)

        # Add the main splitter to the layout
        self.mainLayout.addWidget(self.mainSplitter, 0, 0)

        self.mainSplitter.setStretchFactor(0, 8)  # 30% for the top widget
        self.mainSplitter.setStretchFactor(1, 2)  # 70%
