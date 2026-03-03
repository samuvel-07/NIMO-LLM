# JARVIS Volumetric - Professional 3-Layer Living Energy Core
# Multi-layer depth, Perlin noise, color variation, state-based blur

import pygame
import numpy as np
import math
from volumetric_particles import VolumetricParticleSystem
from visual_states import StateManager, VisualState

class JarvisVolumetric:
    """Professional volumetric 3-layer particle system"""
    
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
        
        # Volumetric particle system (3 layers)
        radius = min(self.width, self.height) // 3
        self.particles = VolumetricParticleSystem(radius=radius)
        self.state = StateManager()
        
        # Timing
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.dt = 0.0
        
        # Background
        self.background_surface = self._create_background()
        
        # Bloom simulation surface
        self.bloom_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Running
        self.running = True
        self.exiting = False
        self.exit_fade = 1.0  # Fade from 1.0 to 0.0
        
        self.auto_cycle = True
        self.cycle_timer = 0.0
        self.cycle_interval = 4.0
        
        # Audio simulation
        self.sim_audio_phase = 0.0
        
        pygame.mouse.set_visible(False)
    
    def _graceful_exit(self):
        """Start graceful exit with fade-out"""
        self.exiting = True
        self.auto_cycle = False
        print("\nInitiating graceful shutdown...")
        
    def _create_background(self):
        """Deep black with fog effect"""
        surface = pygame.Surface((self.width, self.height))
        
        # Deep black base #05070D
        surface.fill((5, 7, 13))
        
        # Volumetric fog simulation (center glow)
        fog = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Multiple fog layers
        for radius_mult in [1.5, 1.0, 0.5]:
            radius = int(max(self.width, self.height) * radius_mult / 2)
            alpha = int(20 / radius_mult)
            
            pygame.draw.circle(
                fog,
                (0, 20, 35, alpha),
                self.center,
                radius
            )
        
        surface.blit(fog, (0, 0))
        
        return surface
    
    def update(self):
        """Update systems"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._graceful_exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                    self._graceful_exit()
                elif event.key == pygame.K_SPACE:
                    self._next_state()
                elif event.key == pygame.K_a:
                    self.auto_cycle = not self.auto_cycle
        
        # Handle fade-out during exit
        if self.exiting:
            self.exit_fade -= 0.03  # Fade speed
            if self.exit_fade <= 0:
                self.running = False
                return
        
        # Auto cycle (only if not exiting)
        if self.auto_cycle and not self.exiting:
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
    
    def _get_blur_amount(self):
        """State-based blur - NOT always blurred"""
        state = self.state.get_state()
        
        if state == VisualState.IDLE:
            return 0  # NO BLUR in idle
        elif state == VisualState.LISTENING:
            return 0.3  # 30% blur
        elif state == VisualState.SPEAKING:
            return 0.5  # 50% blur
        elif state == VisualState.EXECUTING:
            # Pulse flash - minimal blur
            return 0.2
        
        return 0
    
    def _draw_micro_particle_with_bloom(self, surface, bloom_surface, x, y, size, color, alpha, depth_factor):
        """Draw particle with bloom effect"""
        if alpha <= 0:
            return
        
        # Depth-based size scaling
        depth_scale = 1.0 / max(depth_factor * 0.5 + 0.5, 0.5)
        final_size = max(1.5, min(size * depth_scale, 3.0))
        
        # Main particle (on main surface)
        # Outer glow
        outer_size = final_size * 2.0
        outer_alpha = alpha * 0.2
        
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
        
        # Core
        core_size = final_size * 0.7
        core_alpha = alpha * 0.95
        
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
        
        # BLOOM EFFECT (on separate surface)
        bloom_size = final_size * 4.0
        bloom_alpha = alpha * 0.15
        
        bloom_temp = pygame.Surface((int(bloom_size * 2) + 4, int(bloom_size * 2) + 4), pygame.SRCALPHA)
        bloom_center = int(bloom_size) + 2
        
        pygame.draw.circle(
            bloom_temp,
            (*color, int(bloom_alpha * 255)),
            (bloom_center, bloom_center),
            int(bloom_size)
        )
        
        bloom_surface.blit(
            bloom_temp,
            (int(x - bloom_center), int(y - bloom_center)),
            special_flags=pygame.BLEND_RGBA_ADD
        )
    
    def render(self):
        """Render with volumetric effects"""
        # Background
        self.screen.blit(self.background_surface, (0, 0))
        
        # State-based blur (NOT always on!)
        blur_amount = self._get_blur_amount()
        
        if blur_amount > 0:
            blur_passes = int(blur_amount * 5)
            if blur_passes > 0:
                temp = self.screen.copy()
                
                for _ in range(min(blur_passes, 3)):
                    small = pygame.transform.smoothscale(
                        temp, 
                        (self.width // 4, self.height // 4)
                    )
                    temp = pygame.transform.smoothscale(small, (self.width, self.height))
                
                alpha = int(255 * blur_amount)
                temp.set_alpha(alpha)
                self.screen.blit(temp, (0, 0))
        
        # Clear bloom surface
        self.bloom_surface.fill((0, 0, 0, 0))
        
        # Get particles
        positions_2d, depths = self.particles.get_2d_projection(camera_distance=800)
        
        # Sort by depth
        sorted_indices = np.argsort(depths)[::-1]
        
        # Render particles with bloom
        for idx in sorted_indices:
            pos = positions_2d[idx]
            depth = depths[idx]
            
            x = self.center[0] + pos[0]
            y = self.center[1] + pos[1]
            
            if x < -100 or x > self.width + 100 or y < -100 or y > self.height + 100:
                continue
            
            # Depth factor
            depth_factor = depths[idx] / 800.0
            
            # Particle properties
            color_rgb = self.particles.colors[idx]
            color = (
                int(color_rgb[0] * 255),
                int(color_rgb[1] * 255),
                int(color_rgb[2] * 255)
            )
            
            size = self.particles.sizes[idx]
            alpha = self.particles.alphas[idx] * (1.0 - min(depth_factor * 0.4, 0.6))
            
            # Apply fade-out during exit
            if self.exiting:
                alpha *= self.exit_fade
            
            # Draw with bloom
            self._draw_micro_particle_with_bloom(
                self.screen, self.bloom_surface,
                x, y, size, color, alpha, depth_factor
            )
        
        # Apply bloom pass
        self.screen.blit(self.bloom_surface, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        
        # Minimal UI
        font = pygame.font.SysFont('Consolas', 20)
        state_name = self.state.get_state().value.upper()
        
        # Show layer info
        info_text = f"{state_name} | 3-Layer Volumetric"
        text = font.render(info_text, True, (0, 240, 255, 150))
        self.screen.blit(text, (25, 25))
        
        hint_font = pygame.font.SysFont('Consolas', 14)
        hint = hint_font.render("ESC = Exit | SPACE = Cycle", True, (60, 100, 140))
        self.screen.blit(hint, (25, self.height - 35))
        
        pygame.display.flip()
    
    def run(self):
        """Main loop"""
        print("=" * 70)
        print("JARVIS - VOLUMETRIC 3-LAYER NEURAL CORE")
        print("=" * 70)
        print(f"Resolution: {self.width}x{self.height}")
        print()
        print("LAYER STRUCTURE:")
        print(f"  Layer 1 (Inner Cloud):  {self.particles.layer1_count} particles - Random volume")
        print(f"  Layer 2 (Orbital Shell): {self.particles.layer2_count} particles - Fibonacci sphere")
        print(f"  Layer 3 (Outer Halo):   {self.particles.layer3_count} particles - Extended shell")
        print(f"  TOTAL: {self.particles.total_particles} particles")
        print()
        print("FEATURES:")
        print("  + Volumetric depth distribution")
        print("  + Perlin noise motion")
        print("  + Color variation (not uniform)")
        print("  + State-based blur (idle=0%, listening=30%, speaking=50%)")
        print("  + Bloom effect")
        print("  + Depth-based scaling")
        print()
        print("ESC or Q = Exit | SPACE = Cycle states")
        print("=" * 70)
        
        while self.running:
            self.dt = self.clock.tick(self.fps) / 1000.0
            self.update()
            self.render()
        
        # Cleanup
        self._cleanup()
        pygame.mouse.set_visible(True)
        pygame.quit()
        print("\nJARVIS volumetric core offline.")
        print("All resources cleaned up.")
    
    def _cleanup(self):
        """Proper cleanup to prevent GPU memory leaks"""
        print("Cleaning up resources...")
        
        # Dispose surfaces
        if hasattr(self, 'background_surface'):
            del self.background_surface
        
        if hasattr(self, 'bloom_surface'):
            del self.bloom_surface
        
        # Clear particle data
        if hasattr(self, 'particles'):
            del self.particles
        
        # Force garbage collection
        import gc
        gc.collect()
        
        print("GPU resources released.")

if __name__ == "__main__":
    jarvis = JarvisVolumetric()
    jarvis.run()
