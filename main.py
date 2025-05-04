import tkinter as tk
from tkinter import filedialog
import pyttsx3
import PyPDF2
import threading

class PDFReaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF to Speech Reader")
        self.root.geometry("300x200")

        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)

        self.is_paused = False
        self.is_reading = False
        self.stop_reading = False

        self.pdf_text = ""

        tk.Button(root, text="Select PDF", command=self.load_pdf).pack(pady=10)
        self.start_btn = tk.Button(root, text="Start/Resume", command=self.start_resume, state="disabled")
        self.start_btn.pack(pady=5)

        self.pause_btn = tk.Button(root, text="Pause", command=self.pause, state="disabled")
        self.pause_btn.pack(pady=5)

        self.stop_btn = tk.Button(root, text="End", command=self.stop, state="disabled")
        self.stop_btn.pack(pady=5)

    def load_pdf(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if not file_path:
            return
        reader = PyPDF2.PdfReader(file_path)
        self.pdf_text = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                self.pdf_text += text + "\n"
        self.start_btn.config(state="normal")
        self.pause_btn.config(state="normal")
        self.stop_btn.config(state="normal")
        self.stop_reading = False
        print("PDF loaded successfully.")

    def read_text(self):
        for line in self.pdf_text.splitlines():
            if self.stop_reading:
                break
            while self.is_paused:
                self.engine.stop()
            self.engine.say(line)
            self.engine.runAndWait()

    def start_resume(self):
        if not self.is_reading:
            self.stop_reading = False
            self.is_paused = False
            self.is_reading = True
            threading.Thread(target=self.read_text).start()
        else:
            self.is_paused = False

    def pause(self):
        self.is_paused = True

    def stop(self):
        self.stop_reading = True
        self.engine.stop()
        self.is_reading = False
        self.is_paused = False

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFReaderApp(root)
    root.mainloop()
