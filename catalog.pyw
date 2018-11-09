import os
import socket
import sqlite3
import subprocess
import sys
from collections import namedtuple

try:
    import hou
except ImportError:
    pass

try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *
    from PyQt5.QtGui import *
except ImportError:
    from PySide2.QtWidgets import *
    from PySide2.QtCore import *
    from PySide2.QtGui import *

ROOT = r'\\File-share\DATA\PROPS\C4D\MODELS'
DBFILE = r'\\File-share_new\system\HSITE\catalog.db'


class Application:
    Cinema4D = 0
    HoudiniFx = 1


def openFile(fileLink):
    if sys.platform.startswith('win'):
        os.startfile(fileLink)
    else:
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, fileLink])


def match(pattern, word):
    position = 0
    index = 0
    while index != len(pattern):
        try:
            new_position = word.index(pattern[index], position)
        except ValueError:
            return False
        index += 1
        position = new_position + 1
    return True


class SearchField(QComboBox):
    def __init__(self, parent=None):
        super(SearchField, self).__init__(parent)
        self.setEditable(True)
        completer = self.completer()
        completer.setCompletionMode(QCompleter.PopupCompletion)
        completer.setFilterMode(Qt.MatchContains)
        completer.setModelSorting(QCompleter.CaseInsensitivelySortedModel)
        completer.setMaxVisibleItems(5)
        popup = completer.popup()
        popup.setIconSize(QSize(64, 64))
        popup.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        clearAction = QAction('Clear', self)
        clearAction.setShortcut(QKeySequence(Qt.Key_Escape))
        clearAction.triggered.connect(lambda: self.clearEditText())
        self.addAction(clearAction)


class AssetList(QListWidget):
    def __init__(self, parent=None):
        super(AssetList, self).__init__(parent)
        self.setViewMode(QListView.IconMode)
        self.setResizeMode(QListView.Adjust)
        self.setDragDropMode(QAbstractItemView.NoDragDrop)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.verticalScrollBar().setSingleStep(30)
        self.setIconSize(QSize(120, 90))
        self.setUniformItemSizes(True)
        self.setContextMenuPolicy(Qt.CustomContextMenu)


def loadCinema4DAsset(path):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('127.0.0.1', 2900))
    sock.send(
        'Content-Length: 300\nEncoding: binary\nFilename: {0}\n'
        'Origin: Merge\nPassword: 7c9fb847d117531433435b68b61f91f6'.format(
            path).encode('ascii', 'ignore'))
    sock.close()


def loadHoudiniAsset(path):
    hou.hda.installFile(path)
    obj = hou.node('/obj')
    for definition in hou.hda.definitionsInFile(path):
        asset = definition.nodeTypeName()
        node = obj.createNode(asset)
        node.moveToGoodPosition()


class CatalogWidget(QWidget):
    def __init__(self, parent=None):
        super(CatalogWidget, self).__init__(parent)

        # Common
        self.setWindowTitle('Catalog 4')
        self.setMinimumSize(540, 160)
        self.resize(1300, 720)

        # Houdini
        self.setProperty("houdiniStyle", True)

        # UI
        self.statusBar = QStatusBar()

        self.searchBar = SearchField()
        self.searchBar.lineEdit().setPlaceholderText('Search...')
        self.searchBar.currentTextChanged.connect(self.filterAssets)

        self.assetList = AssetList()
        self.assetList.itemSelectionChanged.connect(self.updateStatus)
        self.assetList.customContextMenuRequested.connect(self.contextMenu)
        self.assetList.doubleClicked.connect(self.showAssetPreview)
        self.updateAssetList()

        updateAssetListAction = QAction('Update Asset List', self)
        updateAssetListAction.setShortcut(QKeySequence(Qt.Key_F5))
        updateAssetListAction.triggered.connect(self.updateAssetList)
        self.addAction(updateAssetListAction)

        searchAction = QAction('Search', self.assetList)
        searchAction.setShortcuts((QKeySequence('Ctrl+F'), QKeySequence('Alt+F'), QKeySequence(Qt.Key_F3)))
        searchAction.triggered.connect(self.doSearch)
        self.addAction(searchAction)

        # Layouts
        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.addWidget(self.searchBar)
        self.verticalLayout.addWidget(self.assetList)
        self.verticalLayout.addWidget(self.statusBar)

    def doSearch(self):
        self.searchBar.setFocus()
        self.searchBar.lineEdit().selectAll()

    def contextMenu(self):
        functions = {'Load': self.loadAsset,
                     'Open': self.openAsset,
                     'Open Folder': self.openAssetFolder,
                     'Preview': self.showAssetPreview,
                     'Copy Name': self.copyAssetName,
                     'Copy Folder Link': self.copyAssetFolderLink,
                     'Copy Model Link': self.copyAssetLink}
        if self.assetList.selectedItems():
            actions = ['Load',
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
                functions.get(reaction.text())()
            except AttributeError:
                pass

    def updateAssetList(self):
        try:
            with sqlite3.connect(DBFILE) as db:
                c = db.cursor()
                self.assetList.blockSignals(True)
                self.searchBar.blockSignals(True)
                self.assetList.clear()
                self.searchBar.clear()
                c.execute('SELECT * FROM Assets ORDER BY FILENAME ASC;')
                AssetDataItem = namedtuple('AssetDataItem',
                                           'ID NAME LABEL APPLICATION VERSION FOLDER'
                                           ' FILENAME PREVIEWFILE CLASS TAGS THUMBNAIL')
                for data in c.fetchall():
                    assetData = AssetDataItem(*data)._asdict()
                    tmb = QPixmap()
                    tmb.loadFromData(bytes(assetData.get('THUMBNAIL')))
                    icon = QIcon(tmb)
                    item = QListWidgetItem(icon, assetData.get('LABEL'), self.assetList)
                    item.setData(Qt.UserRole, assetData)
                    if len(assetData.get('LABEL')) > 18:
                        item.setToolTip(assetData.get('LABEL'))
                    self.searchBar.addItem(icon, assetData.get('LABEL'))
                self.assetList.blockSignals(False)
                self.searchBar.clearEditText()
                self.searchBar.blockSignals(False)
                self.updateStatus()
        except sqlite3.OperationalError:
            pass

    def loadAsset(self):
        reply = None
        items = self.assetList.selectedItems()
        if len(items) > 3:
            # noinspection PyTypeChecker
            reply = QMessageBox.question(self, 'Merge Operation',
                                         'Too many files ({0}). Would you like to merge all?'.format(len(items)),
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if reply == QMessageBox.Yes or reply is None:
            for item in items:
                assetData = item.data(Qt.UserRole)
                filename = os.path.join(assetData.get('FOLDER'), assetData.get('FILENAME'))
                if assetData.get('APPLICATION ') == Application.Cinema4D:
                    loadCinema4DAsset(filename)
                elif assetData.get('APPLICATION') == Application.HoudiniFx:
                    loadHoudiniAsset(filename)

    def openAsset(self):
        reply = None
        items = self.assetList.selectedItems()
        if len(items) > 3:
            # noinspection PyTypeChecker
            reply = QMessageBox.question(self, 'Open File Operation',
                                         'Too many files ({0}). Would you like to open all?'.format(len(items)),
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if reply == QMessageBox.Yes or reply is None:
            for item in items:
                assetData = item.data(Qt.UserRole)
                openFile(os.path.join(assetData.get('FOLDER'), assetData.get('FILENAME')))

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

    def openAssetFolder(self):
        reply = None
        items = self.assetList.selectedItems()
        if len(items) > 3:
            # noinspection PyTypeChecker
            reply = QMessageBox.question(self, 'Open Folder Operation',
                                         'Too many folders ({0}). Would you like to open all?'.format(len(items)),
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if reply == QMessageBox.Yes or reply is None:
            for item in items:
                self.openFolder(item.data(Qt.UserRole).get('FOLDER'))

    def showAssetPreview(self):
        reply = None
        items = self.assetList.selectedItems()
        if len(items) > 1:
            # noinspection PyTypeChecker
            reply = QMessageBox.question(self, 'Preview Operation',
                                         'Too many files ({0}). Would you like to preview all?'.format(len(items)),
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if reply == QMessageBox.Yes or reply is None:
            for item in items:
                openFile(item.data(Qt.UserRole).get('PREVIEWFILE'))

    def updateStatus(self):
        message = 'Assets: {0}'.format(self.assetList.count())
        selectedItems = self.assetList.selectedItems()
        if selectedItems:
            message += '    Selected: {0}'.format(len(selectedItems))
        self.statusBar.showMessage(message)

    def filterAssets(self):
        for item in (self.assetList.item(i) for i in range(self.assetList.count())):
            if match(self.searchBar.currentText().lower(), item.text().lower()):
                item.setHidden(False)
            else:
                item.setHidden(True)
                item.setSelected(False)

    def copyAssetLink(self):
        links = []
        items = self.assetList.selectedItems()
        for item in items:
            assetData = item.data(Qt.UserRole)
            links.append(os.path.join(assetData.get('FOLDER'), assetData.get('FILENAME')))
        app.clipboard().setText('\n'.join(links), QClipboard.Clipboard)

    def copyAssetName(self):
        names = []
        items = self.assetList.selectedItems()
        for item in items:
            names.append(item.data(Qt.UserRole).get('NAME'))
        app.clipboard().setText('\n'.join(names), QClipboard.Clipboard)

    def copyAssetFolderLink(self):
        folders = []
        items = self.assetList.selectedItems()
        for item in items:
            folders.append(item.data(Qt.UserRole).get('FOLDER'))
        app.clipboard().setText('\n'.join(folders), QClipboard.Clipboard)


def onCreateInterface():
    return CatalogWidget()


if __name__ == '__main__':
    def my_excepthook(type, value, tback):
        sys.__excepthook__(type, value, tback)


    sys.excepthook = my_excepthook

    app = QApplication(sys.argv)
    window = CatalogWidget()
    window.show()
    sys.exit(app.exec_())
