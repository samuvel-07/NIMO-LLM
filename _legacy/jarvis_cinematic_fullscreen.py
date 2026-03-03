# JARVIS Cinematic - FULLSCREEN VERSION
# Maximum immersion - fills entire screen

import pygame
import numpy as np
import time
import math
from particle_system import ParticleSystem
from visual_states import StateManager, VisualState

class JarvisCinematicFullscreen:
    """Cinematic JARVIS - FULLSCREEN immersive experience"""
    
    def __init__(self):
        pygame.init()
        
        # Get display info for fullscreen
        infoObject = pygame.display.Info()
        self.width = infoObject.current_w
        self.height = infoObject.current_h
        
        # FULLSCREEN - NO WINDOW CHROME
        self.screen = pygame.display.set_mode(
            (self.width, self.height), 
            pygame.FULLSCREEN | pygame.NOFRAME
        )
        pygame.display.set_caption("JARVIS")
        
        self.center = (self.width // 2, self.height // 2)
        
        # BIGGER particles for fullscreen
        radius = min(self.width, self.height) // 3  # 1/3 of screen
        self.particles = ParticleSystem(num_particles=800, radius=radius)
        self.state = StateManager()
        
        # Timing
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.dt = 0.0
        
        # Background
        self.background_surface = self._create_background()
        
        # Running flag
        self.running = True
        
        # Auto state cycling
        self.auto_cycle = True
        self.cycle_timer = 0.0
        self.cycle_interval = 4.0  # 4 seconds per state
        
        # Simulated audio
        self.sim_audio_phase = 0.0
        
        # Hide mouse cursor
        pygame.mouse.set_visible(False)
        
    def _create_background(self):
        """Create dark radial gradient"""
        surface = pygame.Surface((self.width, self.height))
        
        # Faster gradient creation
        for y in range(0, self.height, 2):
            for x in range(0, self.width, 2):
                dx = x - self.center[0]
                dy = y - self.center[1]
                dist = np.sqrt(dx*dx + dy*dy)
                
                factor = max(0, 1.0 - dist / (max(self.width, self.height) * 0.6))
                
                r = int(5 + factor * 15)
                g = int(7 + factor * 20)
                b = int(13 + factor * 30)
                
                # Draw 2x2 block
                pygame.draw.rect(surface, (r, g, b), (x, y, 2, 2))
        
        return surface
    
    def update(self):
        """Update systems"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    self._next_state()
                elif event.key == pygame.K_a:
                    self.auto_cycle = not self.auto_cycle
        
        # Auto state cycling
        if self.auto_cycle:
            self.cycle_timer += self.dt
            if self.cycle_timer >= self.cycle_interval:
                self.cycle_timer = 0.0
                self._next_state()
        
        # Update state
        self.state.update(self.dt)
        
        # Update particles
        current_state = self.state.get_state()
        
        if current_state == VisualState.IDLE:
            self.particles.update_idle(self.dt)
        elif current_state == VisualState.LISTENING:
            self.particles.update_listening(self.dt)
        elif current_state == VisualState.SPEAKING:
            self.sim_audio_phase += self.dt * 5.0
            amplitude = (math.sin(self.sim_audio_phase) + 1.0) * 0.35
            freqs = np.array([
                math.sin(self.sim_audio_phase * (i + 1) * 0.5) * 0.5 + 0.5
                for i in range(16)
            ])
            self.particles.update_speaking(amplitude, freqs, self.dt)
        elif current_state == VisualState.EXECUTING:
            progress = self.state.get_execute_progress()
            self.particles.update_executing(self.dt, progress)
    
    def _next_state(self):
        """Cycle states"""
        current = self.state.get_state()
        if current == VisualState.IDLE:
            self.state.set_state(VisualState.LISTENING)
        elif current == VisualState.LISTENING:
            self.state.set_state(VisualState.SPEAKING)
        elif current == VisualState.SPEAKING:
            self.state.set_state(VisualState.EXECUTING)
        else:
            self.state.set_state(VisualState.IDLE)
    
    def _draw_particle(self, surface, x, y, size, color, alpha):
        """Draw glowing particle"""
        if alpha <= 0 or size <= 0:
            return
        
        # Multi-layer glow - BIGGER for fullscreen
        for i in range(4, 0, -1):  # 4 layers instead of 3
            glow_alpha = alpha * (1.0 / (i + 1))
            glow_size = size * (i + 1.5)  # Bigger glow
            
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
        # Background
        self.screen.blit(self.background_surface, (0, 0))
        
        # Blur effect
        blur_intensity = self.state.get_blur_intensity()
        if blur_intensity > 0:
            blur_passes = int(blur_intensity / 8)
            if blur_passes > 0:
                temp = self.screen.copy()
                for _ in range(min(blur_passes, 3)):
                    small = pygame.transform.smoothscale(
                        temp, 
                        (self.width // 4, self.height // 4)
                    )
                    temp = pygame.transform.smoothscale(small, (self.width, self.height))
                
                alpha = min(int(255 * blur_intensity / 25.0), 220)
                temp.set_alpha(alpha)
                self.screen.blit(temp, (0, 0))
        
        # Get particle positions
        positions_2d, depths = self.particles.get_2d_projection(camera_distance=800)
        
        # Sort by depth
        sorted_indices = np.argsort(depths)[::-1]
        
        # Render particles
        for idx in sorted_indices:
            pos = positions_2d[idx]
            depth = depths[idx]
            
            x = self.center[0] + pos[0]
            y = self.center[1] + pos[1]
            
            if x < -100 or x > self.width + 100 or y < -100 or y > self.height + 100:
                continue
            
            depth_factor = 1.0 - min(depth / 1400.0, 0.5)
            
            color_rgb = self.particles.colors[idx]
            color = (
                int(color_rgb[0] * 255),
                int(color_rgb[1] * 255),
                int(color_rgb[2] * 255)
            )
            
            size = self.particles.sizes[idx] * depth_factor * 1.5  # BIGGER particles
            alpha = self.particles.alphas[idx] * depth_factor
            
            self._draw_particle(self.screen, x, y, size, color, alpha)
        
        # Minimal UI in corner
        font = pygame.font.SysFont('Consolas', 24)
        state_name = self.state.get_state().value.upper()
        text = font.render(state_name, True, (0, 240, 255, 180))
        self.screen.blit(text, (30, 30))
        
        # ESC hint
        hint_font = pygame.font.SysFont('Consolas', 16)
        hint = hint_font.render("ESC or Q = Exit", True, (80, 120, 160))
        self.screen.blit(hint, (30, self.height - 40))
        
        pygame.display.flip()
    
    def run(self):
        """Main loop"""
        print("=" * 60)
        print("JARVIS CINEMATIC - FULLSCREEN")
        print("=" * 60)
        print(f"Resolution: {self.width}x{self.height}")
        print(f"Particles: 800")
        print(f"Particle Radius: {self.particles.base_radius}px")
        print()
        print("Press ESC or Q to exit")
        print("Press SPACE to cycle states")
        print()
        print("Enjoy the experience!")
        print("=" * 60)
        
        while self.running:
            self.dt = self.clock.tick(self.fps) / 1000.0
            self.update()
            self.render()
        
        pygame.mouse.set_visible(True)
        pygame.quit()

if __name__ == "__main__":
    jarvis = JarvisCinematicFullscreen()
    jarvis.run()
