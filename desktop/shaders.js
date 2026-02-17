// JARVIS Desktop - GLSL Shaders
// Ultra-fine micro-particle rendering for compact 150px sphere
// Master Professional Prompt Spec: Electric Cyan, Micro-Motion, No Bloom

export const vertexShader = `
uniform float uTime;
uniform float uExpansion;
uniform float uAudio;
uniform float uSize; // Passed as 60.0 from core.js
uniform float uState; // 0=IDLE, 1=LISTENING, 2=RESPONDING

varying float vDepth;
varying float vDistFromCenter;

attribute float aSize; // Custom attribute from core.js

void main() {
    vec3 pos = position;
    vDistFromCenter = length(pos);

    // ----- STATE BASED MOTION -----
    
    // IDLE (0.0): Breathing Intelligence (User Requested)
    if (uState < 0.5) {
        // Slow Rotation
        float angle = uTime * 0.15;
        vec3 rotated;
        rotated.x = cos(angle) * position.x - sin(angle) * position.z;
        rotated.z = sin(angle) * position.x + cos(angle) * position.z;
        rotated.y = position.y;
        
        // Micro Breathing
        float breathe = sin(uTime * 1.2) * 0.02;
        pos = rotated * (1.0 + breathe);
    }
    
    // LISTENING (1.0): Focus Pull (User Requested)
    else if (uState < 1.5) {
        // Subtle pull toward center (Focusing)
        float focus = 0.03 * sin(uTime * 3.0);
        pos *= (1.0 - focus);
    }
    
    // RESPONDING (2.0): Bass Wave Boom
    else {
        // Traveling radial wave
        float wave = sin(length(position) * 8.0 - uTime * 10.0);
        pos *= 1.0 + wave * 0.05; 
    }
    
    // ----- EXPANSION -----
    pos *= uExpansion;

    // ----- TRANSFORM & SIZING -----
    vec4 mvPosition = modelViewMatrix * vec4(pos, 1.0);
    vDepth = -mvPosition.z;

    // SAFER SIZE CALCULATION (User Requested)
    float size = 12.0 * (1.0 / -mvPosition.z);
    gl_PointSize = clamp(size, 4.0, 12.0); // Clamped 4-12 (True Round)
    
    gl_Position = projectionMatrix * mvPosition;
}
`;

export const fragmentShader = `
precision mediump float;

void main() {
    vec2 coord = gl_PointCoord - vec2(0.5);
    float dist = length(coord);

    if (dist > 0.5) discard;

    // Subtle Drop Glow (User Requested)
    float fade = smoothstep(0.6, 0.0, dist); 
    // Using 0.6 -> 0.0 allows center to be bright, edges fade slightly for "grounded" feel
    // Actually user asked for: float fade = smoothstep(0.6, 1.0, length(...)); 
    // But since we discard > 0.5, we need to adjust logic or remove discard for glow.
    // User constraint: "Hard Circle" was previous request.
    // User NEW request: "Subtle drop glow... float fade = smoothstep(0.6, 1.0, ...)"
    // If we use user's exact line on a discard>0.5, it won't be visible.
    // I will interpret "drop glow" as an alpha fade on the edge of the *existing* circle to make it look less "cut out".
    
    // Let's stick to the high-quality solid circle but maybe soften the very edge 
    // OR just use a solid alpha with the fade variable if that's what they meant.
    
    // Re-reading: "Add subtle drop glow under sphere"... "float fade = smoothstep(0.6, 1.0, length...)"
    // If I apply this inside the particle, it makes the particle glow.
    // I will apply a high-end softened edge to the particle itself using the user's math idea but adapted for 0.5 radius.
    
    float alpha = smoothstep(0.5, 0.3, dist); // Soft edge
    
    gl_FragColor = vec4(0.0, 0.9, 1.0, alpha); 
}
`;
