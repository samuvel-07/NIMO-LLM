# Advanced Particle System - Volumetric 3-Layer Neural Core
# Professional multi-layer distribution with depth and motion variation

import numpy as np
import math
import random

class VolumetricParticleSystem:
    """3-layer volumetric particle system - living energy core"""
    
    def __init__(self, radius=250):
        self.base_radius = radius
        
        # 3 LAYERS
        self.layer1_count = 300  # Inner cloud
        self.layer2_count = 350  # Neural orbital shell
        self.layer3_count = 150  # Outer halo
        self.total_particles = self.layer1_count + self.layer2_count + self.layer3_count
        
        # Generate layered particles
        self.positions = np.zeros((self.total_particles, 3))
        self.layer_ids = np.zeros(self.total_particles, dtype=int)
        self.colors = np.ones((self.total_particles, 3))
        self.sizes = np.ones(self.total_particles) * 2.0
        self.alphas = np.ones(self.total_particles) * 0.8
        
        self._generate_volumetric_layers()
        
        # Motion parameters
        self.rotation_angle = 0.0
        self.rotation_speed = 0.5
        self.pulse_phase = 0.0
        self.pulse_speed = 0.02
        
        # Perlin noise simulation (simplified)
        self.noise_offsets = np.random.rand(self.total_particles, 3) * 100
        self.noise_time = 0.0
        
        # Audio reactivity
        self.audio_displacement = np.zeros(self.total_particles)
        
    def _generate_volumetric_layers(self):
        """Generate 3 distinct particle layers"""
        idx = 0
        
        # LAYER 1: Inner Cloud - TRUE volumetric distribution
        # Using cube root to prevent center clustering
        for i in range(self.layer1_count):
            # Proper sphere volume distribution
            u = random.uniform(0, 1)
            v = random.uniform(0, 1)
            theta = 2 * math.pi * u
            phi = math.acos(2 * v - 1)
            
            # CRITICAL: Use cube root for uniform volume density!
            # This prevents center overload
            r = (self.base_radius * 0.5) * (random.uniform(0, 1) ** (1.0/3.0))  # cbrt
            
            x = r * math.sin(phi) * math.cos(theta)
            y = r * math.sin(phi) * math.sin(theta)
            z = r * math.cos(phi)
            
            self.positions[idx] = [x, y, z]
            self.layer_ids[idx] = 1
            
            # Slightly darker, smaller
            self.colors[idx] = self._get_varied_color(0.7)
            self.sizes[idx] = 1.5
            self.alphas[idx] = 0.6
            idx += 1
        
        # LAYER 2: Neural Orbital Shell - Fibonacci sphere
        phi_golden = math.pi * (3.0 - math.sqrt(5.0))
        
        for i in range(self.layer2_count):
            y = 1 - (i / float(self.layer2_count - 1)) * 2
            radius_at_y = math.sqrt(1 - y * y)
            theta = phi_golden * i
            
            x = math.cos(theta) * radius_at_y
            z = math.sin(theta) * radius_at_y
            
            # At 70-90% of radius
            r_scale = random.uniform(0.7, 0.9)
            
            self.positions[idx] = [
                x * self.base_radius * r_scale,
                y * self.base_radius * r_scale,
                z * self.base_radius * r_scale
            ]
            self.layer_ids[idx] = 2
            
            # Brighter, medium size
            self.colors[idx] = self._get_varied_color(1.0)
            self.sizes[idx] = 2.0
            self.alphas[idx] = 0.8
            idx += 1
        
        # LAYER 3: Outer Halo - Larger spread
        for i in range(self.layer3_count):
            # Fibonacci on outer shell
            y = 1 - (i / float(self.layer3_count - 1)) * 2
            radius_at_y = math.sqrt(1 - y * y)
            theta = phi_golden * i
            
            x = math.cos(theta) * radius_at_y
            z = math.sin(theta) * radius_at_y
            
            # At 90-110% of radius (some outside)
            r_scale = random.uniform(0.9, 1.1)
            
            self.positions[idx] = [
                x * self.base_radius * r_scale,
                y * self.base_radius * r_scale,
                z * self.base_radius * r_scale
            ]
            self.layer_ids[idx] = 3
            
            # Slightly larger, varied brightness
            self.colors[idx] = self._get_varied_color(0.9)
            self.sizes[idx] = 2.3
            self.alphas[idx] = 0.7
            idx += 1
    
    def _get_varied_color(self, intensity=1.0):
        """Get color with variation - not uniform cyan"""
        # Base colors
        cyan = np.array([0.0, 0.94, 1.0])      # #00F0FF
        blue = np.array([0.0, 0.47, 1.0])      # #0077FF
        
        # Random mix
        mix_factor = random.uniform(0.3, 0.7)
        color = cyan * mix_factor + blue * (1 - mix_factor)
        
        return color * intensity
    
    def _perlin_noise_1d(self, x):
        """Simplified Perlin noise"""
        i = int(x)
        f = x - i
        
        # Smooth interpolation
        u = f * f * (3.0 - 2.0 * f)
        
        # Random gradients
        a = math.sin(i * 12.9898 + 78.233) * 43758.5453
        b = math.sin((i + 1) * 12.9898 + 78.233) * 43758.5453
        
        a = a - math.floor(a)
        b = b - math.floor(b)
        
        return a * (1 - u) + b * u
    
    def update_idle(self, dt):
        """IDLE: Gentle motion with Perlin noise"""
        self.rotation_angle += self.rotation_speed * dt * 0.01
        self.pulse_phase += self.pulse_speed
        self.noise_time += dt * 0.5
        
        # Base rotation
        rotated = self._rotate_particles(self.positions, self.rotation_angle)
        
        # Add Perlin noise displacement
        for i in range(self.total_particles):
            layer = self.layer_ids[i]
            
            # Different noise amplitude per layer
            if layer == 1:
                noise_scale = 5.0  # Inner cloud - more random
            elif layer == 2:
                noise_scale = 2.0  # Orbital shell - less random
            else:
                noise_scale = 3.0  # Outer halo - medium
            
            # Perlin noise displacement
            nx = self._perlin_noise_1d(self.noise_offsets[i, 0] + self.noise_time) * noise_scale
            ny = self._perlin_noise_1d(self.noise_offsets[i, 1] + self.noise_time) * noise_scale
            nz = self._perlin_noise_1d(self.noise_offsets[i, 2] + self.noise_time) * noise_scale
            
            rotated[i] += [nx, ny, nz]
        
        # Gentle pulse
        pulse = 1.0 + math.sin(self.pulse_phase) * 0.08
        self.current_positions = rotated * pulse
        
        # Layer-specific colors
        for i in range(self.total_particles):
            self.colors[i] = self._get_varied_color(0.7 if self.layer_ids[i] == 1 else 1.0)
            self.alphas[i] = 0.4 + math.sin(self.pulse_phase + i * 0.1) * 0.1
    
    def update_listening(self, dt):
        """LISTENING: Accelerated with expansion"""
        self.rotation_angle += self.rotation_speed * dt * 0.04
        self.noise_time += dt * 1.5
        
        rotated = self._rotate_particles(self.positions, self.rotation_angle)
        
        # Perlin noise
        for i in range(self.total_particles):
            noise_scale = 8.0 if self.layer_ids[i] == 3 else 4.0
            
            nx = self._perlin_noise_1d(self.noise_offsets[i, 0] + self.noise_time) * noise_scale
            ny = self._perlin_noise_1d(self.noise_offsets[i, 1] + self.noise_time) * noise_scale
            nz = self._perlin_noise_1d(self.noise_offsets[i, 2] + self.noise_time) * noise_scale
            
            rotated[i] += [nx, ny, nz]
        
        # Expansion
        expansion = 1.25
        self.current_positions = rotated * expansion
        
        # Brighter blue
        for i in range(self.total_particles):
            self.colors[i] = np.array([0.0, 0.5, 1.0])  # Electric blue
            self.alphas[i] = 0.8
            self.sizes[i] = 2.0 if self.layer_ids[i] == 1 else 2.5
    
    def update_speaking(self, audio_amplitude, audio_freqs, dt):
        """SPEAKING: Audio-reactive with color variation"""
        self.rotation_angle += self.rotation_speed * dt * 0.03
        self.noise_time += dt * 2.0
        
        rotated = self._rotate_particles(self.positions, self.rotation_angle)
        
        # Audio-reactive displacement
        num_bands = min(len(audio_freqs), self.total_particles)
        for i in range(num_bands):
            displacement = audio_freqs[i % len(audio_freqs)] * 30.0
            self.audio_displacement[i] = displacement
        
        # Apply noise + audio
        for i in range(self.total_particles):
            # Perlin noise
            noise_scale = 10.0
            nx = self._perlin_noise_1d(self.noise_offsets[i, 0] + self.noise_time) * noise_scale
            ny = self._perlin_noise_1d(self.noise_offsets[i, 1] + self.noise_time) * noise_scale
            nz = self._perlin_noise_1d(self.noise_offsets[i, 2] + self.noise_time) * noise_scale
            
            rotated[i] += [nx, ny, nz]
            
            # Audio displacement (radial)
            if np.linalg.norm(rotated[i]) > 0:
                direction = rotated[i] / np.linalg.norm(rotated[i])
                rotated[i] += direction * self.audio_displacement[i]
        
        self.current_positions = rotated
        
        # Color variation (cyan + purple)
        cyan = np.array([0.0, 0.94, 1.0])
        purple = np.array([0.66, 0.33, 0.97])
        
        for i in range(self.total_particles):
            mix = min(audio_amplitude * 1.5 + random.uniform(0, 0.3), 1.0)
            self.colors[i] = cyan * (1 - mix) + purple * mix
            self.alphas[i] = 0.7 + audio_amplitude * 0.3
            self.sizes[i] = 2.0 + audio_amplitude * 1.5
    
    def update_executing(self, dt, progress):
        """EXECUTING: Energy pulse ripple"""
        self.rotation_angle += self.rotation_speed * dt * 0.06
        
        rotated = self._rotate_particles(self.positions, self.rotation_angle)
        
        # Pulse ripple
        ripple = 1.0 + math.sin(progress * math.pi * 3) * 0.4
        self.current_positions = rotated * ripple
        
        # Bright flash
        for i in range(self.total_particles):
            self.colors[i] = np.array([0.0, 0.94, 1.0])
            self.alphas[i] = 0.9 + math.sin(progress * math.pi) * 0.1
            self.sizes[i] = 3.0
    
    def _rotate_particles(self, positions, angle):
        """Rotate around Y axis"""
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        
        rotation_matrix = np.array([
            [cos_a, 0, sin_a],
            [0, 1, 0],
            [-sin_a, 0, cos_a]
        ])
        
        return positions @ rotation_matrix.T
    
    def get_2d_projection(self, camera_distance=800):
        """Project 3D to 2D with depth"""
        if not hasattr(self, 'current_positions'):
            self.current_positions = self.positions
        
        z_offset = camera_distance
        
        projected = []
        depths = []
        
        for pos in self.current_positions:
            x, y, z = pos
            z_cam = z + z_offset
            
            if z_cam > 0:
                scale = camera_distance / z_cam
                x_2d = x * scale
                y_2d = y * scale
                
                projected.append([x_2d, y_2d])
                depths.append(z_cam)
            else:
                projected.append([0, 0])
                depths.append(z_offset)
        
        return np.array(projected), np.array(depths)
