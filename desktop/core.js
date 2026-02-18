// JARVIS Desktop - Core Visual Engine v3.0
// Flicker-free rendering with IPC-coordinated lifecycle cleanup

import * as THREE from 'three';
import { vertexShader, fragmentShader } from './shaders.js';
import { StateManager, STATES } from './states.js';
import { performShutdown, emergencyShutdown } from './shutdown.js';

// ====================================================================
// CONFIGURATION
// ====================================================================

const CONFIG = {
    // Container config is overridden by dynamic resizing
    particles: { count: 1000, radius: 3.4 },
    camera: { fov: 50, near: 0.1, far: 50, z: 8.0 }, // User Requested: Z 8
    ws: { url: 'ws://localhost:8765', reconnectInterval: 5000 }
};

// ====================================================================
// ENGINE STATE — single source of truth
// ====================================================================

let animFrameId = null;
let isRunning = false;
let isShuttingDown = false;
let socket = null;
let reconnectTimer = null;

// ====================================================================
// SCENE SETUP
// ====================================================================

const container = document.getElementById('container');
const stateLabel = document.getElementById('state-label');

const scene = new THREE.Scene();
scene.background = null; // transparent — acrylic blur shows through

const camera = new THREE.PerspectiveCamera(
    CONFIG.camera.fov, 1, CONFIG.camera.near, CONFIG.camera.far
);
camera.position.z = CONFIG.camera.z;

const renderer = new THREE.WebGLRenderer({
    antialias: true,  // Important for crisp points
    alpha: true,  // transparent canvas — let acrylic blur show through
    powerPreference: 'high-performance',
    preserveDrawingBuffer: false
});
renderer.setClearColor(0x000000, 0); // fully transparent clear
// Initial size set by resizeRenderer
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
container.appendChild(renderer.domElement);

// ====================================================================
// MICRO-PARTICLE SPHERE — 1000 particles, Hybrid Shell/Volume
// ====================================================================

const particleCount = CONFIG.particles.count;
const sphereRadius = CONFIG.particles.radius;
const geometry = new THREE.BufferGeometry();
const positions = new Float32Array(particleCount * 3);
const sizes = new Float32Array(particleCount); // New Size Attribute

// Hybrid Distribution (User Requested: 35% Shell)
const shellCount = Math.floor(particleCount * 0.35);

for (let i = 0; i < particleCount; i++) {
    const u = Math.random();
    const v = Math.random();
    const theta = 2.0 * Math.PI * u;
    const phi = Math.acos(2.0 * v - 1.0);

    let r;
    if (i < shellCount) {
        // SHELL (Edge)
        r = sphereRadius;
        sizes[i] = 10.0; // User Requested: Edge size 10
    } else {
        // VOLUME (Base/Inside)
        r = sphereRadius * Math.cbrt(Math.random());
        sizes[i] = 8.0;  // User Requested: Base size 8
    }

    const x = r * Math.sin(phi) * Math.cos(theta);
    const y = r * Math.sin(phi) * Math.sin(theta);
    const z = r * Math.cos(phi);

    positions[i * 3] = x;
    positions[i * 3 + 1] = y;
    positions[i * 3 + 2] = z;
}

geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
geometry.setAttribute('aSize', new THREE.BufferAttribute(sizes, 1));

// ====================================================================
// SHADER MATERIAL
// ====================================================================

const material = new THREE.ShaderMaterial({
    uniforms: {
        uTime: { value: 0 },
        uAudio: { value: 0 },
        uExpansion: { value: 1.0 },
        uGlow: { value: 0.0 }, // Disabled bloom
        uRipple: { value: 0.0 },
        uRippleTime: { value: 0.0 },
        uShutdownFade: { value: 0.0 },
        uState: { value: 0.0 }, // 0=IDLE, 1=LISTENING, 2=RESPONDING
        uSize: { value: 24.0 } // Balanced size (was 60.0)
    },
    vertexShader: vertexShader,
    fragmentShader: fragmentShader,
    blending: THREE.NormalBlending, // Switch to Normal for solid circles
    transparent: true,
    depthWrite: false,
    depthTest: false
});

const particles = new THREE.Points(geometry, material);
scene.add(particles);

// ====================================================================
// DYNAMIC RESIZING (DISABLED - FIXED SIZE)
// ====================================================================

function resizeRenderer() {
    // FIXED SIZE: 240px (User Requested Step 4 - Visual Margin)
    const size = 240;

    renderer.setSize(size, size);

    // Maintain 1:1 aspect for the sphere canvas
    camera.aspect = 1;
    camera.updateProjectionMatrix();
}

window.addEventListener('resize', resizeRenderer);
resizeRenderer(); // Initial sizing

// ====================================================================
// STATE MANAGEMENT
// ====================================================================

const stateManager = new StateManager();

// ====================================================================
// WEBSOCKET CONNECTION
// ====================================================================

function connectWebSocket() {
    if (isShuttingDown) return;

    try {
        // 🔥 REAL FIX: Prevent duplicate connections
        if (window.socket) {
            window.socket.close();
        }

        window.socket = new WebSocket(CONFIG.ws.url);
        socket = window.socket; // Sync local reference

        socket.onopen = () => console.log('[JARVIS] WebSocket connected');

        socket.onmessage = (event) => {
            if (isShuttingDown) return;
            try {
                const data = JSON.parse(event.data);

                // --- Legacy State Handling ---
                if (data.state) {
                    stateManager.setState(data.state, data.audio || 0);
                    updateStateLabel(data.state);

                    const u = material.uniforms;
                    if (data.state === 'IDLE') u.uState.value = 0.0;
                    if (data.state === 'LISTENING') u.uState.value = 1.0;
                    if (data.state === 'RESPONDING') u.uState.value = 2.0;
                }

                // --- Brain Event Handling ---
                // Map Brain Events to Visual States
                if (data.type) {
                    let nextState = null;
                    let nextAudio = 0.0;

                    switch (data.type) {
                        case 'DECISION':
                            // Brain is thinking/deciding
                            // If action is EXECUTE, maybe we go to EXECUTING soon?
                            // For now, DECISION might be instant, but let's show activity
                            // If confidence is high, maybe RESPONDING? 
                            // Let's use RESPONDING for "Thinking" visual for now
                            if (data.payload && data.payload.action === 'CLARIFY') {
                                nextState = STATES.RESPONDING;
                            } else {
                                nextState = STATES.RESPONDING;
                            }
                            break;

                        case 'EXECUTION_START':
                            nextState = STATES.EXECUTING;
                            nextAudio = 0.5;
                            break;

                        case 'EXECUTION_SUCCESS':
                            nextState = STATES.SUCCESS;
                            // Auto-return to IDLE after a moment? 
                            // For now, stick to SUCCESS, maybe Orchestrator sends IDLE later?
                            // Or we set a timeout? 
                            // The visual engine is reactive. Let's just set state.
                            setTimeout(() => {
                                if (stateManager.currentState === STATES.SUCCESS) {
                                    stateManager.setState(STATES.IDLE);
                                    updateStateLabel('IDLE');
                                    material.uniforms.uState.value = 0.0;
                                }
                            }, 2000);
                            break;

                        case 'EXECUTION_FAILURE':
                            nextState = STATES.ERROR;
                            setTimeout(() => {
                                if (stateManager.currentState === STATES.ERROR) {
                                    stateManager.setState(STATES.IDLE);
                                    updateStateLabel('IDLE');
                                    material.uniforms.uState.value = 0.0;
                                }
                            }, 2000);
                            break;

                        case 'CONFIRMATION_REQUIRED':
                            nextState = STATES.CONFIRM;
                            break;

                        case 'CONFIRMATION_ACCEPTED':
                            nextState = STATES.EXECUTING; // Transition to executing
                            break;

                        case 'CONFIRMATION_PENDING_BLOCKED':
                            nextState = STATES.CONFIRM; // Re-assert Amber state
                            break;

                        case 'CONFIRMATION_CANCELLED':
                            nextState = STATES.IDLE;
                            // Maybe a visual cue for cancel? 
                            // For now IDLE is fine.
                            break;

                        case 'CONFIRMATION_EXPIRED':
                            nextState = STATES.ERROR; // Soft error/fade
                            setTimeout(() => {
                                if (stateManager.currentState === STATES.ERROR) {
                                    stateManager.setState(STATES.IDLE);
                                    updateStateLabel('IDLE');
                                    material.uniforms.uState.value = 0.0;
                                }
                            }, 2000);
                            break;

                        case 'PERMISSION_DENIED':
                            nextState = STATES.DENIED;
                            setTimeout(() => {
                                if (stateManager.currentState === STATES.DENIED) {
                                    stateManager.setState(STATES.IDLE);
                                    updateStateLabel('IDLE');
                                    material.uniforms.uState.value = 0.0;
                                }
                            }, 2000);
                            break;
                    }

                    if (nextState) {
                        stateManager.setState(nextState, nextAudio);
                        updateStateLabel(nextState);

                        // Uniform mappings for shader
                        const u = material.uniforms;
                        if (nextState === STATES.IDLE) u.uState.value = 0.0;
                        if (nextState === STATES.LISTENING) u.uState.value = 1.0;
                        if (nextState === STATES.RESPONDING) u.uState.value = 2.0;
                        if (nextState === STATES.EXECUTING) u.uState.value = 2.0; // Same as responding for now
                        if (nextState === STATES.SUCCESS) u.uState.value = 1.0;   // Listening blue? Or add new?
                        if (nextState === STATES.ERROR) u.uState.value = 0.0;
                        if (nextState === STATES.CONFIRM) u.uState.value = 2.0;
                        if (nextState === STATES.DENIED) u.uState.value = 0.0;
                    }
                }

                if (data.audio !== undefined) {
                    stateManager.setAudio(data.audio);
                }
            } catch (e) { /* malformed */ }
        };

        socket.onclose = () => {
            if (!isShuttingDown) scheduleReconnect();
        };

        socket.onerror = () => { };
    } catch (e) {
        if (!isShuttingDown) scheduleReconnect();
    }
}

function scheduleReconnect() {
    if (reconnectTimer) clearTimeout(reconnectTimer);
    if (isShuttingDown) return;
    reconnectTimer = setTimeout(connectWebSocket, CONFIG.ws.reconnectInterval);
}

// ====================================================================
// UI — JS-driven label color (no CSS transitions)
// ====================================================================

function updateStateLabel(state) {
    if (!stateLabel) return;
    stateLabel.textContent = state;
    stateLabel.style.color = state !== 'IDLE'
        ? 'rgba(0, 212, 255, 0.6)'
        : 'rgba(0, 212, 255, 0.35)';
}

// ====================================================================
// KEYBOARD CONTROLS
// ====================================================================

function keydownHandler(e) {
    if (isShuttingDown) return;

    switch (e.key) {
        case '1':
            stateManager.setState(STATES.IDLE, 0);
            updateStateLabel('IDLE');
            material.uniforms.uState.value = 0.0;
            break;
        case '2':
            stateManager.setState(STATES.LISTENING, 0.1);
            updateStateLabel('LISTENING');
            material.uniforms.uState.value = 1.0;
            break;
        case '3':
            stateManager.setState(STATES.RESPONDING, 0.5);
            updateStateLabel('RESPONDING');
            material.uniforms.uState.value = 2.0;
            break;
        case 's':
        case 'S':
            initiateGracefulShutdown();
            break;
    }
}

window.addEventListener('keydown', keydownHandler);

// ====================================================================
// VISIBILITY HANDLING — pause GPU when tab is hidden
// ====================================================================

function visibilityHandler() {
    if (isShuttingDown) return;

    if (document.hidden) {
        if (animFrameId !== null) {
            cancelAnimationFrame(animFrameId);
            animFrameId = null;
            isRunning = false;
            console.log('[JARVIS] Paused (hidden)');
        }
    } else {
        if (!isRunning && !isShuttingDown) {
            isRunning = true;
            clock.getDelta();
            animFrameId = requestAnimationFrame(animate);
            console.log('[JARVIS] Resumed (visible)');
        }
    }
}

document.addEventListener('visibilitychange', visibilityHandler);

// ====================================================================
// ANIMATION LOOP — tracked rAF with batched uniform writes
// ====================================================================

const clock = new THREE.Clock();

function animate() {
    if (!isRunning || isShuttingDown) return;

    animFrameId = requestAnimationFrame(animate);

    const dt = clock.getDelta();
    const elapsed = clock.getElapsedTime();

    stateManager.update(dt);
    const snap = stateManager.getUniforms();

    // Batch all uniform writes before single render call
    const u = material.uniforms;
    u.uTime.value = elapsed;
    u.uExpansion.value = snap.expansion;
    u.uGlow.value = snap.glow;
    u.uAudio.value = snap.audio;
    u.uRipple.value = snap.ripple;
    u.uRippleTime.value = snap.rippleTime;
    u.uShutdownFade.value = snap.shutdownFade;

    renderer.render(scene, camera);
}

// ====================================================================
// SHUTDOWN — IPC-coordinated lifecycle cleanup
// ====================================================================

function cancelLoop() {
    isRunning = false;
    if (animFrameId !== null) {
        cancelAnimationFrame(animFrameId);
        animFrameId = null;
    }
}

function getEngineState() {
    return {
        renderer, scene, camera, geometry, material, particles,
        stateManager,
        getAnimFrameId: () => animFrameId,
        cancelLoop,
        socket, reconnectTimer,
        keydownHandler, visibilityHandler
    };
}

async function initiateGracefulShutdown() {
    if (isShuttingDown) return;
    isShuttingDown = true;
    cancelLoop();

    console.log('[JARVIS] Graceful shutdown initiated');
    await performShutdown(getEngineState());
    console.log('[JARVIS] GPU resources released');

    // Notify main process that renderer disposal is complete
    if (window.jarvis && window.jarvis.notifyShutdownComplete) {
        window.jarvis.notifyShutdownComplete();
        console.log('[JARVIS] Notified main process — safe to quit');
    }
}

function onPageTeardown() {
    if (isShuttingDown) return;
    isShuttingDown = true;
    emergencyShutdown(getEngineState());

    if (window.jarvis && window.jarvis.notifyShutdownComplete) {
        window.jarvis.notifyShutdownComplete();
    }

    // 🔥 Cleanup On Unload
    if (window.socket) {
        window.socket.close();
    }
}

// Wire to page lifecycle
window.addEventListener('beforeunload', onPageTeardown);
window.addEventListener('pagehide', onPageTeardown);

// Wire to IPC shutdown from main process (window close / app.quit)
if (window.jarvis && window.jarvis.onShutdownRequest) {
    window.jarvis.onShutdownRequest(() => {
        console.log('[JARVIS] Shutdown requested by main process');
        initiateGracefulShutdown();
    });
}

// ====================================================================
// START
// ====================================================================

console.log('[JARVIS] Neural Core v3.0 — Electron Native');
console.log('[JARVIS] Particles:', particleCount);
console.log('[JARVIS] Controls: 1=IDLE  2=LISTENING  3=RESPONDING  S=SHUTDOWN');

// DEBUG: User Requested Checks
console.log('[JARVIS] DEBUG: Geometry Count:', geometry.attributes.position.count);
console.log('[JARVIS] DEBUG: isWebGL2:', renderer.capabilities.isWebGL2);

isRunning = true;
animFrameId = requestAnimationFrame(animate);
connectWebSocket();
