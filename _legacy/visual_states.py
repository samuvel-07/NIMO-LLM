# Visual States - State machine for JARVIS visual modes

from enum import Enum
import time

class VisualState(Enum):
    """JARVIS visual states"""
    IDLE = "idle"
    LISTENING = "listening"
    SPEAKING = "speaking"
    EXECUTING = "executing"

class StateManager:
    """Manages visual state transitions"""
    
    def __init__(self):
        self.current_state = VisualState.IDLE
        self.state_start_time = time.time()
        self.execute_progress = 0.0
        
        # Transition parameters
        self.blur_intensity = 0.0  # 0.0 to 1.0
        self.target_blur = 0.0
        self.blur_speed = 0.1
        
    def set_state(self, new_state):
        """Change to new visual state"""
        if new_state != self.current_state:
            print(f"State: {self.current_state.value} -> {new_state.value}")
            self.current_state = new_state
            self.state_start_time = time.time()
            
            # Set blur targets
            if new_state == VisualState.IDLE:
                self.target_blur = 0.0
            elif new_state == VisualState.LISTENING:
                self.target_blur = 15.0  # 15px blur
            elif new_state == VisualState.SPEAKING:
                self.target_blur = 25.0  # 25px blur
            elif new_state == VisualState.EXECUTING:
                self.target_blur = 20.0
            
            # Reset execute progress
            if new_state == VisualState.EXECUTING:
                self.execute_progress = 0.0
    
    def update(self, dt):
        """Update state transitions"""
        # Smooth blur transition
        if self.blur_intensity < self.target_blur:
            self.blur_intensity = min(
                self.blur_intensity + self.blur_speed * dt * 60,
                self.target_blur
            )
        elif self.blur_intensity > self.target_blur:
            self.blur_intensity = max(
                self.blur_intensity - self.blur_speed * dt * 60,
                self.target_blur
            )
        
        # Update execute progress
        if self.current_state == VisualState.EXECUTING:
            elapsed = time.time() - self.state_start_time
            self.execute_progress = min(elapsed / 0.5, 1.0)  # 0.5 second pulse
            
            # Auto-return to idle
            if self.execute_progress >= 1.0:
                self.set_state(VisualState.IDLE)
    
    def get_state(self):
        """Get current state"""
        return self.current_state
    
    def get_blur_intensity(self):
        """Get current blur intensity (0-25px)"""
        return self.blur_intensity
    
    def get_execute_progress(self):
        """Get execution progress (0.0 to 1.0)"""
        return self.execute_progress
    
    def get_state_duration(self):
        """Get time in current state"""
        return time.time() - self.state_start_time
