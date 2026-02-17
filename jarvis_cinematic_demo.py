# JARVIS Cinematic - Visual Demo (No Audio Required)
# Pure particle visualization without microphone dependency

import pygame
import numpy as np
import time
import math
from particle_system import ParticleSystem
from visual_states import StateManager, VisualState

class JarvisCinematicDemo:
    """Cinematic JARVIS - Visual demo without audio"""
    
    def __init__(self, width=1920, height=1080, fullscreen=False):
        pygame.init()
        
        # Window setup - NO CHROME
        flags = pygame.NOFRAME
        if fullscreen:
            flags |= pygame.FULLSCREEN
            
        self.screen = pygame.display.set_mode((width, height), flags)
        pygame.display.set_caption("JARVIS Cinematic")
        
        self.width = width
        self.height = height
        self.center = (width // 2, height // 2)
        
        # Core systems
        self.particles = ParticleSystem(num_particles=800, radius=250)
        self.state = StateManager()
        
        # Timing
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.dt = 0.0
        
        # Background
        self.background_color = (5, 7, 13)
        self.background_surface = self._create_background()
        
        # Running flag
        self.running = True
        
        # Auto state cycling
        self.auto_cycle = True
        self.cycle_timer = 0.0
        self.cycle_interval = 3.0  # 3 seconds per state
        
        # Simulated audio for SPEAKING state
        self.sim_audio_phase = 0.0
        
    def _create_background(self):
        """Create dark gradient background"""
        surface = pygame.Surface((self.width, self.height))
        
        for y in range(self.height):
            for x in range(self.width):
                dx = x - self.center[0]
                dy = y - self.center[1]
                dist = np.sqrt(dx*dx + dy*dy)
                
                factor = max(0, 1.0 - dist / (self.width * 0.7))
                
                r = int(5 + factor * 10)
                g = int(7 + factor * 15)
                b = int(13 + factor * 25)
                
                surface.set_at((x, y), (r, g, b))
        
        return surface
    
    def update(self):
        """Update all systems"""
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    # Manual state cycling
                    self._next_state()
                elif event.key == pygame.K_a:
                    # Toggle auto-cycle
                    self.auto_cycle = not self.auto_cycle
                    print(f"Auto-cycle: {self.auto_cycle}")
        
        # Auto state cycling
        if self.auto_cycle:
            self.cycle_timer += self.dt
            if self.cycle_timer >= self.cycle_interval:
                self.cycle_timer = 0.0
                self._next_state()
        
        # Update state
        self.state.update(self.dt)
        
        # Update particles based on state
        current_state = self.state.get_state()
        
        if current_state == VisualState.IDLE:
            self.particles.update_idle(self.dt)
            
        elif current_state == VisualState.LISTENING:
            self.particles.update_listening(self.dt)
            
        elif current_state == VisualState.SPEAKING:
            # Simulate audio with sine waves
            self.sim_audio_phase += self.dt * 5.0
            amplitude = (math.sin(self.sim_audio_phase) + 1.0) * 0.3
            
            # Generate fake frequency bands
            freqs = np.array([
                math.sin(self.sim_audio_phase * (i + 1) * 0.5) * 0.5 + 0.5
                for i in range(16)
            ])
            
            self.particles.update_speaking(amplitude, freqs, self.dt)
            
        elif current_state == VisualState.EXECUTING:
            progress = self.state.get_execute_progress()
            self.particles.update_executing(self.dt, progress)
    
    def _next_state(self):
        """Cycle to next state"""
        current = self.state.get_state()
        if current == VisualState.IDLE:
            self.state.set_state(VisualState.LISTENING)
            print("→ LISTENING MODE")
        elif current == VisualState.LISTENING:
            self.state.set_state(VisualState.SPEAKING)
            print("→ SPEAKING MODE")
        elif current == VisualState.SPEAKING:
            self.state.set_state(VisualState.EXECUTING)
            print("→ EXECUTING MODE")
        else:
            self.state.set_state(VisualState.IDLE)
            print("→ IDLE MODE")
    
    def _draw_particle(self, surface, x, y, size, color, alpha):
        """Draw a glowing particle with additive blending"""
        if alpha <= 0 or size <= 0:
            return
            
        # Multi-layer glow
        for i in range(3, 0, -1):
            glow_alpha = alpha * (1.0 / (i + 1))
            glow_size = size * (i + 1)
            
            # Create temp surface for transparency
            temp_size = int(glow_size * 2) + 2
            temp = pygame.Surface((temp_size, temp_size), pygame.SRCALPHA)
            
            pygame.draw.circle(
                temp,
                (*color, int(glow_alpha * 255)),
                (temp_size // 2, temp_size // 2),
                int(glow_size)
            )
            
            surface.blit(
                temp,
                (int(x - temp_size // 2), int(y - temp_size // 2)),
                special_flags=pygame.BLEND_RGBA_ADD
            )
    
    def render(self):
        """Render frame"""
        # Clear with background
        self.screen.blit(self.background_surface, (0, 0))
        
        # Apply blur effect
        blur_intensity = self.state.get_blur_intensity()
        if blur_intensity > 0:
            blur_passes = int(blur_intensity / 10)
            if blur_passes > 0:
                temp = self.screen.copy()
                for _ in range(min(blur_passes, 3)):
                    small = pygame.transform.smoothscale(
                        temp, 
                        (self.width // 4, self.height // 4)
                    )
                    temp = pygame.transform.smoothscale(small, (self.width, self.height))
                
                alpha = min(int(255 * blur_intensity / 25.0), 200)
                temp.set_alpha(alpha)
                self.screen.blit(temp, (0, 0))
        
        # Get particle 2D positions
        positions_2d, depths = self.particles.get_2d_projection(camera_distance=600)
        
        # Sort by depth (far to near)
        sorted_indices = np.argsort(depths)[::-1]
        
        # Render particles
        for idx in sorted_indices:
            pos = positions_2d[idx]
            depth = depths[idx]
            
            # Screen coordinates
            x = self.center[0] + pos[0]
            y = self.center[1] + pos[1]
            
            # Skip if off-screen
            if x < -50 or x > self.width + 50 or y < -50 or y > self.height + 50:
                continue
            
            # Depth fade
            depth_factor = 1.0 - min(depth / 1200.0, 0.5)
            
            # Particle properties
            color_rgb = self.particles.colors[idx]
            color = (
                int(color_rgb[0] * 255),
                int(color_rgb[1] * 255),
                int(color_rgb[2] * 255)
            )
            
            size = self.particles.sizes[idx] * depth_factor
            alpha = self.particles.alphas[idx] * depth_factor
            
            # Draw particle
            self._draw_particle(self.screen, x, y, size, color, alpha)
        
        # Draw status text (minimal)
        font = pygame.font.SysFont('Consolas', 20)
        state_name = self.state.get_state().value.upper()
        text = font.render(f"{state_name}", True, (0, 240, 255))
        self.screen.blit(text, (20, 20))
        
        # Instructions
        help_font = pygame.font.SysFont('Consolas', 14)
        help_text = [
            "SPACE: Next State",
            "A: Toggle Auto-cycle",
            "ESC: Exit"
        ]
        for i, line in enumerate(help_text):
            text_surface = help_font.render(line, True, (100, 150, 200))
            self.screen.blit(text_surface, (20, self.height - 80 + i * 20))
        
        # Update display
        pygame.display.flip()
    
    def run(self):
        """Main render loop"""
        print("=" * 60)
        print("JARVIS CINEMATIC - Visual Demo")
        print("=" * 60)
        print()
        print("Controls:")
        print("  SPACE - Cycle state manually")
        print("  A     - Toggle auto-cycle (currently: ON)")
        print("  ESC   - Exit")
        print()
        print("States cycle every 3 seconds:")
        print("  IDLE → LISTENING → SPEAKING → EXECUTING → IDLE")
        print()
        print("=" * 60)
        
        while self.running:
            self.dt = self.clock.tick(self.fps) / 1000.0
            self.update()
            self.render()
        
        pygame.quit()

# Main entry point
if __name__ == "__main__":
    jarvis = JarvisCinematicDemo(
        width=1920, 
        height=1080, 
        fullscreen=False
    )
    jarvis.run()
