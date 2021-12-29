from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import socket
import subprocess, platform
import threading


class Communicator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = "Data Communicator"
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setMinimumHeight(550)
        self.setMinimumWidth(635)
        # self.setMaximumHeight(250)
        # self.setMaximumWidth(335)

        # Layouts
        self.grid = QGridLayout()
        self.ipLayout = QHBoxLayout()
        self.verticleButtons = QVBoxLayout()

        self.verticleButtons.setAlignment(Qt.AlignTop)

        # Layout Properties
        self.ipLayout.addStretch(0)

        # Widgets
        self.labelIp = QLabel('IP')
        self.lineEditIP1 = QLineEdit()
        self.lineEditIP2 = QLineEdit()
        self.lineEditIP3 = QLineEdit()
        self.lineEditIP4 = QLineEdit()
        self.labelSocket = QLabel('SOCKET')
        self.textMsgLineEdt = QLineEdit()
        self.lineEditSocket = QLineEdit()
        self.btnConnect = QPushButton('Connect')
        self.btnTerminate = QPushButton('Terminate')
        self.btnSend = QPushButton('SEND')
        self.btnReceive = QPushButton('RECV')
        self.status = QPlainTextEdit()
        self.btnSendData = QPushButton("Data")
        self.btnSendVoice = QPushButton("Voice")

        # Widget Properties
        self.labelSocket.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        # self.lineEditIP1.setMaximumWidth(30)
        # self.lineEditIP2.setMaximumWidth(30)
        # self.lineEditIP3.setMaximumWidth(30)
        # self.lineEditIP4.setMaximumWidth(30)
        self.lineEditSocket.setMaximumWidth(100)
        self.status.setReadOnly(True)
        self.status.setPlainText('Ready...')
        self.btnTerminate.setEnabled(False)
        self.btnSend.setEnabled(False)
        self.btnReceive.setEnabled(False)
        self.btnConnect.setToolTip('Click to create a connection between 2 parties!')

        # TODO :: Delete later
        self.lineEditIP1.setText('127')
        self.lineEditIP2.setText('0')
        self.lineEditIP3.setText('0')
        self.lineEditIP4.setText('1')
        self.lineEditSocket.setText('65432')

        # Listeners
        self.btnConnect.clicked.connect(self.checkConnection)
        self.btnSend.clicked.connect(self.sendSelectFile)
        # self.btnReceive.clicked.connect(self.recvSelectFile)
        self.btnSendData.clicked.connect(self.sendDataBurst)
        self.btnSendVoice.clicked.connect(self.sendVoiceBurst)

        # Add to Sub-Layout
        self.ipLayout.addWidget(self.lineEditIP1)
        self.ipLayout.addWidget(QLabel('.'))
        self.ipLayout.addWidget(self.lineEditIP2)
        self.ipLayout.addWidget(QLabel('.'))
        self.ipLayout.addWidget(self.lineEditIP3)
        self.ipLayout.addWidget(QLabel('.'))
        self.ipLayout.addWidget(self.lineEditIP4)
        self.verticleButtons.addWidget(self.btnSendData)
        self.verticleButtons.addWidget(self.btnSendVoice)

        # Add to Grid Layout
        self.grid.addWidget(self.labelIp, 0, 0)
        self.grid.addLayout(self.ipLayout, 0, 1)
        self.grid.addWidget(self.labelSocket, 1, 0)
        self.grid.addWidget(self.lineEditSocket, 1, 1, 1, 2)
        self.grid.addWidget(self.btnConnect, 2, 0)
        self.grid.addWidget(self.textMsgLineEdt, 2, 1)
        # self.grid.addWidget(self.btnReceive, 2, 1)
        self.grid.addWidget(self.btnSend, 2, 2)
        self.grid.addWidget(self.status, 3, 0, 1, 2)
        self.grid.addLayout(self.verticleButtons, 3, 2)

        # Add main layout to main widget
        self.mainWidget = QWidget()
        self.mainWidget.setLayout(self.grid)
        self.setCentralWidget(self.mainWidget)
        self.show()

    def checkConnection(self):
        btnString = self.btnConnect.text()
        if btnString == 'Terminate':
            self.btnConnect.setText('Connect')
            self.btnSend.setEnabled(False)
            self.btnReceive.setEnabled(False)
            # self.self.thread_stop_flag = False
            # self.t._stop.set()
        else:
            self.btnConnect.setText('Terminate')
            self.btnSend.setEnabled(True)
            self.btnReceive.setEnabled(True)

            self.HOST = self.lineEditIP1.text() + '.' + \
                        self.lineEditIP2.text() + '.' + \
                        self.lineEditIP3.text() + '.' + \
                        self.lineEditIP4.text()

            self.PORT = int(self.lineEditSocket.text())

            self.status.setPlainText(
                self.status.toPlainText() + '\n' + 'Connecting to... (' + self.HOST + ' , ' + str(self.PORT) + ')' + '\n' + \
                'Please Wait! Waiting for a response...\n'
            )

            # Ping Host machine
            ping_output = self.pingHostJob(self.HOST)

            if not ping_output:
                self.status.setPlainText(
                    self.status.toPlainText() + 'Remote machine unresponsive...' + '\n'
                )
            else:
                self.status.setPlainText(
                    self.status.toPlainText() + 'Connected to remote machine...' + '\n'
                )
                self.setUpRecvDaemon()


    # def recvSelectFile(self):
    #     self.btnReceive.setEnabled(False)
    #     self.btnConnect.setEnabled(False)
    #     try:
    #         self.R()
    #     except:
    #         self.updateTextBox('Nothing to receive...!')
    #     self.btnReceive.setEnabled(True)
    #     self.btnConnect.setEnabled(True)

    def sendSelectFile(self):
        msgBx = QMessageBox()
        msgBx.setWindowTitle("Your options...")
        msgBx.setText("Do you want to send Text?\nSelect-\nYes - to send text\nNo - to sent file.")
        msgBx.addButton(QMessageBox.Yes)
        msgBx.addButton(QMessageBox.No)
        msgBx.addButton(QMessageBox.Cancel)
        reply = msgBx.exec_()
        if reply == QMessageBox.No:
            self.btnReceive.setEnabled(False)
            self.btnConnect.setEnabled(False)
            fname = QFileDialog.getOpenFileName(self, 'Open file...')
            if len(fname[0]) > 0:
                fn = str(fname[0])
                fn = fn[::-1]
                fileName = fn[:fn.index('/')][::-1]
                url = fn[fn.index('/'):][::-1]
                self.updateTextBox('Sending File...')
                self.updateTextBox(url + fileName)
                self.S(fileName, url, 'file')
                self.updateTextBox('File Sent!')
                self.btnReceive.setEnabled(True)
                self.btnConnect.setEnabled(True)
            else:
                self.btnReceive.setEnabled(True)
                self.btnConnect.setEnabled(True)
        elif reply == QMessageBox.Yes:
            self.S("", "", 'text_msg')

    def setUpRecvDaemon(self):
        self.thread_stop_flag = True
        self.t = threading.Thread(target=self.setUpRecvDaemonLooper, args=(self.HOST, self.PORT,))
        self.t.daemon = True
        self.t.start()

    def setUpRecvDaemonLooper(self, host, port):
        while self.thread_stop_flag:
            try:
                self.R(host, port)
            except:
                print("Nothing to receive. Please check connection.")

    def R(self, host, port):
        s = socket.socket()
        host = self.HOST
        port = 60000
        s.connect((host, port))
        data_type = (s.recv(1024)).decode('utf-8')
        if data_type == 'text_msg':
            msg = (s.recv(1024)).decode('utf-8')
            self.updateTextBox('Receiving Text Message... %s' % msg)
        else:
            filename = s.recv(1024)
            filename = filename.decode("utf-8")
            self.updateTextBox('Receiving File...' + filename)
            self.updateTextBox('Saving As...\nstorage-recv/' + filename)
            with open('storage-recv/' + filename, 'wb') as f:
                while True:
                    data = s.recv(1024)
                    if not data:
                        break
                    f.write(data)

            f.close()
            self.updateTextBox('File Saved!')
        s.close()

    def S(self, filename, URL, dataType): # self.S("", "", 'text_msg')
        port = 60000
        s = socket.socket()
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        host = '0.0.0.0'
        try:
            s.bind((host, port))
        except:
            print('Address already used!')

        s.listen(5)
        conn, addr = s.accept()
        if dataType == 'text_msg':
            conn.send(str.encode('text_msg'))
            # TODO :: Change here
            conn.send(str.encode(self.textMsgLineEdt.text()))
        else:
            status = True
            while status:
                # data = conn.recv(1024)
                conn.send(str.encode("file"))
                conn.send(str.encode(filename))
                f = open(URL + filename, 'rb')
                l = f.read(1024)
                while (l):
                    conn.send(l)
                    l = f.read(1024)
                f.close()

                status = False
            conn.close()


    def pingHostJob(self, HOST):
        ping_str = "-n 1" if platform.system().lower() == "windows" else "-c 1"
        args = "ping " + " " + ping_str + " " + HOST
        need_sh = False if platform.system().lower() == "windows" else True
        return ((subprocess.call(args, shell=need_sh) == 0))

    def updateTextBox(self, msg):
        self.status.setPlainText(
            self.status.toPlainText() + msg + '\n'
        )

    def sendDataBurst(self):
        for i in range(0, 5):
            self.S("", "", 'text_msg')

    def sendVoiceBurst(self):
        for i in range(0, 5):
            self.S("", "", 'text_msg')