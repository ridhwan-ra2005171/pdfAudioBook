import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import PyPDF2
import pyttsx3
import threading
import os
from tkinter import PhotoImage


class PDFReaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF to Speech Reader")
        self.root.geometry("600x500")
        self.root.configure(bg="#f0f0f0")
        self.root.resizable(True, True)
        
        # Set minimum window size
        self.root.minsize(500, 400)
        
        # PDF reading variables
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)
        self.voice_rate = 150
        self.is_paused = False
        self.is_reading = False
        self.stop_reading = False
        self.pdf_text = ""
        self.current_page = 0
        self.total_pages = 0
        self.filename = ""
        
        # Create main frames
        self.create_frames()
        self.create_menu()
        self.create_widgets()
        
        # Set default voice
        voices = self.engine.getProperty('voices')
        if voices:
            self.voice_var = tk.StringVar(value="Default")
            self.available_voices = {"Default": voices[0].id}
            
            # Add all available voices
            for voice in voices:
                name = f"{voice.name} ({voice.languages[0] if voice.languages else 'Unknown'})"
                self.available_voices[name] = voice.id
        
        # Center window on screen
        self.center_window()
        
    def center_window(self):
        """Center the window on the screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_frames(self):
        # Header frame
        self.header_frame = tk.Frame(self.root, bg="#3498db", height=60)
        self.header_frame.pack(fill=tk.X)
        
        # Title
        tk.Label(self.header_frame, text="PDF to Speech Reader", 
                 font=("Helvetica", 18, "bold"), bg="#3498db", fg="white").pack(pady=10)
        
        # Main content frame
        self.content_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Left side - controls
        self.controls_frame = tk.LabelFrame(self.content_frame, text="Controls", bg="#f0f0f0", font=("Helvetica", 10))
        self.controls_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10), pady=10)
        
        # Right side - preview
        self.preview_frame = tk.LabelFrame(self.content_frame, text="PDF Preview", bg="#f0f0f0", font=("Helvetica", 10))
        self.preview_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=10)
        
        # Status bar
        self.status_frame = tk.Frame(self.root, bg="#e0e0e0", height=25)
        self.status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        self.status_label = tk.Label(self.status_frame, text="Ready", bg="#e0e0e0", anchor=tk.W)
        self.status_label.pack(fill=tk.X, padx=5)
    
    def create_menu(self):
        menu_bar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Open PDF", command=self.load_pdf)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)
        
        # Settings menu
        settings_menu = tk.Menu(menu_bar, tearoff=0)
        
        # Voice submenu
        voice_menu = tk.Menu(settings_menu, tearoff=0)
        if hasattr(self, 'available_voices'):
            self.voice_var = tk.StringVar(value="Default")
            for voice_name in self.available_voices:
                voice_menu.add_radiobutton(label=voice_name, variable=self.voice_var, 
                                          value=voice_name, command=self.change_voice)
        settings_menu.add_cascade(label="Voice", menu=voice_menu)
        
        # Help menu
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="Help", command=self.show_help)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        
        menu_bar.add_cascade(label="Settings", menu=settings_menu)
        self.root.config(menu=menu_bar)
    
    def create_widgets(self):
        # File selection section
        file_frame = tk.Frame(self.controls_frame, bg="#f0f0f0")
        file_frame.pack(fill=tk.X, pady=10)
        
        self.file_label = tk.Label(file_frame, text="No file selected", bg="#f0f0f0", anchor=tk.W, 
                                  font=("Helvetica", 9))
        self.file_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        select_btn = ttk.Button(file_frame, text="Select PDF", command=self.load_pdf)
        select_btn.pack(side=tk.RIGHT, padx=5)
        
        # Voice rate control
        rate_frame = tk.Frame(self.controls_frame, bg="#f0f0f0")
        rate_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(rate_frame, text="Speech Rate:", bg="#f0f0f0").pack(side=tk.LEFT, padx=5)
        
        self.rate_var = tk.IntVar(value=150)
        rate_scale = ttk.Scale(rate_frame, from_=50, to=300, variable=self.rate_var, 
                              orient=tk.HORIZONTAL, command=self.update_rate)
        rate_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.rate_label = tk.Label(rate_frame, text="150", width=3, bg="#f0f0f0")
        self.rate_label.pack(side=tk.RIGHT, padx=5)
        
        # Page navigation
        page_frame = tk.Frame(self.controls_frame, bg="#f0f0f0")
        page_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(page_frame, text="Page:", bg="#f0f0f0").pack(side=tk.LEFT, padx=5)
        
        self.page_var = tk.StringVar(value="0/0")
        tk.Label(page_frame, textvariable=self.page_var, bg="#f0f0f0").pack(side=tk.LEFT, padx=5)
        
        self.prev_btn = ttk.Button(page_frame, text="Previous", command=self.prev_page, state="disabled")
        self.prev_btn.pack(side=tk.LEFT, padx=5)
        
        self.next_btn = ttk.Button(page_frame, text="Next", command=self.next_page, state="disabled")
        self.next_btn.pack(side=tk.LEFT, padx=5)
        
        # Control buttons with modern styling
        buttons_frame = tk.Frame(self.controls_frame, bg="#f0f0f0")
        buttons_frame.pack(fill=tk.X, pady=10)
        
        style = ttk.Style()
        style.configure("Play.TButton", foreground="green")
        style.configure("Pause.TButton", foreground="orange")
        style.configure("Stop.TButton", foreground="red")
        
        self.start_btn = ttk.Button(buttons_frame, text="▶ Play", style="Play.TButton",
                                   command=self.start_resume, state="disabled", width=12)
        self.start_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.pause_btn = ttk.Button(buttons_frame, text="⏸ Pause", style="Pause.TButton",
                                   command=self.pause, state="disabled", width=12)
        self.pause_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.stop_btn = ttk.Button(buttons_frame, text="⏹ Stop", style="Stop.TButton",
                                  command=self.stop, state="disabled", width=12)
        self.stop_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # PDF Preview
        self.text_preview = tk.Text(self.preview_frame, wrap=tk.WORD, height=15, width=40, 
                                   font=("Helvetica", 10))
        self.text_preview.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add scrollbar to the preview
        preview_scroll = ttk.Scrollbar(self.text_preview, command=self.text_preview.yview)
        preview_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_preview.config(yscrollcommand=preview_scroll.set)
        
        # Make text preview read-only
        self.text_preview.config(state=tk.DISABLED)
    
    def load_pdf(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if not file_path:
            return
        
        try:
            self.reader = PyPDF2.PdfReader(file_path)
            self.total_pages = len(self.reader.pages)
            self.filename = os.path.basename(file_path)
            
            # Update file label with filename
            self.file_label.config(text=f"File: {self.filename}")
            
            # Reset to first page
            self.current_page = 0
            self.page_var.set(f"1/{self.total_pages}")
            
            # Enable buttons
            self.start_btn.config(state="normal")
            self.pause_btn.config(state="disabled")
            self.stop_btn.config(state="normal")
            
            if self.total_pages > 1:
                self.next_btn.config(state="normal")
            
            # Reset reading states
            self.stop_reading = False
            self.is_reading = False
            self.is_paused = False
            
            # Display first page preview
            self.display_page(0)
            
            # Update status
            self.status_label.config(text=f"Loaded {self.filename} with {self.total_pages} pages")
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not open PDF file: {str(e)}")
    
    def display_page(self, page_num):
        """Display the specified page in the preview"""
        if not hasattr(self, 'reader') or page_num >= self.total_pages:
            return
        
        try:
            page = self.reader.pages[page_num]
            text = page.extract_text() or "No text could be extracted from this page."
            
            # Update text preview
            self.text_preview.config(state=tk.NORMAL)
            self.text_preview.delete(1.0, tk.END)
            self.text_preview.insert(tk.END, text)
            self.text_preview.config(state=tk.DISABLED)
            
            # Update page navigation
            self.current_page = page_num
            self.page_var.set(f"{page_num + 1}/{self.total_pages}")
            
            # Update button states
            self.prev_btn.config(state="normal" if page_num > 0 else "disabled")
            self.next_btn.config(state="normal" if page_num < self.total_pages - 1 else "disabled")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error displaying page: {str(e)}")
    
    def next_page(self):
        """Navigate to the next page"""
        if self.current_page < self.total_pages - 1:
            self.display_page(self.current_page + 1)
    
    def prev_page(self):
        """Navigate to the previous page"""
        if self.current_page > 0:
            self.display_page(self.current_page - 1)
    
    def read_text(self):
        """Read the PDF text aloud"""
        if not hasattr(self, 'reader'):
            return
        
        try:
            # Start from current page
            for page_num in range(self.current_page, self.total_pages):
                if self.stop_reading:
                    break
                    
                # Update UI to show current page
                self.root.after(0, lambda p=page_num: self.display_page(p))
                
                page = self.reader.pages[page_num]
                text = page.extract_text()
                
                if not text:
                    continue
                
                # Read paragraphs
                for paragraph in text.split('\n\n'):
                    if self.stop_reading:
                        break
                        
                    # Handle pausing
                    while self.is_paused and not self.stop_reading:
                        self.root.update()  # Keep UI responsive
                        import time
                        time.sleep(0.1)
                        
                    if not self.stop_reading:
                        self.engine.say(paragraph)
                        self.engine.runAndWait()
            
            # Reset state after reading is complete
            if not self.stop_reading:
                self.is_reading = False
                self.start_btn.config(text="▶ Play")
                self.status_label.config(text="Reading complete")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error while reading: {str(e)}")
            self.stop()
    
    def start_resume(self):
        """Start or resume reading"""
        if not hasattr(self, 'reader'):
            messagebox.showinfo("Notice", "Please select a PDF file first")
            return
            
        if not self.is_reading:
            self.stop_reading = False
            self.is_paused = False
            self.is_reading = True
            self.start_btn.config(text="⏸ Pause")
            self.pause_btn.config(state="normal")
            self.status_label.config(text=f"Reading page {self.current_page + 1}/{self.total_pages}")
            
            # Start reading in a separate thread to keep UI responsive
            threading.Thread(target=self.read_text, daemon=True).start()
        else:
            # Toggle between pause and resume
            if self.is_paused:
                self.is_paused = False
                self.start_btn.config(text="⏸ Pause")
                self.status_label.config(text="Resumed reading")
            else:
                self.is_paused = True
                self.start_btn.config(text="▶ Resume")
                self.status_label.config(text="Paused")
    
    def pause(self):
        """Pause reading"""
        if self.is_reading and not self.is_paused:
            self.is_paused = True
            self.start_btn.config(text="▶ Resume")
            self.status_label.config(text="Paused")
    
    def stop(self):
        """Stop reading"""
        self.stop_reading = True
        self.engine.stop()
        self.is_reading = False
        self.is_paused = False
        self.start_btn.config(text="▶ Play")
        self.status_label.config(text="Stopped")
    
    def update_rate(self, event=None):
        """Update the speech rate"""
        rate = self.rate_var.get()
        self.rate_label.config(text=str(rate))
        self.engine.setProperty('rate', rate)
    
    def change_voice(self):
        """Change the voice of the speech engine"""
        voice_name = self.voice_var.get()
        if voice_name in self.available_voices:
            voice_id = self.available_voices[voice_name]
            self.engine.setProperty('voice', voice_id)
            self.status_label.config(text=f"Voice changed to {voice_name}")
    
    def show_about(self):
        """Show about dialog"""
        messagebox.showinfo("About PDF to Audio Reader", 
                           "PDF to Speech Reader\nVersion 1.0\n\nA tool to read PDF documents aloud.",
                           "\n\nCopyright © 2025 Ridhwan Athaullah\nAll rights reserved."
                           )
    
    def show_help(self):
        """Show help dialog"""
        helptext = """
PDF to Speech Reader Help

1. Click 'Select PDF' to open a PDF file
2. Use 'Next' and 'Previous' to navigate pages
3. Click 'Play' to start reading the current page
4. Use 'Pause' to pause reading
5. Use 'Stop' to end reading

You can adjust the speech rate with the slider.
Different voices can be selected in the Settings menu.
        """
        messagebox.showinfo("Help", helptext)


if __name__ == "__main__":
    root = tk.Tk()
    app = PDFReaderApp(root)
    root.mainloop()
