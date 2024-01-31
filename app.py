import sys, re, json
import PyQt6.QtWidgets as QtWidgets

from PyQt6.QtCore import QSize, QProcess, Qt

progress_re = re.compile("Download Progress: (\d+)%")

def simple_percent_parser(output):
    """
    Matches lines using the progress_re regex,
    returning a single integer for the % progress.
    """
    m = progress_re.search(output)
    if m:
        pc_complete = m.group(1)
        return int(pc_complete)

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()

        items = {}
        with open("last_used_items.json", 'r') as f:
            items = json.load(f)
            f.close()

        self.setWindowTitle("RSS Feed Downloader")
        self.setFixedSize(QSize(500,400))

        self.feed_input = QtWidgets.QLineEdit()
        self.feed_input.setPlaceholderText("RSS Feed URL")
        self.feed_input.setText(items['url'])

        # === Destination folder section ===
        file_button = QtWidgets.QPushButton('Browse')
        file_button.setCheckable(True)
        file_button.clicked.connect(self.get_destination)

        self.file_input = QtWidgets.QLineEdit()
        self.file_input.setReadOnly(True)
        self.file_input.setText(items['path'])

        file_layout = QtWidgets.QHBoxLayout()
        file_layout.addWidget(file_button)
        file_layout.addWidget(self.file_input)
        # ===================================

        # === Start & Stop Button Section ===
        start_button = QtWidgets.QPushButton('Start')
        start_button.clicked.connect(self.start_process)

        stop_button = QtWidgets.QPushButton('Stop')
        stop_button.clicked.connect(self.stop_process)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(start_button)
        button_layout.addWidget(stop_button)
        # ====================================

        # === Progress Bar ===
        self.process = None
        self.progress = QtWidgets.QProgressBar()
        # self.progress.setFormat('Test') # This let's you set the interior bar text. Change to download speed eventually.
        self.progress.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress.setRange(0, 100)

        self.terminal_output = QtWidgets.QPlainTextEdit()
        self.terminal_output.setReadOnly(True)
        # ====================

        # === Layout Manager ===
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.feed_input)
        layout.addLayout(file_layout)
        layout.addLayout(button_layout)
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
            items = {
                "url": self.feed_input.text(),
                "path": self.file_input.text()
            }
            with open("last_used_items.json", 'w') as f:
                f.write(json.dumps(items, indent=4))
                f.close()

            self.process = QProcess()
            self.process.readyReadStandardOutput.connect(self.handle_stdout)
            self.process.readyReadStandardError.connect(self.handle_stderr)
            self.process.stateChanged.connect(self.handle_state)
            self.process.finished.connect(self.process_finished)
            self.process.start("python", ['main.py', self.feed_input.text(), self.file_input.text()])

    def handle_stderr(self):
        try:
            data = self.process.readAllStandardError()
            stderr = bytes(data).decode("utf8")

            # Extract progress if it is in the data.
            progress = simple_percent_parser(stderr)
            if progress:
                self.progress.setValue(progress)
        except:
            pass

        # self.update_terminal(stderr)

    def handle_stdout(self):
        data = self.process.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")
        self.update_terminal(stdout)

    def handle_state(self, state):
        states = {
            QProcess.ProcessState.NotRunning: '',
            QProcess.ProcessState.Starting: 'Starting Downloads',
            QProcess.ProcessState.Running: '',
        }
        state_name = states[state]
        self.update_terminal(f"{state_name}")

    def process_finished(self):
        self.update_terminal("Process finished.")
        self.process = None
    
    def stop_process(self):
        try:
            self.process.kill()
            self.update_terminal("Process stopped.")
            self.process = None
        except:
            pass

app = QtWidgets.QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()