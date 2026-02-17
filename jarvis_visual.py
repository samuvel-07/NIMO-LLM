"""
JARVIS Visual Interface
Modern GUI with particle animation and transparent background
"""

import tkinter as tk
from tkinter import ttk
import threading
import math
import random
from jarvis_core import JarvisCore

class Particle:
    """Individual particle in the cluster"""
    def __init__(self, canvas_width, canvas_height):
        self.x = random.uniform(0, canvas_width)
        self.y = random.uniform(0, canvas_height)
        self.vx = random.uniform(-0.5, 0.5)
        self.vy = random.uniform(-0.5, 0.5)
        self.size = random.randint(1, 3)
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        
    def update(self):
        """Update particle position"""
        self.x += self.vx
        self.y += self.vy
        
        # Bounce off edges
        if self.x < 0 or self.x > self.canvas_width:
            self.vx *= -1
        if self.y < 0 or self.y > self.canvas_height:
            self.vy *= -1
            
        # Keep within bounds
        self.x = max(0, min(self.canvas_width, self.x))
        self.y = max(0, min(self.canvas_height, self.y))

class JarvisVisualUI:
    def __init__(self, root):
        self.root = root
        self.root.title("JARVIS")
        
        # Window setup - transparent background
        self.root.attributes('-alpha', 0.95)  # Slight transparency
        self.root.configure(bg='black')
        
        # Window size
        self.width = 500
        self.height = 600
        self.root.geometry(f"{self.width}x{self.height}")
        
        # Make window frameless for modern look (optional)
        # self.root.overrideredirect(True)
        
        # Initialize JARVIS core
        self.core = None
        self.running = False
        
        # Create UI elements
        self._create_ui()
        
        # Particle system
        self.particles = []
        self.create_particles(200)
        
        # Animation
        self.animation_running = True
        self.animate()
        
    def _create_ui(self):
        # Top control bar
        control_frame = tk.Frame(self.root, bg='#1a1a1a', height=60)
        control_frame.pack(fill='x', side='top')
        control_frame.pack_propagate(False)
        
        # JARVIS title
        title = tk.Label(control_frame, text="J.A.R.V.I.S", 
                        font=('Arial', 16, 'bold'), 
                        fg='#00d9ff', bg='#1a1a1a')
        title.pack(side='left', padx=20, pady=15)
        
        # Status indicator
        self.status_label = tk.Label(control_frame, text="● Offline", 
                                     font=('Arial', 10), 
                                     fg='#ff4444', bg='#1a1a1a')
        self.status_label.pack(side='left', padx=10)
        
        # LLM status
        self.llm_label = tk.Label(control_frame, text="LLM: Ready", 
                                 font=('Arial', 9), 
                                 fg='#666666', bg='#1a1a1a')
        self.llm_label.pack(side='left', padx=10)
        
        # Start/Stop button
        self.control_btn = tk.Button(control_frame, text="START", 
                                     command=self.toggle_jarvis,
                                     font=('Arial', 10, 'bold'),
                                     fg='white', bg='#00aa00',
                                     activebackground='#00ff00',
                                     relief='flat', padx=20, pady=5)
        self.control_btn.pack(side='right', padx=20)
        
        # Close button
        close_btn = tk.Button(control_frame, text="✕", 
                             command=self.root.quit,
                             font=('Arial', 14, 'bold'),
                             fg='white', bg='#ff4444',
                             activebackground='#ff0000',
                             relief='flat', width=3)
        close_btn.pack(side='right', padx=5)
        
        # Particle canvas
        self.canvas = tk.Canvas(self.root, bg='black', 
                               highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)
        
        # Bottom status bar
        status_frame = tk.Frame(self.root, bg='#1a1a1a', height=100)
        status_frame.pack(fill='x', side='bottom')
        status_frame.pack_propagate(False)
        
        # Voice prompt
        self.prompt_label = tk.Label(status_frame, 
                                     text='Say "Jarvis" to activate...',
                                     font=('Arial', 11),
                                     fg='#00d9ff', bg='#1a1a1a')
        self.prompt_label.pack(pady=10)
        
        # Activity log (last command)
        self.activity_label = tk.Label(status_frame, 
                                       text="",
                                       font=('Arial', 9),
                                       fg='#888888', bg='#1a1a1a',
                                       wraplength=450)
        self.activity_label.pack()
        
    def create_particles(self, count):
        """Create particle cluster"""
        canvas_width = self.width
        canvas_height = self.height - 160  # Exclude control bars
        
        for _ in range(count):
            self.particles.append(Particle(canvas_width, canvas_height))
    
    def animate(self):
        """Animation loop for particles"""
        if not self.animation_running:
            return
            
        self.canvas.delete('all')
        
        # Get canvas dimensions
        canvas_width = self.canvas.winfo_width() or self.width
        canvas_height = self.canvas.winfo_height() or (self.height - 160)
        
        # Update particles canvas bounds
        for p in self.particles:
            p.canvas_width = canvas_width
            p.canvas_height = canvas_height
        
        # Center point for cluster effect
        center_x = canvas_width / 2
        center_y = canvas_height / 2
        
        # Update and draw particles
        for p in self.particles:
            # Pull particles toward center slightly (cluster effect)
            dx = center_x - p.x
            dy = center_y - p.y
            dist = math.sqrt(dx*dx + dy*dy)
            
            if dist > 0:
                p.vx += (dx / dist) * 0.01
                p.vy += (dy / dist) * 0.01
            
            # Damping to prevent too fast movement
            p.vx *= 0.99
            p.vy *= 0.99
            
            p.update()
            
            # Draw particle
            color_intensity = int(255 * (1 - min(dist / 200, 1)))
            color = f'#{color_intensity:02x}{200:02x}{255:02x}'
            
            self.canvas.create_oval(
                p.x - p.size, p.y - p.size,
                p.x + p.size, p.y + p.size,
                fill=color, outline=color
            )
        
        # Draw connections between nearby particles
        for i, p1 in enumerate(self.particles):
            for p2 in self.particles[i+1:i+10]:  # Only check nearby particles
                dx = p1.x - p2.x
                dy = p1.y - p2.y
                dist = math.sqrt(dx*dx + dy*dy)
                
                if dist < 80:  # Connection threshold
                    opacity = int(100 * (1 - dist / 80))
                    color = f'#{opacity:02x}{opacity:02x}{opacity+100:02x}'
                    self.canvas.create_line(
                        p1.x, p1.y, p2.x, p2.y,
                        fill=color, width=1
                    )
        
        # Continue animation
        self.root.after(30, self.animate)  # ~30 FPS
    
    def log_message(self, msg):
        """Log messages to UI"""
        self.activity_label.config(text=msg)
    
    def toggle_jarvis(self):
        """Start/Stop JARVIS"""
        if not self.running:
            self.start_jarvis()
        else:
            self.stop_jarvis()
    
    def start_jarvis(self):
        """Start JARVIS voice listening"""
        self.running = True
        self.control_btn.config(text="STOP", bg='#aa0000', activebackground='#ff0000')
        self.status_label.config(text="● Online", fg='#00ff00')
        self.prompt_label.config(text='Listening for "Jarvis"...')
        
        # Initialize JARVIS core
        self.core = JarvisCore(log_fn=self.log_message)
        
        # Check LLM status
        if hasattr(self.core, 'llm_handler') and self.core.llm_handler.is_available():
            self.llm_label.config(text="LLM: Active", fg='#00ff00')
        else:
            self.llm_label.config(text="LLM: Offline", fg='#ff8800')
        
        # Start JARVIS thread
        self.core.start()
        self.log_message("JARVIS initialized and listening...")
    
    def stop_jarvis(self):
        """Stop JARVIS"""
        self.running = False
        self.control_btn.config(text="START", bg='#00aa00', activebackground='#00ff00')
        self.status_label.config(text="● Offline", fg='#ff4444')
        self.prompt_label.config(text='Say "Jarvis" to activate...')
        
        if self.core:
            self.core.running = False
            self.core = None
        
        self.log_message("JARVIS stopped")
    
    def on_closing(self):
        """Clean up on window close"""
        self.animation_running = False
        self.stop_jarvis()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = JarvisVisualUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
