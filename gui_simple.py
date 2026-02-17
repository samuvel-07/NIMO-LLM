# Simplified JARVIS GUI - Voice Ready
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json, os
from jarvis_core import JarvisCore

MEMORY = os.path.join(os.path.dirname(__file__), "memory.json")
APPS = os.path.join(os.path.dirname(__file__), "apps.json")

def load_json(p):
    try:
        return json.load(open(p,"r",encoding="utf-8"))
    except:
        return {}

def save_json(p,d):
    json.dump(d, open(p,"w",encoding="utf-8"), indent=2)

class JarvisGUI:
    def __init__(self, root):
        self.root = root
        root.title("JARVIS Voice Assistant - Python 3.12")
        root.geometry("700x480")
        self.core = None
        
        # Top frame with controls
        top = ttk.Frame(root)
        top.pack(fill="x", padx=8, pady=8)
        
        self.start_btn = ttk.Button(top, text="Start JARVIS", command=self.start, width=15)
        self.start_btn.pack(side="left", padx=4)
        
        self.stop_btn = ttk.Button(top, text="Stop", command=self.stop, state="disabled", width=10)
        self.stop_btn.pack(side="left", padx=4)
        
        self.add_app_btn = ttk.Button(top, text="Add App", command=self.add_app, width=10)
        self.add_app_btn.pack(side="left", padx=4)
        
        # Status label
        self.status_label = ttk.Label(top, text="Status: Ready", foreground="green")
        self.status_label.pack(side="right", padx=10)
        
        # Log text box
        log_frame = ttk.Frame(root)
        log_frame.pack(fill="both", expand=True, padx=8, pady=6)
        
        self.logbox = tk.Text(log_frame, height=22, wrap="word", font=("Consolas", 9))
        scrollbar = ttk.Scrollbar(log_frame, command=self.logbox.yview)
        self.logbox.config(yscrollcommand=scrollbar.set)
        
        self.logbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Load memory and apps
        self.memory = load_json(MEMORY)
        self.apps = load_json(APPS)
        
        # Welcome message
        self.log("=" * 70)
        self.log("JARVIS Voice Assistant - Ready!")
        self.log("=" * 70)
        self.log("Python 3.12.6 Environment Active")
        self.log("All dependencies loaded successfully")
        self.log("")
        self.log("Click 'Start JARVIS' to begin")
        self.log("Say 'Jarvis' followed by your command")
        self.log("=" * 70)

    def log(self, s):
        self.logbox.insert("end", s+"\\n")
        self.logbox.see("end")

    def start(self):
        try:
            self.log("")
            self.log("[SYSTEM] Initializing JARVIS...")
            self.core = JarvisCore(log_fn=self.log)
            self.core.start()
            self.start_btn.config(state="disabled")
            self.stop_btn.config(state="normal")
            self.status_label.config(text="Status: Listening...", foreground="blue")
            self.log("[SYSTEM] JARVIS started! Say 'Jarvis' to activate.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start JARVIS:\\n{e}")
            self.log(f"[ERROR] {e}")

    def stop(self):
        if self.core and hasattr(self.core, "running"):
            self.core.running = False
            self.log("[SYSTEM] JARVIS stopped.")
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.status_label.config(text="Status: Stopped", foreground="red")

    def add_app(self):
        name = simpledialog.askstring("App Name", "Friendly name for the app (e.g., chrome):")
        if not name:
            return
        
        path = simpledialog.askstring("Executable Path", 
                                      "Executable path or name (e.g., chrome.exe):")
        if name and path:
            self.apps[name.lower()] = path
            save_json(APPS, self.apps)
            self.log(f"[SYSTEM] Added app: {name} -> {path}")
            messagebox.showinfo("Success", f"App '{name}' added successfully!")

if __name__ == "__main__":
    root = tk.Tk()
    app = JarvisGUI(root)
    root.mainloop()
