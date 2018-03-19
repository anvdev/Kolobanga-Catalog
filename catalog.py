import sys
import os
import subprocess

FREE = False

if FREE:
    from PySide2 import QtWidgets as QW
    # from PySide2 import QtCore as QC
    # from PySide2 import QtGui as QG
    from PySide2.QtCore import Qt as QT
else:
    from PyQt5 import QtWidgets as QW
    # from PyQt5 import QtCore as QC
    # from PyQt5 import QtGui as QG
    from PyQt5.QtCore import Qt as QT

ROOT = r'\\File-share\DATA\PROPS\C4D\MODELS'
UPDATE_FILE = r'\\File-share_NEW\System\Updates\Catalog\release.exe'  # Windows only


class MainWindow(QW.QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()

        # Common
        self.setWindowTitle('QCatalog')
        self.setMinimumSize(560, 160)
        self.resize(800, 600)

        # Visual Elements
        self.buttonFeedback = QW.QPushButton('Feedback')
        self.buttonFeedback.setFixedSize(80, 25)
        self.buttonFeedback.clicked.connect(self.buttonFeedback_click)
        self.buttonFeedback.setDisabled(True)  # Disabled in Qt version

        self.buttonHelp = QW.QPushButton('Help')
        self.buttonHelp.setFixedSize(80, 25)
        self.buttonHelp.clicked.connect(self.buttonHelp_click)

        self.buttonUpdate = QW.QPushButton('Update')
        self.buttonUpdate.setFixedSize(80, 25)
        self.buttonUpdate.clicked.connect(self.updateApplication)
        if os.path.exists(UPDATE_FILE):
            if os.stat(UPDATE_FILE).st_size == os.stat(__file__).st_size:
                self.buttonUpdate.setVisible(False)
        else:
            self.buttonUpdate.setVisible(False)

        self.labelPath = QW.QLabel('...')
        self.labelPath.setCursor(QT.PointingHandCursor)
        self.labelPath.setToolTip('Open Folder')
        self.labelPath.setAlignment(QT.AlignCenter)
        self.labelPath.keyPressEvent = self.openFolder

        self.treeView = QW.QTreeWidget()
        self.treeView.setFixedWidth(200)
        self.treeView.header().hide()
        self.treeView.setCursor(QT.PointingHandCursor)
        self.treeView.itemClicked.connect(self.treeItem_click)

        self.modelsScene = QW.QGraphicsScene()
        self.modelsView = QW.QGraphicsView(self.modelsScene)

        # self.statusBar = QW.QStatusBar()

        # Layouts
        horizontalLayoutTop = QW.QHBoxLayout()
        horizontalLayoutTop.setContentsMargins(4, 4, 4, 2)
        horizontalLayoutBottom = QW.QHBoxLayout()
        horizontalLayoutBottom.setContentsMargins(4, 2, 4, 4)
        verticalLayout = QW.QVBoxLayout(self)
        verticalLayout.setSpacing(4)
        verticalLayout.setContentsMargins(4, 4, 4, 4)
        verticalLayout.addLayout(horizontalLayoutTop)
        verticalLayout.addLayout(horizontalLayoutBottom)

        # Fill Layouts
        horizontalLayoutTop.addWidget(self.buttonFeedback)
        horizontalLayoutTop.addWidget(self.buttonHelp)
        horizontalLayoutTop.addWidget(self.buttonUpdate)
        horizontalLayoutTop.addWidget(self.labelPath)

        horizontalLayoutBottom.addWidget(self.treeView)
        horizontalLayoutBottom.addWidget(self.modelsView)

        # Initialization
        self.treeInit()

    def buttonFeedback_click(self):
        pass

    def buttonHelp_click(self):
        QW.QMessageBox.information(self, 'Help', ('Navigation: Arrows, Home, End, Page Up, Page Down\n'
                                                  'Selection: Mouse + Ctrl or Shift, Ctrl + A\n'
                                                  'Import: Alt + RMB click, Context Menu > Merge\n'
                                                  'Preview: Double LMB click, Context Menu > Preview'))

    def treeInit(self):
        root = self.treeView.invisibleRootItem()
        SOURCE = {'All': (),
                  'Items': (),
                  'Characters': ('Koloboks',
                                 'Animals',
                                 'Viruses',
                                 'Fido',
                                 'Aliens',
                                 'Draft',
                                 'Others'),
                  'Transport': (),
                  'Locations': ('Alien Planet',
                                'Antivirus Planet',
                                'City Planet',
                                'Fido Planet',
                                'Homepage Oracle',
                                'Kolobanga',
                                'New Year',
                                'SocialNet',
                                'Valley',
                                'Wiki'),
                  'Buildings': (),
                  'Objects': (),
                  'Others': ()}
        for key, value in SOURCE.items():
            upItem = QW.QTreeWidgetItem()
            upItem.setText(0, key)
            root.addChild(upItem)
            upItem.setExpanded(True)
            upItem.setFlags(QT.ItemIsEnabled | QT.ItemIsSelectable)
            if value:
                for i in value:
                    downItem = QW.QTreeWidgetItem()
                    downItem.setText(0, i)
                    downItem.setFlags(QT.ItemIsEnabled | QT.ItemIsSelectable)
                    upItem.addChild(downItem)

    def treeItem_click(self, item):
        path = os.path.join(ROOT, item.text(0))
        self.labelPath.setText(path)
        # self.loadDirectory(path)

    def updateApplication(self):
        pass

    def contextMenu(self):
        pass

    def merge(self, modelLink):
        pass

    def open(self, modelLink):
        os.system(os.path.join(ROOT, modelLink))

    def openFolder(self, folderLink):
        if sys.platform.startswith('win'):
            os.startfile(folderLink)
        elif sys.platform == 'darwin':
            subprocess.Popen(['open', folderLink])
        elif sys.platform.startswith('linux'):
            try:
                subprocess.Popen(['xdg-open', folderLink])  # Gnome, KDE, Xfce
            except OSError:
                QW.QMessageBox.warning(self, 'Unknown OS', "Can't open folder on this OS!")
        else:
            QW.QMessageBox.warning(self, 'Unknown OS', "Can't open folder on this OS!")

    def preview(self, previewLink):
        pass # os.system(os.path.join(ROOT, previewLink))

    def copyName(self):
        pass

    def copyFolderLink(self):
        pass

    def copyModelLink(self):
        pass

    def loadDirectory(self):
        pass


if __name__ == '__main__':
    app = QW.QApplication(sys.argv)

    # # Style
    # with open('style.qss', 'rt') as style:
    #     app.setStyleSheet(style.read())

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
