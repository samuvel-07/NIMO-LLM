// JARVIS Desktop - State Management
// Refined for calm, minimal, system-native behaviors

export const STATES = {
    IDLE: 'IDLE',
    LISTENING: 'LISTENING',
    RESPONDING: 'RESPONDING',
    EXECUTING: 'EXECUTING',
    SUCCESS: 'SUCCESS',
    ERROR: 'ERROR',
    CONFIRM: 'CONFIRM',
    DENIED: 'DENIED',
    SHUTDOWN: 'SHUTDOWN'
};

// Master Spec State Parameters
const STATE_CONFIG = {
    IDLE: {
        expansion: 0.93,   // User Request: Safe size, not too small
        glow: 0.0,
        ripple: 0.0,
        audioScale: 0.0,
        particleSize: 10.0
    },
    LISTENING: {
        expansion: 1.0,    // Max 1.0 to avoid clipping
        glow: 0.1,
        ripple: 0.0,
        audioScale: 0.1,
        particleSize: 12.0
    },
    RESPONDING: {
        expansion: 1.05,
        glow: 0.05,
        ripple: 0.1, // Added ripple for activity
        audioScale: 1.0,
        particleSize: 11.0
    },
    EXECUTING: {
        expansion: 1.1,    // Larger expansion
        glow: 0.2,         // Brighter
        ripple: 0.5,       // Fast ripple
        audioScale: 0.5,
        particleSize: 12.0
    },
    SUCCESS: {
        expansion: 1.15,   // Pulse out
        glow: 0.3,         // Flash
        ripple: 0.0,
        audioScale: 0.0,
        particleSize: 14.0
    },
    ERROR: {
        expansion: 0.85,   // Shrink
        glow: 0.0,
        ripple: 0.0,
        audioScale: 0.0,
        particleSize: 8.0  // Small particles
    },
    CONFIRM: {
        expansion: 1.0,
        glow: 0.5,         // High glow (Attention)
        ripple: 0.2,
        audioScale: 0.0,
        particleSize: 12.0
    },
    DENIED: {
        expansion: 0.9,
        glow: 0.0,
        ripple: 0.0,
        audioScale: 0.0,
        particleSize: 9.0
    },
    SHUTDOWN: {
        expansion: 0.8,
        glow: 0.0,
        ripple: 0.0,
        audioScale: 0.0,
        particleSize: 0.1
    }
};

// Tuned for 60fps
const LERP_RATE = 0.08;      // Faster, smoother transitions (requested 0.08)
const AUDIO_LERP_RATE = 0.1; // Responsive but fluid audio

export class StateManager {
    constructor() {
        this.currentState = STATES.IDLE;
        this.targetConfig = { ...STATE_CONFIG.IDLE };
        this.liveConfig = { ...STATE_CONFIG.IDLE };
        this.audioLevel = 0.0;
        this.targetAudio = 0.0;
        this.rippleTime = 0.0;
        this.shutdownFade = 0.0;
        this.targetShutdownFade = 0.0;

        this._snapshot = this._buildSnapshot();
    }

    setState(state, audio = 0) {
        if (!STATE_CONFIG[state]) return;

        this.currentState = state;
        this.targetConfig = { ...STATE_CONFIG[state] };
        this.targetAudio = audio;

        if (state === STATES.RESPONDING) {
            this.rippleTime = 0;
        }

        if (state === STATES.SHUTDOWN) {
            this.targetShutdownFade = 1.0;
        }
    }

    setAudio(level) {
        this.targetAudio = Math.max(0, Math.min(1, level));
    }

    update(dt) {
        const factor = 1 - Math.pow(1 - LERP_RATE, dt * 60);
        const audioFactor = 1 - Math.pow(1 - AUDIO_LERP_RATE, dt * 60);

        // Interpolate visual parameters
        this.liveConfig.expansion = this._lerp(this.liveConfig.expansion, this.targetConfig.expansion, factor);
        this.liveConfig.glow = this._lerp(this.liveConfig.glow, this.targetConfig.glow, factor);
        this.liveConfig.ripple = this._lerp(this.liveConfig.ripple, this.targetConfig.ripple, factor);
        this.liveConfig.particleSize = this._lerp(this.liveConfig.particleSize, this.targetConfig.particleSize, factor);

        // Smooth audio
        this.audioLevel = this._lerp(this.audioLevel, this.targetAudio * this.targetConfig.audioScale, audioFactor);

        // Shutdown fade (approx 300ms linear-ish)
        if (this.targetShutdownFade > 0.5) {
            this.shutdownFade += dt * 3.3;
            this.shutdownFade = Math.min(1.0, this.shutdownFade);
        } else {
            this.shutdownFade = this._lerp(this.shutdownFade, 0.0, factor);
        }

        // Ripple time
        if (this.liveConfig.ripple > 0.01) {
            this.rippleTime += dt;
        }

        this._snapshot = this._buildSnapshot();
    }

    getUniforms() {
        return this._snapshot;
    }

    _buildSnapshot() {
        return Object.freeze({
            expansion: this.liveConfig.expansion,
            glow: this.liveConfig.glow,
            audio: this.audioLevel,
            ripple: this.liveConfig.ripple,
            rippleTime: this.rippleTime,
            shutdownFade: this.shutdownFade,
            particleSize: this.liveConfig.particleSize
        });
    }

    _lerp(a, b, t) {
        return a + (b - a) * t;
    }
}
