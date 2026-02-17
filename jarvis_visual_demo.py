"""
JARVIS Visual Demo - Particle Animation
Standalone demo of the visual interface
"""

import tkinter as tk
import math
import random

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

class JarvisVisualDemo:
    def __init__(self, root):
        self.root = root
        self.root.title("JARVIS - Visual Demo")
        
        # Window setup - semi-transparent
        try:
            self.root.attributes('-alpha', 0.95)
        except:
            pass  # Alpha not supported on all platforms
            
        self.root.configure(bg='black')
        
        # Window size
        self.width = 500
        self.height = 600
        self.root.geometry(f"{self.width}x{self.height}")
        
        # Create UI
        self._create_ui()
        
        # Particle system
        self.particles = []
        self.create_particles(200)
        
        # Animation state
        self.animation_running = True
        self.listening = False
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
        self.status_label = tk.Label(control_frame, text="● Ready", 
                                     font=('Arial', 10), 
                                     fg='#00ff00', bg='#1a1a1a')
        self.status_label.pack(side='left', padx=10)
        
        # LLM status
        self.llm_label = tk.Label(control_frame, text="LLM: llama3.2", 
                                 font=('Arial', 9), 
                                 fg='#00ff00', bg='#1a1a1a')
        self.llm_label.pack(side='left', padx=10)
        
        # Demo button
        self.control_btn = tk.Button(control_frame, text="SIMULATE", 
                                     command=self.simulate_listening,
                                     font=('Arial', 10, 'bold'),
                                     fg='white', bg='#0088ff',
                                     activebackground='#00aaff',
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
        
        # Particle canvas (transparent background effect)
        self.canvas = tk.Canvas(self.root, bg='#0a0a0a', 
                               highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)
        
        # Bottom status bar
        status_frame = tk.Frame(self.root, bg='#1a1a1a', height=100)
        status_frame.pack(fill='x', side='bottom')
        status_frame.pack_propagate(False)
        
        # Voice prompt
        self.prompt_label = tk.Label(status_frame, 
                                     text='Say something...',
                                     font=('Arial', 12),
                                     fg='#00d9ff', bg='#1a1a1a')
        self.prompt_label.pack(pady=10)
        
        # Activity log
        self.activity_label = tk.Label(status_frame, 
                                       text="Visual Interface Ready",
                                       font=('Arial', 9),
                                       fg='#888888', bg='#1a1a1a',
                                       wraplength=450)
        self.activity_label.pack()
        
    def create_particles(self, count):
        """Create particle cluster"""
        canvas_width = self.width
        canvas_height = self.height - 160
        
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
        
        # Update bounds
        for p in self.particles:
            p.canvas_width = canvas_width
            p.canvas_height = canvas_height
        
        # Center point
        center_x = canvas_width / 2
        center_y = canvas_height / 2
        
        # Update and draw particles
        for p in self.particles:
            # Cluster effect - pull toward center
            dx = center_x - p.x
            dy = center_y - p.y
            dist = math.sqrt(dx*dx + dy*dy)
            
            if dist > 0:
                # Stronger pull when listening
                pull_strength = 0.02 if self.listening else 0.01
                p.vx += (dx / dist) * pull_strength
                p.vy += (dy / dist) * pull_strength
            
            # Damping
            p.vx *= 0.99
            p.vy *= 0.99
            
            p.update()
            
            # Draw particle with color gradient
            if self.listening:
                # More vibrant when "listening"
                color_intensity = int(255 * (1 - min(dist / 150, 1)))
                color = f'#{color_intensity:02x}{255:02x}{255:02x}'  # Cyan
            else:
                # Blue-ish when idle
                color_intensity = int(200 * (1 - min(dist / 200, 1)))
                color = f'#{color_intensity:02x}{color_intensity+50:02x}{255:02x}'
            
            self.canvas.create_oval(
                p.x - p.size, p.y - p.size,
                p.x + p.size, p.y + p.size,
                fill=color, outline=color
            )
        
        # Draw connections between nearby particles
        for i, p1 in enumerate(self.particles):
            for p2 in self.particles[i+1:i+10]:
                dx = p1.x - p2.x
                dy = p1.y - p2.y
                dist = math.sqrt(dx*dx + dy*dy)
                
                threshold = 90 if self.listening else 80
                if dist < threshold:
                    opacity = int(150 * (1 - dist / threshold))
                    color = f'#{opacity:02x}{opacity+50:02x}{opacity+100:02x}'
                    self.canvas.create_line(
                        p1.x, p1.y, p2.x, p2.y,
                        fill=color, width=1
                    )
        
        # Continue animation (~30 FPS)
        self.root.after(30, self.animate)
    
    def simulate_listening(self):
        """Simulate voice activation"""
        if not self.listening:
            self.listening = True
            self.control_btn.config(text="LISTENING...", bg='#00ff00')
            self.prompt_label.config(text='Listening...', fg='#00ff00')
            self.activity_label.config(text="Processing voice input...")
            
            # Auto-stop after 3 seconds
            self.root.after(3000, self.simulate_response)
        else:
            self.stop_listening()
    
    def simulate_response(self):
        """Simulate JARVIS responding"""
        self.activity_label.config(text="JARVIS: Opening Chrome browser...")
        self.root.after(2000, self.stop_listening)
    
    def stop_listening(self):
        """Stop listening state"""
        self.listening = False
        self.control_btn.config(text="SIMULATE", bg='#0088ff')
        self.prompt_label.config(text='Say something...', fg='#00d9ff')
        self.activity_label.config(text="Ready for commands")

def main():
    root = tk.Tk()
    app = JarvisVisualDemo(root)
    root.mainloop()

if __name__ == "__main__":
    main()
