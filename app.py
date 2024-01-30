import sys
import PyQt6.QtWidgets as QtWidgets
# import downloader

from PyQt6.QtCore import QSize, QProcess

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()

        # self.downloader = downloader.FileDownloader()

        self.setWindowTitle("RSS Feed Downloader")
        self.setFixedSize(QSize(400,300))

        self.feed_input = QtWidgets.QLineEdit()
        self.feed_input.setMaxLength(70)
        self.feed_input.setPlaceholderText("Put.io RSS Feed URL")

        # === Destination folder section ===
        file_button = QtWidgets.QPushButton('Browse')
        file_button.setCheckable(True)
        file_button.clicked.connect(self.get_destination)

        self.file_input = QtWidgets.QLineEdit()
        self.file_input.setReadOnly(True)

        file_layout = QtWidgets.QHBoxLayout()
        file_layout.addWidget(file_button)
        file_layout.addWidget(self.file_input)
        # ===================================

        self.process = None
        self.progress = QtWidgets.QProgressBar()
        self.progress.setRange(0, 100)

        start_button = QtWidgets.QPushButton('Start')
        start_button.clicked.connect(self.start_process)

        self.terminal_output = QtWidgets.QPlainTextEdit()
        self.terminal_output.setReadOnly(True)

        # === Layout Manager ===
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.feed_input)
        layout.addLayout(file_layout)
        layout.addWidget(start_button)
        layout.addWidget(self.progress)
        layout.addWidget(self.terminal_output)
        # ======================

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def get_destination(self):
        destination_folder = QtWidgets.QFileDialog.getExistingDirectory(None, 'Select Destination Folder')
        self.file_input.setText(destination_folder)
    
    def update_terminal(self, text):
        self.terminal_output.appendPlainText(text)
    
    def start_process(self):
        if self.process is None:
            # self.update_terminal("=== Starting Download ===")
            self.process = QProcess()
            self.process.readyReadStandardOutput.connect(self.handle_stdout)
            self.process.readyReadStandardError.connect(self.handle_stderr)
            self.process.stateChanged.connect(self.handle_state)
            self.process.finished.connect(self.process_finished)
            self.process.start("python", ['dummy_script.py'])

    def handle_stderr(self):
        data = self.process.readAllStandardError()
        stderr = bytes(data).decode("utf8")

        # # Extract progress if it is in the data.
        # progress = simple_percent_parser(stderr)
        # if progress:
        #     self.progress.setValue(progress)

        self.update_terminal(stderr)

    def handle_stdout(self):
        data = self.process.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")
        self.update_terminal(stdout)

    def handle_state(self, state):
        states = {
            QProcess.ProcessState.NotRunning: 'Not running',
            QProcess.ProcessState.Starting: 'Starting',
            QProcess.ProcessState.Running: 'Running',
        }
        state_name = states[state]
        self.update_terminal(f"State changed: {state_name}")

    def process_finished(self):
        self.update_terminal("Process finished.")
        self.process = None

app = QtWidgets.QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()