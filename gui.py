# gui.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json, os
from jarvis_core import JarvisCore
from voice_auth import audio_to_mfcc_mean, load_voice_db
from pathlib import Path

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
        root.title("Jarvis Pro")
        root.geometry("700x480")
        self.core = JarvisCore(log_fn=self.log)
        # top frame
        top = ttk.Frame(root); top.pack(fill="x", padx=8, pady=8)
        self.start_btn = ttk.Button(top, text="Start", command=self.start)
        self.start_btn.pack(side="left", padx=4)
        self.stop_btn = ttk.Button(top, text="Stop", command=self.stop, state="disabled")
        self.stop_btn.pack(side="left", padx=4)
        self.enroll_btn = ttk.Button(top, text="Enroll Voice", command=self.enroll_voice)
        self.enroll_btn.pack(side="left", padx=4)
        self.toggle_btn = ttk.Button(top, text="Toggle Voice Auth", command=self.toggle_voice_auth)
        self.toggle_btn.pack(side="left", padx=4)
        self.add_app_btn = ttk.Button(top, text="Add App", command=self.add_app)
        self.add_app_btn.pack(side="left", padx=4)
        self.train_btn = ttk.Button(top, text="Train Commands (record)", command=self.train_commands)
        self.train_btn.pack(side="left", padx=4)
        # logs
        self.logbox = tk.Text(root, height=22)
        self.logbox.pack(fill="both", expand=True, padx=8, pady=6)
        self.memory = load_json(MEMORY)
        self.apps = load_json(APPS)

    def log(self, s):
        self.logbox.insert("end", s+"\n"); self.logbox.see("end")

    def start(self):
        self.core = JarvisCore(log_fn=self.log)
        self.core.start()
        self.start_btn.config(state="disabled"); self.stop_btn.config(state="normal")

    def stop(self):
        if hasattr(self.core, "running"):
            self.core.running = False
        self.start_btn.config(state="normal"); self.stop_btn.config(state="disabled")

    def enroll_voice(self):
        # simple enroll flow using command line helper (or you can call enroll_profile)
        import speech_recognition as sr
        r = sr.Recognizer()
        samples = simpledialog.askinteger("Enroll", "How many samples (3-6)?", initialvalue=3, minvalue=1, maxvalue=10)
        if not samples: return
        name = simpledialog.askstring("Profile name", "Name of profile:", initialvalue="owner")
        if not name: return
        self.log(f"Enroll {name} samples={samples}. Say wake word 'jarvis' when prompted.")
        from voice_auth import audio_to_mfcc_mean, enroll_profile
        mfccs=[]
        with sr.Microphone() as source:
            for i in range(samples):
                r.adjust_for_ambient_noise(source, duration=0.4)
                self.log(f"Speak sample {i+1}/{samples} now...")
                audio = r.listen(source, timeout=6, phrase_time_limit=3)
                mf = audio_to_mfcc_mean(audio)
                if mf is not None:
                    mfccs.append(mf)
                    self.log("Sample saved.")
                else:
                    self.log("Sample failed.")
        if mfccs:
            enroll_profile(name, mfccs)
            messagebox.showinfo("Enroll", "Profile saved.")
        else:
            messagebox.showerror("Enroll", "No good samples recorded.")

    def toggle_voice_auth(self):
        self.memory = load_json(MEMORY)
        self.memory["voice_auth_enabled"] = not self.memory.get("voice_auth_enabled", False)
        save_json(MEMORY, self.memory)
        self.log("Voice auth set to " + str(self.memory["voice_auth_enabled"]))

    def add_app(self):
        name = simpledialog.askstring("App name", "Friendly name for the app (like chrome)")
        path = simpledialog.askstring("Executable/path", "Executable path or exe name (e.g., chrome.exe)")
        if name and path:
            self.apps[name]=path
            save_json(APPS, self.apps)
            self.log(f"Added app {name} -> {path}")

    def train_commands(self):
        # launch training script (commands_trainer.py) as module or instruct user
        messagebox.showinfo("Train", "Training helper launched in terminal. Follow prompts there.")
        import subprocess, sys
        subprocess.Popen([sys.executable, os.path.join(os.path.dirname(__file__), "commands_trainer.py")])

if __name__ == "__main__":
    root = tk.Tk()
    app = JarvisGUI(root)
    root.mainloop()
