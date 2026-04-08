# src/gui/app.py
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import threading
import sys
from pathlib import Path
from io import StringIO

# Add project root for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.main import run_pipeline

class PipelineGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Data Pipeline Controller")
        self.root.geometry("700x500")
        
        self.output_dir = None
        self.create_widgets()
    
    def create_widgets(self):
        # Top frame with controls
        control_frame = ttk.Frame(self.root)
        control_frame.pack(pady=10, padx=10, fill=tk.X)
        
        # Output directory selection
        ttk.Label(control_frame, text="Output Directory:").pack(side=tk.LEFT, padx=5)
        self.dir_var = tk.StringVar(value=str(Path("data/processed").absolute()))
        ttk.Entry(control_frame, textvariable=self.dir_var, width=40).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Browse...", command=self.browse_output).pack(side=tk.LEFT)
        
        # Run button
        self.run_btn = ttk.Button(control_frame, text="Run Pipeline", command=self.start_pipeline)
        self.run_btn.pack(side=tk.RIGHT, padx=5)
        
        # Log output area
        log_frame = ttk.LabelFrame(self.root, text="Pipeline Log")
        log_frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        
        self.log_area = scrolledtext.ScrolledText(
            log_frame, height=20, width=80, wrap=tk.WORD
        )
        self.log_area.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
        
        # Bottom status bar
        self.status = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN)
        self.status.pack(side=tk.BOTTOM, fill=tk.X)
    
    def browse_output(self):
        directory = filedialog.askdirectory()
        if directory:
            self.dir_var.set(directory)
    
    def start_pipeline(self):
        """Run pipeline in background thread"""
        self.run_btn.config(state=tk.DISABLED)
        self.status.config(text="Running...")
        self.log("Starting pipeline...")
        
        self.output_dir = Path(self.dir_var.get())
        
        thread = threading.Thread(target=self._run_pipeline_thread)
        thread.daemon = True
        thread.start()
    
    def _run_pipeline_thread(self):
        """Actual pipeline execution"""
        # Capture stdout to display in GUI
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        
        try:
            results = run_pipeline(output_dir=self.output_dir)
            output = sys.stdout.getvalue()
            self.log(output)
            self.log("Pipeline completed successfully!")
            self.log(f"Output saved to: {results['processed_data']}")
            messagebox.showinfo("Success", "Pipeline completed successfully!")
        except Exception as e:
            self.log(f"ERROR: {e}")
            messagebox.showerror("Error", str(e))
        finally:
            sys.stdout = old_stdout
            self.root.after(0, self._finish_pipeline)
    
    def _finish_pipeline(self):
        """Reset UI after pipeline completes"""
        self.run_btn.config(state=tk.NORMAL)
        self.status.config(text="Ready")
    
    def log(self, message):
        """Add message to log area"""
        def _log():
            self.log_area.insert(tk.END, str(message) + "\n")
            self.log_area.see(tk.END)
        self.root.after(0, _log)
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = PipelineGUI()
    app.run()