# Particle System - 800-Particle Spherical Distribution
# Fibonacci sphere algorithm for perfect particle distribution

import numpy as np
import math

class ParticleSystem:
    """800-particle spherical system with Fibonacci distribution"""
    
    def __init__(self, num_particles=800, radius=200):
        self.num_particles = num_particles
        self.base_radius = radius
        self.radius = radius
        
        # Generate particles using Fibonacci sphere
        self.positions = self._generate_fibonacci_sphere()
        self.velocities = np.zeros((num_particles, 3))
        
        # Visual properties
        self.colors = np.ones((num_particles, 3))  # RGB
        self.sizes = np.ones(num_particles) * 2.0
        self.alphas = np.ones(num_particles) * 0.8
        
        # Motion parameters
        self.rotation_angle = 0.0
        self.rotation_speed = 0.5  # RPM
        self.pulse_phase = 0.0
        self.pulse_speed = 0.02
        self.pulse_amplitude = 0.1
        
        # Audio reactivity
        self.audio_displacement = np.zeros(num_particles)
        
    def _generate_fibonacci_sphere(self):
        """Generate evenly distributed points on a sphere using Fibonacci spiral"""
        positions = np.zeros((self.num_particles, 3))
        
        phi = math.pi * (3.0 - math.sqrt(5.0))  # Golden angle in radians
        
        for i in range(self.num_particles):
            y = 1 - (i / float(self.num_particles - 1)) * 2  # y from 1 to -1
            radius_at_y = math.sqrt(1 - y * y)  # radius at y
            
            theta = phi * i  # Golden angle increment
            
            x = math.cos(theta) * radius_at_y
            z = math.sin(theta) * radius_at_y
            
            positions[i] = [x * self.base_radius, 
                          y * self.base_radius, 
                          z * self.base_radius]
        
        return positions
    
    def update_idle(self, dt):
        """Update particles in IDLE state - gentle breathing motion"""
        # Slow rotation
        self.rotation_angle += self.rotation_speed * dt * 0.01
        
        # Breathing pulse
        self.pulse_phase += self.pulse_speed
        pulse = 1.0 + math.sin(self.pulse_phase) * self.pulse_amplitude
        
        # Apply rotation and pulse
        rotated = self._rotate_particles(self.positions, self.rotation_angle)
        self.current_positions = rotated * pulse
        
        # Gentle glow
        self.colors[:] = [0.0, 0.94, 1.0]  # Cyan #00F0FF
        self.alphas[:] = 0.4 + math.sin(self.pulse_phase) * 0.1
        
    def update_listening(self, dt):
        """Update particles in LISTENING state - accelerated motion"""
        # Faster rotation
        self.rotation_angle += self.rotation_speed * dt * 0.04
        
        # Expansion
        expansion = 1.2  # 20% larger
        
        # Apply rotation and expansion
        rotated = self._rotate_particles(self.positions, self.rotation_angle)
        self.current_positions = rotated * expansion
        
        # Bright glow with blue accent
        self.colors[:] = [0.0, 0.47, 1.0]  # Electric blue #0077FF
        self.alphas[:] = 0.8
        self.sizes[:] = 2.5
        
    def update_speaking(self, audio_amplitude, audio_freqs, dt):
        """Update particles in SPEAKING state - audio reactive"""
        # Rotation
        self.rotation_angle += self.rotation_speed * dt * 0.03
        
        # Audio-reactive displacement
        # Map frequency bands to particles
        num_bands = min(len(audio_freqs), self.num_particles)
        
        for i in range(num_bands):
            # Scale frequency amplitude
            displacement = audio_freqs[i] * 50.0  # Adjust sensitivity
            self.audio_displacement[i] = displacement
        
        # Apply rotation
        rotated = self._rotate_particles(self.positions, self.rotation_angle)
        
        # Add audio displacement along radial direction
        for i in range(self.num_particles):
            direction = rotated[i] / np.linalg.norm(rotated[i])
            rotated[i] += direction * self.audio_displacement[i]
        
        self.current_positions = rotated
        
        # Multi-color glow
        base_cyan = np.array([0.0, 0.94, 1.0])
        purple_accent = np.array([0.66, 0.33, 0.97])  # #A855F7
        
        # Mix colors based on audio
        mix = min(audio_amplitude * 2.0, 1.0)
        self.colors[:] = base_cyan * (1 - mix) + purple_accent * mix
        
        # Pulse alpha with audio
        self.alphas[:] = 0.7 + audio_amplitude * 0.3
        self.sizes[:] = 2.0 + audio_amplitude * 2.0
        
    def update_executing(self, dt, progress):
        """Update particles in EXECUTING state - energy pulse"""
        # Quick rotation
        self.rotation_angle += self.rotation_speed * dt * 0.06
        
        # Pulse ripple effect
        ripple = 1.0 + math.sin(progress * math.pi * 2) * 0.3
        
        rotated = self._rotate_particles(self.positions, self.rotation_angle)
        self.current_positions = rotated * ripple
        
        # Bright flash
        self.colors[:] = [0.0, 0.94, 1.0]
        self.alphas[:] = 0.9 + math.sin(progress * math.pi) * 0.1
        self.sizes[:] = 3.0
        
    def _rotate_particles(self, positions, angle):
        """Rotate particles around Y axis"""
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        
        rotation_matrix = np.array([
            [cos_a, 0, sin_a],
            [0, 1, 0],
            [-sin_a, 0, cos_a]
        ])
        
        return positions @ rotation_matrix.T
    
    def get_2d_projection(self, camera_distance=800):
        """Project 3D particles to 2D screen coordinates"""
        # Simple perspective projection
        if not hasattr(self, 'current_positions'):
            self.current_positions = self.positions
        
        # Z-offset for camera
        z_offset = camera_distance
        
        # Perspective division
        projected = []
        depths = []
        
        for pos in self.current_positions:
            x, y, z = pos
            z_cam = z + z_offset
            
            if z_cam > 0:
                # Perspective projection
                scale = camera_distance / z_cam
                x_2d = x * scale
                y_2d = y * scale
                
                projected.append([x_2d, y_2d])
                depths.append(z_cam)
            else:
                projected.append([0, 0])
                depths.append(z_offset)
        
        return np.array(projected), np.array(depths)
