# JARVIS Cinematic - MICRO PARTICLE VERSION
# Ultra-small particles like luminous dust - Professional AI aesthetic

import pygame
import numpy as np
import math
from particle_system import ParticleSystem
from visual_states import StateManager, VisualState

class JarvisMicroParticles:
    """JARVIS with ultra-small micro particles - like digital stardust"""
    
    def __init__(self):
        pygame.init()
        
        # Fullscreen
        infoObject = pygame.display.Info()
        self.width = infoObject.current_w
        self.height = infoObject.current_h
        
        self.screen = pygame.display.set_mode(
            (self.width, self.height), 
            pygame.FULLSCREEN | pygame.NOFRAME
        )
        pygame.display.set_caption("JARVIS")
        
        self.center = (self.width // 2, self.height // 2)
        
        # Particle system
        radius = min(self.width, self.height) // 3
        self.particles = ParticleSystem(num_particles=800, radius=radius)
        self.state = StateManager()
        
        # Timing
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.dt = 0.0
        
        # Background
        self.background_surface = self._create_background()
        
        # Running
        self.running = True
        self.auto_cycle = True
        self.cycle_timer = 0.0
        self.cycle_interval = 4.0
        
        # Audio simulation
        self.sim_audio_phase = 0.0
        
        # Hide cursor
        pygame.mouse.set_visible(False)
        
    def _create_background(self):
        """Deep black background with subtle gradient"""
        surface = pygame.Surface((self.width, self.height))
        surface.fill((5, 7, 13))  # #05070D
        
        # Very subtle center glow
        center_glow = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.circle(
            center_glow,
            (0, 15, 25, 30),
            self.center,
            max(self.width, self.height) // 2
        )
        surface.blit(center_glow, (0, 0))
        
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
        
        # Auto cycling
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
    
    def _draw_micro_particle(self, surface, x, y, size, color, alpha):
        """Draw ultra-small particle with soft glow - like luminous dust"""
        if alpha <= 0:
            return
        
        # MICRO particles: 1.5px - 3px max
        base_size = max(1.5, min(size, 3.0))
        
        # Soft glow - 2 layers only, very subtle
        # Layer 1: Outer soft glow
        outer_size = base_size * 2.5
        outer_alpha = alpha * 0.15
        
        temp = pygame.Surface((int(outer_size * 2) + 4, int(outer_size * 2) + 4), pygame.SRCALPHA)
        center_pos = int(outer_size) + 2
        
        pygame.draw.circle(
            temp,
            (*color, int(outer_alpha * 255)),
            (center_pos, center_pos),
            int(outer_size)
        )
        
        surface.blit(
            temp,
            (int(x - center_pos), int(y - center_pos)),
            special_flags=pygame.BLEND_RGBA_ADD
        )
        
        # Layer 2: Core bright point
        core_size = base_size * 0.8
        core_alpha = alpha * 0.9
        
        temp2 = pygame.Surface((int(core_size * 2) + 2, int(core_size * 2) + 2), pygame.SRCALPHA)
        core_center = int(core_size) + 1
        
        pygame.draw.circle(
            temp2,
            (*color, int(core_alpha * 255)),
            (core_center, core_center),
            int(core_size)
        )
        
        surface.blit(
            temp2,
            (int(x - core_center), int(y - core_center)),
            special_flags=pygame.BLEND_RGBA_ADD
        )
    
    def render(self):
        """Render frame"""
        # Background
        self.screen.blit(self.background_surface, (0, 0))
        
        # Strong blur effect when active
        blur_intensity = self.state.get_blur_intensity()
        if blur_intensity > 0:
            blur_passes = int(blur_intensity / 6)
            if blur_passes > 0:
                temp = self.screen.copy()
                
                # Multi-pass blur
                for _ in range(min(blur_passes, 4)):
                    small = pygame.transform.smoothscale(
                        temp, 
                        (self.width // 5, self.height // 5)
                    )
                    temp = pygame.transform.smoothscale(small, (self.width, self.height))
                
                # Strong blur alpha
                alpha = min(int(255 * blur_intensity / 20.0), 240)
                temp.set_alpha(alpha)
                self.screen.blit(temp, (0, 0))
        
        # Get particle positions
        positions_2d, depths = self.particles.get_2d_projection(camera_distance=800)
        
        # Sort by depth
        sorted_indices = np.argsort(depths)[::-1]
        
        # Render MICRO particles
        for idx in sorted_indices:
            pos = positions_2d[idx]
            depth = depths[idx]
            
            x = self.center[0] + pos[0]
            y = self.center[1] + pos[1]
            
            if x < -50 or x > self.width + 50 or y < -50 or y > self.height + 50:
                continue
            
            # Depth fade
            depth_factor = 1.0 - min(depth / 1400.0, 0.6)
            
            # Color
            color_rgb = self.particles.colors[idx]
            color = (
                int(color_rgb[0] * 255),
                int(color_rgb[1] * 255),
                int(color_rgb[2] * 255)
            )
            
            # MICRO size: 1.8px - 2.5px
            base_particle_size = self.particles.sizes[idx]
            size = 1.8 + (base_particle_size * 0.3) * depth_factor  # 1.8 - 2.5px range
            
            alpha = self.particles.alphas[idx] * depth_factor * 0.9
            
            # Draw micro particle
            self._draw_micro_particle(self.screen, x, y, size, color, alpha)
        
        # Minimal state indicator
        font = pygame.font.SysFont('Consolas', 20)
        state_name = self.state.get_state().value.upper()
        text = font.render(state_name, True, (0, 240, 255, 150))
        self.screen.blit(text, (25, 25))
        
        # Exit hint
        hint_font = pygame.font.SysFont('Consolas', 14)
        hint = hint_font.render("ESC = Exit", True, (60, 100, 140))
        self.screen.blit(hint, (25, self.height - 35))
        
        pygame.display.flip()
    
    def run(self):
        """Main loop"""
        print("=" * 60)
        print("JARVIS - MICRO PARTICLE VISUALIZATION")
        print("=" * 60)
        print(f"Resolution: {self.width}x{self.height}")
        print(f"Particles: 800 ultra-small (1.8-2.5px)")
        print(f"Style: Luminous dust / Digital stardust")
        print()
        print("ESC or Q = Exit")
        print("SPACE = Cycle states")
        print()
        print("=" * 60)
        
        while self.running:
            self.dt = self.clock.tick(self.fps) / 1000.0
            self.update()
            self.render()
        
        pygame.mouse.set_visible(True)
        pygame.quit()
        print("\nJARVIS offline.")

if __name__ == "__main__":
    jarvis = JarvisMicroParticles()
    jarvis.run()
