import sys
import os
import subprocess
import socket

try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *
    from PyQt5.QtGui import *
except ImportError:
    from PySide2.QtWidgets import *
    from PySide2.QtCore import *
    from PySide2.QtGui import *

ROOT = r'\\File-share\DATA\PROPS\C4D\MODELS'
EXTENSION = '.c4d'


def openFile(fileLink):
    if sys.platform.startswith('win'):
        os.startfile(fileLink)
    else:
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, fileLink])


def copyNameAction(items):
    names = []
    for item in items:
        names.append(os.path.basename(os.path.splitext(item.data(Qt.UserRole))[0].replace('_tmb', '')))
    app.clipboard().setText('\n'.join(names), QClipboard.Clipboard)


def copyFolderLinkAction(items):
    folders = []
    for item in items:
        folders.append(os.path.dirname(item.data(Qt.UserRole)))
    app.clipboard().setText('\n'.join(folders), QClipboard.Clipboard)


def copyModelLinkAction(items):
    links = []
    for item in items:
        links.append(item.data(Qt.UserRole).replace('_tmb.jpg', EXTENSION))
    app.clipboard().setText('\n'.join(links), QClipboard.Clipboard)


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        # Common
        self.widget = QWidget(self)
        self.setCentralWidget(self.widget)
        self.setWindowTitle('QCatalog')
        self.setMinimumSize(540, 160)
        self.resize(800, 600)

        # Visual Elements
        self.buttonHelp = QPushButton('Help')
        self.buttonHelp.setFixedSize(80, 25)
        self.buttonHelp.clicked.connect(self.buttonHelp_click)

        self.labelRoot = QLabel('...')
        self.labelRoot.setCursor(Qt.PointingHandCursor)
        self.labelRoot.setToolTip('Open Folder')
        self.labelRoot.setAlignment(Qt.AlignCenter)
        self.labelRoot.mousePressEvent = self.openRoot

        self.previewSize = QSlider(Qt.Horizontal)
        self.previewSize.setFixedWidth(100)
        self.previewSize.setRange(10, 100)
        self.previewSize.setValue(100)
        self.previewSize.valueChanged.connect(self.changePreviewSize)

        self.treeView = QTreeWidget()
        self.treeView.setFixedWidth(200)
        self.treeView.header().hide()
        self.treeView.setCursor(Qt.PointingHandCursor)
        self.treeView.itemClicked.connect(self.treeItem_click)

        self.modelsView = QListWidget(self.widget)
        self.modelsView.setViewMode(QListView.IconMode)
        self.modelsView.setResizeMode(QListView.Adjust)
        self.modelsView.setDragDropMode(QAbstractItemView.NoDragDrop)
        self.modelsView.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.modelsView.setIconSize(QSize(120, 90))
        self.modelsView.setSpacing(2)
        self.modelsView.setUniformItemSizes(True)
        self.modelsView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.modelsView.customContextMenuRequested.connect(self.contextMenu)
        self.modelsView.doubleClicked.connect(lambda: self.previewAction(self.modelsView.selectedItems()))

        self.statusBar().show()

        # Layouts
        self.horizontalLayoutTop = QHBoxLayout()
        self.horizontalLayoutTop.setContentsMargins(4, 4, 4, 2)
        self.horizontalLayoutBottom = QHBoxLayout()
        self.horizontalLayoutBottom.setContentsMargins(4, 2, 4, 4)
        self.verticalLayout = QVBoxLayout(self.widget)
        self.verticalLayout.setSpacing(4)
        self.verticalLayout.setContentsMargins(4, 4, 4, 0)
        self.verticalLayout.addLayout(self.horizontalLayoutTop)
        self.verticalLayout.addLayout(self.horizontalLayoutBottom)

        self.horizontalLayoutTop.addWidget(self.buttonHelp)
        self.horizontalLayoutTop.addWidget(self.labelRoot)
        self.horizontalLayoutTop.addWidget(self.previewSize)

        self.horizontalLayoutBottom.addWidget(self.treeView)
        self.horizontalLayoutBottom.addWidget(self.modelsView)

        # Initialization
        self.treeInit()

    def buttonHelp_click(self):
        QMessageBox.information(self, 'Help', ('Navigation: Arrows, Home, End, Page Up, Page Down\n'
                                               'Selection: Mouse + Ctrl or Shift, Ctrl + A\n'
                                               'Import: Context Menu > Merge\n'
                                               'Preview: Double LMB click, Context Menu > Preview'))

    def treeInit(self):
        root = self.treeView.invisibleRootItem()
        tree = {
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
        allItem = QTreeWidgetItem()
        allItem.setText(0, 'All')
        allItem.setData(0, Qt.UserRole, ROOT)
        root.addChild(allItem)
        for key, value in tree.items():
            upItem = QTreeWidgetItem()
            upItem.setText(0, key)
            upItem.setData(0, Qt.UserRole, os.path.join(ROOT, key))
            root.addChild(upItem)
            upItem.setExpanded(True)
            upItem.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            if value:
                for i in value:
                    downItem = QTreeWidgetItem()
                    downItem.setText(0, i)
                    downItem.setData(0, Qt.UserRole, os.path.join(ROOT, key, i.replace(' ', '_')))
                    downItem.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                    upItem.addChild(downItem)

    def treeItem_click(self, item):
        path = item.data(0, Qt.UserRole)
        self.labelRoot.setText(path)
        self.fillModelList(path)

    def contextMenu(self):
        functions = {'Merge': self.mergeAction,
                     'Open': self.openFileAction,
                     'Open Folder': self.openFolderAction,
                     'Preview': self.previewAction,
                     'Copy Name': copyNameAction,
                     'Copy Folder Link': copyFolderLinkAction,
                     'Copy Model Link': copyModelLinkAction}
        if self.modelsView.selectedItems():
            actions = ['Merge',
                       'Open',
                       'Open Folder',
                       '-',
                       'Preview',
                       '-',
                       'Copy Name',
                       'Copy Folder Link',
                       'Copy Model Link']
            menu = QMenu()
            for a in actions:
                if a != '-':
                    menu.addAction(QAction(a, self))
                else:
                    menu.addSeparator()
            try:
                reaction = menu.exec_(QCursor().pos())
                functions.get(reaction.text())(self.modelsView.selectedItems())
            except AttributeError:
                pass

    def mergeAction(self, items):
        reply = None
        if len(items) > 3:
            reply = QMessageBox.question(self, 'Merge Operation',
                                         f'Too many files ({len(items)}). Would you like to merge all?',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if reply == QMessageBox.Yes or reply is None:
            for item in items:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect(('127.0.0.1', 2900))
                link = item.data(Qt.UserRole).replace('_tmb.jpg', '.c4d')
                sock.send(
                    f'Content-Length: 300\nEncoding: binary\nFilename: {link}\nOrigin: Merge\nPassword: '
                    f'7c9fb847d117531433435b68b61f91f6'.encode(
                        'ascii', 'ignore'))
                sock.close()

    def openFileAction(self, items):
        reply = None
        if len(items) > 3:
            reply = QMessageBox.question(self, 'Open File Operation',
                                         f'Too many files ({len(items)}). Would you like to open all?',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if reply == QMessageBox.Yes or reply is None:
            for item in items:
                openFile(item.data(Qt.UserRole).replace('_tmb.jpg', '.c4d'))

    def openFolder(self, folderLink):
        if sys.platform.startswith('win'):
            os.startfile(folderLink)
        elif sys.platform == 'darwin':
            subprocess.Popen(['open', folderLink])
        elif sys.platform.startswith('linux'):
            try:
                subprocess.Popen(['xdg-open', folderLink])  # Gnome, KDE, Xfce
            except OSError:
                QMessageBox.warning(self, 'Unknown OS', "Can't open folder on this OS!")
        else:
            QMessageBox.warning(self, 'Unknown OS', "Can't open folder on this OS!")

    def openFolderAction(self, items):
        reply = None
        if len(items) > 3:
            reply = QMessageBox.question(self, 'Open Folder Operation',
                                         f'Too many folders ({len(items)}). Would you like to open all?',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if reply == QMessageBox.Yes or reply is None:
            for item in items:
                self.openFolder(os.path.dirname(item.data(Qt.UserRole)))

    def previewAction(self, items):
        reply = None
        if len(items) > 1:
            reply = QMessageBox.question(self, 'Preview Operation',
                                         f'Too many files ({len(items)}). Would you like to preview all?',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if reply == QMessageBox.Yes or reply is None:
            for item in items:
                openFile(item.data(Qt.UserRole).replace('_tmb.', '_pre.'))

    def fillModelList(self, path):
        count = 0
        self.modelsView.clear()
        for root, folders, files in os.walk(path):
            for file in files:
                if file.endswith('_tmb.jpg'):
                    link = os.path.join(root, file)
                    name = os.path.basename(link).replace('_tmb.jpg', '').replace('_', ' ').title()
                    item = QListWidgetItem(name)
                    if len(name) > 18:
                        item.setToolTip(name)
                    item.setIcon(QIcon(link))
                    item.setData(Qt.UserRole, link)
                    self.modelsView.addItem(item)
                    count += 1
        self.updateStatus(count)

    def updateStatus(self, count):
        self.statusBar().showMessage(f'Elements Count: {count}')

    def openRoot(self, event):
        if self.labelRoot.text() != '...' and event.button() == Qt.LeftButton:
            self.openFolder(self.labelRoot.text())

    def changePreviewSize(self, value):
        self.modelsView.setIconSize(QSize(value/100 * 120, value/100 * 90))
        self.previewSize.setToolTip(str(value))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
