import threading
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QSpinBox, QPushButton, QLabel, QStatusBar
)
from playwright.sync_api import sync_playwright
from humantyping import HumanTyper

CDP_URL = "http://localhost:9222"

class HumanTyperGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HumanTyper")
        self.setMinimumSize(500, 400)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        layout.addWidget(QLabel("Text to type:"))
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("Type something here...")
        layout.addWidget(self.text_input)

        wpm_row = QHBoxLayout()
        wpm_row.addWidget(QLabel("WPM:"))
        self.wpm_spin = QSpinBox()
        self.wpm_spin.setRange(20, 150)
        self.wpm_spin.setValue(70)
        wpm_row.addWidget(self.wpm_spin)
        wpm_row.addStretch()

        self.type_btn = QPushButton("Type!")
        self.type_btn.clicked.connect(self.start_typing)
        wpm_row.addWidget(self.type_btn)
        layout.addLayout(wpm_row)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def set_status(self, msg):
        self.status_bar.showMessage(msg)

    def start_typing(self):
        text = self.text_input.toPlainText().strip()
        if not text:
            self.set_status("Enter some text first.")
            return
        self.type_btn.setEnabled(False)
        wpm = self.wpm_spin.value()
        threading.Thread(target=self.do_type, args=(text, wpm), daemon=True).start()

    def do_type(self, text, wpm):
        self.set_status("Connecting to Chrome...")
        try:
            with sync_playwright() as p:
                browser = p.chromium.connect_over_cdp(CDP_URL)
                page = browser.contexts[0].pages[0]
                page.bring_to_front()
                for sel in ["[role='textbox']", ".kix-editor", "[contenteditable='true']", "textarea"]:
                    editor = page.locator(sel)
                    if editor.count():
                        self.set_status(f"Typing ({wpm} wpm)...")
                        editor.first.click()
                        HumanTyper(wpm=wpm).type_sync(editor.first, text)
                        self.set_status("Done!")
                        self.type_btn.setEnabled(True)
                        return
                self.set_status("No editable field found on current page.")
        except Exception as e:
            self.set_status(f"Error: {e}")
        self.type_btn.setEnabled(True)

if __name__ == "__main__":
    app = QApplication([])
    window = HumanTyperGUI()
    window.show()
    app.exec()
