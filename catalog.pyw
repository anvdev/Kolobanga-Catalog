import sys
import os
import subprocess
import socket

FREE = True

if FREE:
    from PySide2 import QtWidgets as QW
    from PySide2 import QtCore as QC
    from PySide2 import QtGui as QG
    from PySide2.QtCore import Qt as QT
else:
    from PyQt5 import QtWidgets as QW
    from PyQt5 import QtCore as QC
    from PyQt5 import QtGui as QG
    from PyQt5.QtCore import Qt as QT

ROOT = r'\\File-share\DATA\PROPS\C4D\MODELS'
UPDATE_FILE = r'\\File-share_NEW\System\Updates\Catalog\release.exe'  # Windows only


class MainWindow(QW.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        # Common
        self.widget = QW.QWidget(self)
        self.setCentralWidget(self.widget)
        self.setWindowTitle('QCatalog')
        self.setMinimumSize(540, 160)
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

        self.labelRoot = QW.QLabel('...')
        self.labelRoot.setCursor(QT.PointingHandCursor)
        self.labelRoot.setToolTip('Open Folder')
        self.labelRoot.setAlignment(QT.AlignCenter)
        self.labelRoot.mousePressEvent = self.openRoot

        self.treeView = QW.QTreeWidget()
        self.treeView.setFixedWidth(200)
        self.treeView.header().hide()
        self.treeView.setCursor(QT.PointingHandCursor)
        self.treeView.itemClicked.connect(self.treeItem_click)

        self.modelsView = QW.QListWidget(self.widget)
        self.modelsView.setViewMode(QW.QListView.IconMode)
        self.modelsView.setResizeMode(QW.QListView.Adjust)
        self.modelsView.setDragDropMode(QW.QAbstractItemView.NoDragDrop)
        self.modelsView.setSelectionMode(QW.QAbstractItemView.ExtendedSelection)
        self.modelsView.setIconSize(QC.QSize(120, 90))
        self.modelsView.setSpacing(2)
        self.modelsView.setContextMenuPolicy(QT.CustomContextMenu)
        self.modelsView.customContextMenuRequested.connect(self.contextMenu)
        self.modelsView.doubleClicked.connect(lambda :self.previewAction(self.modelsView.selectedItems()))

        # self.previewImage = QW.QLabel()
        # self.previewImage.setFixedSize(220, 160)
        #
        # self.infoPane = QW.QTextBrowser()
        # self.infoPane.setFixedWidth(220)

        self.statusBar = QW.QStatusBar()
        self.statusBar.setContentsMargins(10, 0, 10, 5)
        self.setStatusBar(self.statusBar)
        self.labelStatus = QW.QLabel()
        self.statusBar.addWidget(self.labelStatus)

        # Layouts
        self.horizontalLayoutTop = QW.QHBoxLayout()
        self.horizontalLayoutTop.setContentsMargins(4, 4, 4, 2)
        # self.verticalLayoutRight = QW.QVBoxLayout()
        self.horizontalLayoutBottom = QW.QHBoxLayout()
        self.horizontalLayoutBottom.setContentsMargins(4, 2, 4, 4)
        self.verticalLayout = QW.QVBoxLayout(self.widget)
        self.verticalLayout.setSpacing(4)
        self.verticalLayout.setContentsMargins(4, 4, 4, 0)
        self.verticalLayout.addLayout(self.horizontalLayoutTop)
        self.verticalLayout.addLayout(self.horizontalLayoutBottom)

        # Fill Layouts
        self.horizontalLayoutTop.addWidget(self.buttonFeedback)
        self.horizontalLayoutTop.addWidget(self.buttonHelp)
        self.horizontalLayoutTop.addWidget(self.buttonUpdate)
        self.horizontalLayoutTop.addWidget(self.labelRoot)

        self.horizontalLayoutBottom.addWidget(self.treeView)
        self.horizontalLayoutBottom.addWidget(self.modelsView)

        # self.horizontalLayoutBottom.addLayout(self.verticalLayoutRight)
        # self.verticalLayoutRight.addWidget(self.previewImage)
        # self.verticalLayoutRight.addWidget(self.infoPane)

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
        SOURCE = {#'All': (),
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
                                'City',
                                'Fido',
                                'Homepage Oracle',
                                'Kolobanga',
                                'New Year',
                                'SocialNet',
                                'Valley',
                                'Wiki'),
                  'Buildings': (),
                  'Objects': (),
                  'Others': ()}
        allItem = QW.QTreeWidgetItem()
        allItem.setText(0, 'All')
        allItem.setData(0, QT.UserRole, ROOT)
        root.addChild(allItem)
        for key, value in SOURCE.items():
            upItem = QW.QTreeWidgetItem()
            upItem.setText(0, key)
            upItem.setData(0, QT.UserRole, os.path.join(ROOT, key))
            root.addChild(upItem)
            upItem.setExpanded(True)
            upItem.setFlags(QT.ItemIsEnabled | QT.ItemIsSelectable)
            if value:
                for i in value:
                    downItem = QW.QTreeWidgetItem()
                    downItem.setText(0, i)
                    downItem.setData(0, QT.UserRole, os.path.join(ROOT, key, i.replace(' ', '_')))
                    downItem.setFlags(QT.ItemIsEnabled | QT.ItemIsSelectable)
                    upItem.addChild(downItem)

    def treeItem_click(self, item):
        path = item.data(0, QT.UserRole)
        self.labelRoot.setText(path)
        self.fillModelList(path)

    def updateApplication(self):
        pass

    def contextMenu(self, pos):
        functions = {'Merge': self.mergeAction,
                     'Open': self.openFileAction,
                     'Open Folder': self.openFolderAction,
                     'Preview': self.previewAction,
                     'Copy Name': self.copyNameAction,
                     'Copy Folder Link': self.copyFolderLinkAction,
                     'Copy Model Link': self.copyModelLinkAction}
                     # 'Show Information': self.showInfo}
        if self.modelsView.selectedItems():
            actions = ['Merge',
                       'Open',
                       'Open Folder',
                       '-',
                       # 'Show Information',
                       'Preview',
                       '-',
                       'Copy Name',
                       'Copy Folder Link',
                       'Copy Model Link']
            menu = QW.QMenu()
            for a in actions:
                if a != '-':
                    menu.addAction(QW.QAction(a, self))
                else:
                    menu.addSeparator()
            try:
                reacton = menu.exec_(QG.QCursor().pos())
                functions.get(reacton.text())(self.modelsView.selectedItems())
            except:
                pass

    def mergeAction(self, items):
        reply = None
        if len(items) > 3:
            reply = QW.QMessageBox.question(self, 'Merge Operation', f'Too many files ({len(items)}). Would you like to merge all?', QW.QMessageBox.Yes | QW.QMessageBox.No, QW.QMessageBox.Yes)
            if reply == QW.QMessageBox.Yes or reply == None:
                for item in items:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.connect(('127.0.0.1', 2900))
                    link = item.data(QT.UserRole).replace('_tmb.jpg', '.c4d')
                    sock.send(f'Content-Length: 300\nEncoding: binary\nFilename: {link}\nOrigin: Merge\nPassword: 7c9fb847d117531433435b68b61f91f6'.encode('ascii', 'ignore'))
                    sock.close()

    def openFile(self, fileLink):
        if sys.platform.startswith('win'):
            os.startfile(fileLink)
        elif sys.platform == 'darwin':
            pass
        elif sys.platform.startswith('linux'):
            pass
        else:
            QW.QMessageBox.warning(self, 'Unknown OS', "Can't open file on this OS!")

    def openFileAction(self, items):
        reply = None
        if len(items) > 3:
            reply = QW.QMessageBox.question(self, 'Open File Operation', f'Too many files ({len(items)}). Would you like to open all?', QW.QMessageBox.Yes | QW.QMessageBox.No, QW.QMessageBox.Yes)
        if reply == QW.QMessageBox.Yes or reply == None:
            data = []
            for item in items:
                self.openFile(item.data(QT.UserRole).replace('_tmb.jpg', '.c4d'))

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

    def openFolderAction(self, items):
        reply = None
        if len(items) > 3:
            reply = QW.QMessageBox.question(self, 'Open Folder Operation', f'Too many folders ({len(items)}). Would you like to open all?', QW.QMessageBox.Yes | QW.QMessageBox.No, QW.QMessageBox.Yes)
        if reply == QW.QMessageBox.Yes or reply == None:
            for item in items:
                self.openFolder(os.path.dirname(item.data(QT.UserRole)))

    def preview(self, pictureLink):
        if sys.platform.startswith('win'):
            os.startfile(pictureLink)
        elif sys.platform == 'darwin':
            pass
        elif sys.platform.startswith('linux'):
            pass
        else:
            QW.QMessageBox.warning(self, 'Unknown OS', "Can't open preview on this OS!")

    def previewAction(self, items):
        reply = None
        if len(items) > 1:
            reply = QW.QMessageBox.question(self, 'Preview Operation', f'Too many files ({len(items)}). Would you like to preview all?', QW.QMessageBox.Yes | QW.QMessageBox.No, QW.QMessageBox.Yes)
        if reply == QW.QMessageBox.Yes or reply == None:
            for item in items:
                self.preview(item.data(QT.UserRole).replace('_tmb.', '_pre.'))

    def copyNameAction(self, items):
        data = []
        for item in items:
            data.append(os.path.basename(os.path.splitext(item.data(QT.UserRole))[0].replace('_tmb', '')))
        app.clipboard().setText('\n'.join(data), QG.QClipboard.Clipboard)

    def copyFolderLinkAction(self, items):
        data = []
        for item in items:
            data.append(os.path.dirname(item.data(QT.UserRole)))
        app.clipboard().setText('\n'.join(data), QG.QClipboard.Clipboard)

    def copyModelLinkAction(self, items):
        data = []
        for item in items:
            data.append(item.data(QT.UserRole).replace('_tmb.jpg', '.c4d'))
        app.clipboard().setText('\n'.join(data), QG.QClipboard.Clipboard)

    def fillModelList(self, path):
        count = 0
        self.modelsView.clear()
        for root, folders, files in os.walk(path):
            for file in files:
                if file.endswith('_tmb.jpg'):
                    link = os.path.join(root, file)
                    vName = os.path.basename(link).replace('_tmb.jpg', '').replace('_', ' ').title()
                    if len(vName) > 18:
                        item = QW.QListWidgetItem(vName[:16] + '...')
                    else:
                        item = QW.QListWidgetItem(vName)
                    item.setIcon(QG.QIcon(link))
                    item.setData(QT.UserRole, link)
                    self.modelsView.addItem(item)
                    count += 1
        self.updateStatus(count)

    def updateStatus(self, count):
        self.labelStatus.setText(f'Elements Count: {count}')

    def openRoot(self, event: QG.QMouseEvent):
        if self.labelRoot.text() != '...':
            self.openFolder(self.labelRoot.text())

    # def showInfo(self, items):
    #     if len(items) > 1:
    #         # self.infoPane.setText(f'Items count: {len(items)}\n' + '\n'.join([os.path.split(item.data(QT.UserRole))[1] for item in items]))
    #         self.infoPane.setText(f'Selected: {len(items)}\n' + '\n'.join([item.text() for item in items]))
    #     else:
    #         item = items[0]
    #         self.infoPane.setText('Name: ' + item.text() + f'\nFile Size: {os.stat(item.data(QT.UserRole).replace("_tmb.jpg", ".c4d")).st_size / 1048576}'[:17])
    #         self.previewImage.setPixmap(QG.QPixmap(item.data(QT.UserRole).replace("_tmb.", "_pre.")).scaledToWidth(220, QT.SmoothTransformation))

if __name__ == '__main__':
    app = QW.QApplication(sys.argv)

    # # Style
    with open('style.qss', 'rt') as style:
        app.setStyleSheet(style.read())

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
