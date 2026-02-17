// JARVIS GLSL Shaders - Vertex and Fragment

export const vertexShader = `
uniform float uTime;
uniform float uAudio;
uniform float uStateExpansion;

varying float vDepth;
varying vec3 vPosition;

// Simplified 3D noise function
float noise(vec3 p) {
    return fract(sin(dot(p, vec3(12.9898, 78.233, 45.164))) * 43758.5453);
}

void main() {
    vec3 pos = position;
    
    // Slow Y-axis rotation
    float angle = uTime * 0.15;
    float c = cos(angle);
    float s = sin(angle);
    mat3 rotY = mat3(
        c, 0.0, s,
        0.0, 1.0, 0.0,
        -s, 0.0, c
    );
    
    pos = rotY * pos;
    
    // Breathing pulse
    float pulse = sin(uTime * 0.6) * 0.03;
    vec3 direction = normalize(pos);
    pos += direction * pulse;
    
    // Organic Perlin-like noise motion
    float n = noise(pos * 0.8 + vec3(uTime * 0.5));
    pos += direction * n * 0.15;
    
    // Audio-reactive expansion
    pos += direction * uAudio * 0.6;
    
    // State-based expansion
    pos *= uStateExpansion;
    
    // Transform to view space
    vec4 mvPosition = modelViewMatrix * vec4(pos, 1.0);
    
    // Depth for size scaling
    vDepth = -mvPosition.z;
    vPosition = pos;
    
    // Depth-based point size (closer = larger)
    gl_PointSize = 2.0 * (300.0 / vDepth);
    
    gl_Position = projectionMatrix * mvPosition;
}
`;

export const fragmentShader = `
precision mediump float;

varying float vDepth;
varying vec3 vPosition;

void main() {
    // Distance from center of point
    float d = length(gl_PointCoord - vec2(0.5));
    
    // Smooth circular falloff (no hard edges)
    float alpha = smoothstep(0.5, 0.1, d);
    
    // Color variation (cyan to blue gradient)
    vec3 cyan = vec3(0.0, 0.94, 1.0);   // #00F0FF
    vec3 blue = vec3(0.0, 0.47, 1.0);   // #0077FF
    
    // Mix based on distance from center and depth
    float mixFactor = d * 0.5 + (vDepth / 20.0) * 0.3;
    vec3 color = mix(cyan, blue, mixFactor);
    
    // Brighter core, dimmer edges
    color *= (1.0 - d * 0.5);
    
    gl_FragColor = vec4(color, alpha);
}
`;
