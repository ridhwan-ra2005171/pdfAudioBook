import pyttsx3
from PyPDF2 import PdfReader
from tkinter.filedialog import askopenfilename
import tkinter as tk

# Hide the root window
tk.Tk().withdraw()

# Ask user to select a PDF file
book = askopenfilename()

# Load the PDF
pdfReader = PdfReader(book)
pages = len(pdfReader.pages)
print(f"Total pages: {pages}")

# Initialize text-to-speech engine
speaker = pyttsx3.init()

# Read and speak each page
for num in range(pages):
    page = pdfReader.pages[num]
    text = page.extract_text()
    if text:  # Make sure text is not None
        speaker.say(text)
        speaker.runAndWait()
