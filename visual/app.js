// JARVIS Three.js Visual Engine - SIMPLIFIED WORKING VERSION
// Core particle system without post-processing (for testing)

import * as THREE from 'three';
import { vertexShader, fragmentShader } from './shaders.js';
import { performGracefulShutdown, emergencyShutdown } from './shutdown_animation.js';

console.log("JARVIS initializing...");

//====================================================================
// SCENE SETUP
//====================================================================

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x05070D); // Deep black
scene.fog = new THREE.FogExp2(0x05070D, 0.15);

const camera = new THREE.PerspectiveCamera(
    75,
    window.innerWidth / window.innerHeight,
    0.1,
    1000
);
camera.position.z = 8;

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(window.devicePixelRatio);
document.body.appendChild(renderer.domElement);

console.log("✓ Scene setup complete");

//====================================================================
// PARTICLE SYSTEM - 800 particles with cube root distribution
//====================================================================

const particleCount = 800;
const geometry = new THREE.BufferGeometry();
const positions = new Float32Array(particleCount * 3);

// Generate volumetric sphere with cube root for uniform density
for (let i = 0; i < particleCount; i++) {
    const u = Math.random();
    const v = Math.random();
    const theta = 2 * Math.PI * u;
    const phi = Math.acos(2 * v - 1);

    // CRITICAL: Cube root prevents center clustering
    const r = 3.5 * Math.cbrt(Math.random());

    positions[i * 3] = r * Math.sin(phi) * Math.cos(theta);
    positions[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
    positions[i * 3 + 2] = r * Math.cos(phi);
}

geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));

console.log(`✓ Created ${particleCount} particles`);

//====================================================================
// SHADER MATERIAL
//====================================================================

const material = new THREE.ShaderMaterial({
    uniforms: {
        uTime: { value: 0 },
        uAudio: { value: 0 },
        uStateExpansion: { value: 1.0 }
    },
    vertexShader: vertexShader,
    fragmentShader: fragmentShader,
    blending: THREE.AdditiveBlending,
    transparent: true,
    depthWrite: false
});

const particles = new THREE.Points(geometry, material);
scene.add(particles);

console.log("✓ Particles added to scene");

//====================================================================
// STATE MANAGEMENT
//====================================================================

let currentState = "IDLE";
let targetExpansion = 1.0;
let currentExpansion = 1.0;
let audioLevel = 0.0;
let targetAudio = 0.0;

const stateExpansions = {
    "IDLE": 1.0,
    "LISTENING": 1.2,
    "PROCESSING": 1.05,
    "RESPONDING": 1.0
};

function setState(state, audio = 0) {
    currentState = state;
    targetExpansion = stateExpansions[state] || 1.0;
    targetAudio = audio;

    console.log(`State: ${state} | Expansion: ${targetExpansion.toFixed(2)} | Audio: ${audio.toFixed(2)}`);
    updateStatus(`State: ${state}`);
}

//====================================================================
// STATUS UPDATES
//====================================================================

function updateStatus(message) {
    const statusText = document.getElementById('status-text');
    const debugText = document.getElementById('debug-text');
    const debugDiv = document.getElementById('debug');

    if (statusText) statusText.textContent = message;
    if (debugText && debugDiv) {
        const time = new Date().toLocaleTimeString();
        debugText.innerHTML += `<br>${time}: ${message}`;
        debugDiv.style.display = 'block';
    }
    console.log(message);
}

//====================================================================
// WEBSOCKET CONNECTION
//====================================================================

let socket;
let reconnectTimer;

function connectWebSocket() {
    updateStatus("Connecting to ws://localhost:8765...");

    try {
        socket = new WebSocket("ws://localhost:8765");

        socket.onopen = () => {
            console.log("✅ WebSocket connected");
            updateStatus("✅ Connected to JARVIS backend");
            document.body.classList.remove('disconnected');
        };

        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            setState(data.state, data.audio);
        };

        socket.onclose = (event) => {
            console.log(`❌ WebSocket closed (code: ${event.code})`);
            updateStatus(`Disconnected. Retrying...`);
            document.body.classList.add('disconnected');
            reconnectTimer = setTimeout(connectWebSocket, 2000);
        };

        socket.onerror = (error) => {
            console.error("WebSocket error:", error);
            updateStatus("❌ Connection error");
        };
    } catch (e) {
        console.error("Failed to create WebSocket:", e);
        updateStatus(`❌ ${e.message}`);
        reconnectTimer = setTimeout(connectWebSocket, 2000);
    }
}

//====================================================================
// ANIMATION LOOP
//====================================================================

const clock = new THREE.Clock();
let animationId;

function animate() {
    animationId = requestAnimationFrame(animate);

    const elapsed = clock.getElapsedTime();

    // Update shader uniforms
    material.uniforms.uTime.value = elapsed;

    // Smooth interpolation
    currentExpansion = THREE.MathUtils.lerp(currentExpansion, targetExpansion, 0.05);
    material.uniforms.uStateExpansion.value = currentExpansion;

    audioLevel = THREE.MathUtils.lerp(audioLevel, targetAudio, 0.1);
    material.uniforms.uAudio.value = audioLevel;

    // Render
    renderer.render(scene, camera);
}

//====================================================================
// WINDOW RESIZE
//====================================================================

function onWindowResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
}

window.addEventListener('resize', onWindowResize);

//====================================================================
// KEYBOARD CONTROLS
//====================================================================

window.addEventListener('keydown', (e) => {
    if (e.key === '1') setState("IDLE", 0);
    if (e.key === '2') setState("LISTENING", 0.1);
    if (e.key === '3') setState("PROCESSING", 0.05);
    if (e.key === '4') setState("RESPONDING", 0.5);
    if (e.key === 's' || e.key === 'S') {
        console.log("Graceful shutdown triggered by user");
        window.performGracefulShutdown();
    }
    if (e.key === 'Escape') window.close();
    if (e.key === 'd') {
        const debug = document.getElementById('debug');
        debug.style.display = debug.style.display === 'none' ? 'block' : 'none';
    }
});

//====================================================================
// CLEANUP
//====================================================================

// Store shutdown state
let isShuttingDown = false;

// Graceful shutdown function (exposed to window for external triggering)
window.performGracefulShutdown = async () => {
    if (isShuttingDown) {
        console.warn("Shutdown already in progress");
        return;
    }

    isShuttingDown = true;

    await performGracefulShutdown({
        scene,
        particles,
        material,
        geometry,
        renderer,
        socket,
        animationId,
        updateStatus
    });
};

// Emergency shutdown (no animation)
window.emergencyShutdown = () => {
    emergencyShutdown({
        geometry,
        material,
        renderer,
        socket,
        animationId
    });
};

// Quick cleanup on window close
window.addEventListener('beforeunload', () => {
    if (!isShuttingDown) {
        cancelAnimationFrame(animationId);
        if (socket) socket.close();
        geometry.dispose();
        material.dispose();
        renderer.dispose();
    }
});

//====================================================================
// STARTUP
//====================================================================

console.log("=".repeat(60));
console.log("JARVIS Neural Core - ONLINE");
console.log("=".repeat(60));
console.log("Controls: 1=IDLE 2=LISTENING 3=PROCESSING 4=RESPONDING");
console.log("S=Graceful Shutdown | D=Toggle debug | ESC=Exit");
console.log("=".repeat(60));

animate();
console.log("✓ Animation started");

updateStatus("Initializing...");
connectWebSocket();
