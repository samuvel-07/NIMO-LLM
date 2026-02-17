// JARVIS Desktop - Shutdown Orchestrator
// 4-phase ordered GPU disposal with animated fade-out

import { STATES } from './states.js';

/**
 * Performs a graceful 4-phase shutdown:
 *   Phase 1: Cancel rAF, close WebSocket, remove event listeners
 *   Phase 2: Animated fade-out (2s cubic ease-out)
 *   Phase 3: Dispose geometry → material → renderer
 *   Phase 4: Force WEBGL_lose_context, remove canvas
 *
 * @param {Object} engine - Engine state bag from core.js
 * @returns {Promise<void>} Resolves when all GPU resources are released
 */
export function performShutdown(engine) {
    const {
        renderer,
        scene,
        camera,
        geometry,
        material,
        particles,
        stateManager,
        getAnimFrameId,
        cancelLoop,
        socket,
        reconnectTimer,
        keydownHandler,
        visibilityHandler
    } = engine;

    return new Promise((resolve) => {
        console.log('[SHUTDOWN] Phase 1: Cancelling active loops');

        // ── Phase 1: Cancel everything asynchronous ──────────────
        cancelLoop();

        if (reconnectTimer) clearTimeout(reconnectTimer);

        if (socket && socket.readyState === WebSocket.OPEN) {
            socket.close(1000, 'Graceful shutdown');
        }

        if (keydownHandler) {
            window.removeEventListener('keydown', keydownHandler);
        }
        if (visibilityHandler) {
            document.removeEventListener('visibilitychange', visibilityHandler);
        }

        console.log('[SHUTDOWN] Phase 2: Fade-out animation');

        // ── Phase 2: Animated fade-out ───────────────────────────
        const DURATION = 2000;
        const startTime = performance.now();
        const startExpansion = material.uniforms.uExpansion.value;
        const startGlow = material.uniforms.uGlow.value;
        const startShutdownFade = material.uniforms.uShutdownFade.value;

        function easeOutCubic(t) {
            return 1 - Math.pow(1 - t, 3);
        }

        function fadeStep(now) {
            const elapsed = now - startTime;
            const progress = Math.min(elapsed / DURATION, 1.0);
            const eased = easeOutCubic(progress);

            // Drive uniforms toward zero
            material.uniforms.uExpansion.value = startExpansion * (1 - eased);
            material.uniforms.uGlow.value = startGlow * (1 - eased);
            material.uniforms.uShutdownFade.value = startShutdownFade + (1.0 - startShutdownFade) * eased;
            material.uniforms.uTime.value += 0.016; // keep time advancing

            // Render this frame
            renderer.render(scene, camera);

            if (progress < 1.0) {
                requestAnimationFrame(fadeStep);
            } else {
                completeDisposal();
            }
        }

        function completeDisposal() {
            console.log('[SHUTDOWN] Phase 3: Disposing GPU resources');

            // ── Phase 3: Ordered GPU disposal ────────────────────
            // Order matters: scene objects → buffers → material → renderer → context
            try {
                // Remove objects from scene first (prevents dangling refs)
                if (particles && scene) {
                    scene.remove(particles);
                }

                // Clear all remaining scene children
                while (scene && scene.children.length > 0) {
                    scene.remove(scene.children[0]);
                }

                // Dispose geometry + release buffer attributes explicitly
                if (geometry) {
                    // Delete individual buffer attributes to free GPU memory
                    const attribNames = Object.keys(geometry.attributes);
                    for (const name of attribNames) {
                        geometry.deleteAttribute(name);
                    }
                    if (geometry.index) geometry.setIndex(null);
                    geometry.dispose();
                    console.log('[SHUTDOWN] ✓ Geometry + buffer attributes disposed');
                }

                // Dispose material (releases compiled shader program + uniforms)
                if (material) {
                    material.dispose();
                    console.log('[SHUTDOWN] ✓ Material + shader program disposed');
                }

                if (renderer) {
                    // Grab raw GL context before dispose clears references
                    const gl = renderer.getContext();

                    // Clear internal render lists (draw call queues)
                    if (renderer.renderLists) {
                        renderer.renderLists.dispose();
                    }

                    // Three.js dispose: releases all managed textures,
                    // render targets, and internal caches
                    renderer.dispose();
                    console.log('[SHUTDOWN] ✓ Renderer disposed');

                    // ── Phase 4: Force context loss ──────────────
                    console.log('[SHUTDOWN] Phase 4: Forcing GPU context loss');

                    // Use Three.js canonical method first
                    try {
                        renderer.forceContextLoss();
                        console.log('[SHUTDOWN] ✓ forceContextLoss() called');
                    } catch (e) {
                        // Fallback: directly use the WEBGL_lose_context extension
                        if (gl) {
                            const loseExt = gl.getExtension('WEBGL_lose_context');
                            if (loseExt) {
                                loseExt.loseContext();
                                console.log('[SHUTDOWN] ✓ WEBGL_lose_context fallback');
                            }
                        }
                    }

                    // Remove canvas from DOM — prevent any further compositor interaction
                    const canvas = renderer.domElement;
                    if (canvas && canvas.parentElement) {
                        canvas.parentElement.removeChild(canvas);
                        console.log('[SHUTDOWN] ✓ Canvas removed from DOM');
                    }
                }
            } catch (err) {
                console.error('[SHUTDOWN] Error during disposal:', err);
            }

            // Update UI
            const label = document.getElementById('state-label');
            if (label) {
                label.textContent = 'OFFLINE';
                label.style.color = 'rgba(255, 60, 60, 0.4)';
            }

            console.log('[SHUTDOWN] Complete — all GPU resources released');
            resolve();
        }

        // Start the fade-out
        requestAnimationFrame(fadeStep);
    });
}

/**
 * Emergency shutdown — immediate disposal, no animation.
 * Use when the page is being torn down (beforeunload/pagehide).
 */
export function emergencyShutdown(engine) {
    const { renderer, geometry, material, particles, scene, socket, reconnectTimer, cancelLoop } = engine;

    console.warn('[SHUTDOWN] Emergency — immediate disposal');

    if (cancelLoop) cancelLoop();
    if (reconnectTimer) clearTimeout(reconnectTimer);

    if (socket && socket.readyState === WebSocket.OPEN) {
        socket.close(1000, 'Emergency shutdown');
    }

    // Remove from scene
    if (particles && scene) scene.remove(particles);

    // Dispose geometry + buffer attributes
    if (geometry) {
        const attribNames = Object.keys(geometry.attributes);
        for (const name of attribNames) {
            geometry.deleteAttribute(name);
        }
        if (geometry.index) geometry.setIndex(null);
        geometry.dispose();
    }

    // Dispose material (shader program + uniforms)
    if (material) material.dispose();

    if (renderer) {
        const gl = renderer.getContext();

        // Clear render lists
        if (renderer.renderLists) renderer.renderLists.dispose();

        renderer.dispose();

        // Force context loss — canonical method + fallback
        try {
            renderer.forceContextLoss();
        } catch (e) {
            if (gl) {
                const loseExt = gl.getExtension('WEBGL_lose_context');
                if (loseExt) loseExt.loseContext();
            }
        }

        // Remove canvas
        const canvas = renderer.domElement;
        if (canvas && canvas.parentElement) {
            canvas.parentElement.removeChild(canvas);
        }
    }

    console.log('[SHUTDOWN] Emergency disposal complete');
}
