# JARVIS Cinematic - Main visualization engine
# Iron Man-style particle interface with NO UI

import pygame
import numpy as np
import time
import sys
from particle_system import ParticleSystem
from audio_reactor import AudioReactor
from visual_states import StateManager, VisualState

class JarvisCinematic:
    """Cinematic JARVIS visualization - Pure experience, zero UI"""
    
    def __init__(self, width=1920, height=1080, fullscreen=False):
        pygame.init()
        
        # Window setup - NO CHROME
        if fullscreen:
            self.screen = pygame.display.set_mode(
                (width, height), 
                pygame.FULLSCREEN | pygame.NOFRAME
            )
        else:
            self.screen = pygame.display.set_mode(
                (width, height),
                pygame.NOFRAME  # No window decorations
            )
        
        pygame.display.set_caption("JARVIS")
        
        self.width = width
        self.height = height
        self.center = (width // 2, height // 2)
        
        # Core systems
        self.particles = ParticleSystem(num_particles=800, radius=250)
        self.audio = AudioReactor(sample_rate=16000, fft_size=512)
        self.state = StateManager()
        
        # Timing
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.dt = 0.0
        
        # Background
        self.background_color = (5, 7, 13)  # #05070D near black
        self.background_surface = None
        self._create_background()
        
        # Blur (simulated with multiple passes)
        self.blur_surface = pygame.Surface((width, height))
        
        # Running flag
        self.running = True
        
        # Demo mode (for testing without JARVIS integration)
        self.demo_mode = True
        self.demo_timer = 0.0
        
    def _create_background(self):
        """Create dark gradient background"""
        self.background_surface = pygame.Surface((self.width, self.height))
        
        # Simple radial gradient
        for y in range(self.height):
            for x in range(self.width):
                dx = x - self.center[0]
                dy = y - self.center[1]
                dist = np.sqrt(dx*dx + dy*dy)
                
                # Darker at edges
                factor = max(0, 1.0 - dist / (self.width * 0.7))
                
                r = int(5 + factor * 10)
                g = int(7 + factor * 15)
                b = int(13 + factor * 25)
                
                self.background_surface.set_at((x, y), (r, g, b))
    
    def start(self):
        """Start audio monitoring"""
        self.audio.start()
        print("JARVIS Cinematic started")
        print("Press ESC to exit")
        print("Press SPACE to cycle states (demo)")
    
    def stop(self):
        """Cleanup"""
        self.audio.stop()
        pygame.quit()
    
    def _demo_update(self):
        """Demo mode - cycle through states automatically"""
        self.demo_timer += self.dt
        
        if self.demo_timer > 4.0:  # Switch every 4 seconds
            self.demo_timer = 0.0
            
            current = self.state.get_state()
            if current == VisualState.IDLE:
                self.state.set_state(VisualState.LISTENING)
            elif current == VisualState.LISTENING:
                self.state.set_state(VisualState.SPEAKING)
            elif current == VisualState.SPEAKING:
                self.state.set_state(VisualState.EXECUTING)
            else:
                self.state.set_state(VisualState.IDLE)
    
    def update(self):
        """Update all systems"""
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE and self.demo_mode:
                    # Manual state cycling
                    current = self.state.get_state()
                    if current == VisualState.IDLE:
                        self.state.set_state(VisualState.LISTENING)
                    elif current == VisualState.LISTENING:
                        self.state.set_state(VisualState.SPEAKING)
                    elif current == VisualState.SPEAKING:
                        self.state.set_state(VisualState.EXECUTING)
                    else:
                        self.state.set_state(VisualState.IDLE)
        
        # Update audio
        self.audio.update()
        
        # Update state
        self.state.update(self.dt)
        
        # Demo mode auto-cycling
        if self.demo_mode:
            self._demo_update()
        
        # Update particles based on state
        current_state = self.state.get_state()
        
        if current_state == VisualState.IDLE:
            self.particles.update_idle(self.dt)
            
        elif current_state == VisualState.LISTENING:
            self.particles.update_listening(self.dt)
            
        elif current_state == VisualState.SPEAKING:
            amplitude = self.audio.get_amplitude()
            freqs = self.audio.get_frequency_bands()
            self.particles.update_speaking(amplitude, freqs, self.dt)
            
        elif current_state == VisualState.EXECUTING:
            progress = self.state.get_execute_progress()
            self.particles.update_executing(self.dt, progress)
    
    def _draw_particle(self, surface, x, y, size, color, alpha):
        """Draw a glowing particle"""
        # Create glow effect with multiple circles
        for i in range(3, 0, -1):
            glow_alpha = alpha * (1.0 / (i + 1))
            glow_size = size * (i + 1)
            
            # Create temp surface for transparency
            temp = pygame.Surface((int(glow_size * 2), int(glow_size * 2)), pygame.SRCALPHA)
            
            pygame.draw.circle(
                temp,
                (*color, int(glow_alpha * 255)),
                (int(glow_size), int(glow_size)),
                int(glow_size)
            )
            
            surface.blit(
                temp,
                (int(x - glow_size), int(y - glow_size)),
                special_flags=pygame.BLEND_RGBA_ADD
            )
    
    def render(self):
        """Render frame"""
        # Clear with background
        self.screen.blit(self.background_surface, (0, 0))
        
        # Apply blur if needed
        blur_intensity = self.state.get_blur_intensity()
        if blur_intensity > 0:
            # Simple blur simulation (box blur)
            blur_passes = int(blur_intensity / 10)
            if blur_passes > 0:
                temp = self.screen.copy()
                for _ in range(blur_passes):
                    # Downscale and upscale for blur effect
                    small = pygame.transform.smoothscale(temp, (self.width // 4, self.height // 4))
                    temp = pygame.transform.smoothscale(small, (self.width, self.height))
                
                # Blend blurred background
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
        
        # Update display
        pygame.display.flip()
    
    def run(self):
        """Main render loop"""
        self.start()
        
        while self.running:
            self.dt = self.clock.tick(self.fps) / 1000.0  # Convert to seconds
            
            self.update()
            self.render()
        
        self.stop()

# Main entry point
if __name__ == "__main__":
    # Create cinematic interface
    jarvis = JarvisCinematic(
        width=1920, 
        height=1080, 
        fullscreen=False  # Set True for full experience
    )
    
    # Run
    jarvis.run()
