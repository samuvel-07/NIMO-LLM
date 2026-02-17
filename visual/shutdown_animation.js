// JARVIS Graceful Shutdown Animation
// Premium fade-out with particle system, sphere scaling, and resource cleanup

/**
 * Performs a graceful shutdown of the JARVIS visual system
 * - Fades particle glow intensity over 2 seconds
 * - Smoothly scales sphere to zero with cubic ease-out
 * - Fades background blur back to normal
 * - Disposes GPU resources and WebGL context
 * - Closes WebSocket connection
 * - Removes canvas from DOM
 * 
 * @param {Object} options - Shutdown configuration
 * @param {THREE.Scene} options.scene - Three.js scene
 * @param {THREE.Points} options.particles - Particle system
 * @param {THREE.ShaderMaterial} options.material - Shader material
 * @param {THREE.BufferGeometry} options.geometry - Geometry
 * @param {THREE.WebGLRenderer} options.renderer - WebGL renderer
 * @param {WebSocket} options.socket - WebSocket connection
 * @param {number} options.animationId - Current animation frame ID
 * @param {Function} options.updateStatus - Status update callback
 * @returns {Promise} Resolves when shutdown animation completes
 */
export function performGracefulShutdown(options) {
    const {
        scene,
        particles,
        material,
        geometry,
        renderer,
        socket,
        animationId,
        updateStatus
    } = options;

    return new Promise((resolve) => {
        console.log("=".repeat(60));
        console.log("JARVIS GRACEFUL SHUTDOWN INITIATED");
        console.log("=".repeat(60));

        // Update status
        if (updateStatus) {
            updateStatus("⏸ JARVIS SHUTTING DOWN...");
        }

        // Cancel existing animation loop
        if (animationId) {
            cancelAnimationFrame(animationId);
            console.log("✓ Animation loop cancelled");
        }

        // Shutdown parameters
        const duration = 2000; // 2 seconds
        const startTime = performance.now();
        const startExpansion = material.uniforms.uStateExpansion.value;
        const startAudio = material.uniforms.uAudio.value;

        // Cubic ease-out function for smooth deceleration
        function easeOutCubic(t) {
            return 1 - Math.pow(1 - t, 3);
        }

        function shutdownStep(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1.0);
            const easedProgress = easeOutCubic(progress);

            // Fade particle glow intensity (audio uniform controls glow)
            material.uniforms.uAudio.value = startAudio * (1 - easedProgress);

            // Smoothly scale sphere to zero
            material.uniforms.uStateExpansion.value = startExpansion * (1 - easedProgress);

            // Fade particle opacity
            particles.material.opacity = 1 - easedProgress;

            // Optional: Fade background to black
            const bgColor = scene.background;
            if (bgColor && bgColor.isColor) {
                const fadeValue = 1 - (easedProgress * 0.5); // Fade to 50% darker
                scene.background.setHSL(0, 0, 0.02 * fadeValue);
            }

            // Render current frame
            renderer.render(scene, renderer.camera || scene.camera);

            // Continue animation or complete shutdown
            if (progress < 1.0) {
                requestAnimationFrame(shutdownStep);
            } else {
                completeShutdown();
            }
        }

        function completeShutdown() {
            console.log("✓ Shutdown animation complete");

            // Dispose Three.js resources
            try {
                if (geometry) {
                    geometry.dispose();
                    console.log("✓ Geometry disposed");
                }

                if (material) {
                    material.dispose();
                    console.log("✓ Material disposed");
                }

                if (renderer) {
                    renderer.dispose();
                    console.log("✓ Renderer disposed");

                    // Remove canvas from DOM
                    if (renderer.domElement && renderer.domElement.parentElement) {
                        renderer.domElement.parentElement.removeChild(renderer.domElement);
                        console.log("✓ Canvas removed from DOM");
                    }
                }

                // Clear scene
                if (scene) {
                    while (scene.children.length > 0) {
                        scene.remove(scene.children[0]);
                    }
                    console.log("✓ Scene cleared");
                }

            } catch (error) {
                console.error("Error during resource disposal:", error);
            }

            // Close WebSocket connection
            if (socket && socket.readyState === WebSocket.OPEN) {
                socket.close(1000, "Graceful shutdown");
                console.log("✓ WebSocket connection closed");
            }

            // Update final status
            if (updateStatus) {
                updateStatus("🔴 JARVIS OFFLINE");
            }

            console.log("=".repeat(60));
            console.log("JARVIS SHUTDOWN COMPLETE");
            console.log("GPU resources released");
            console.log("WebSocket connections closed");
            console.log("Goodbye.");
            console.log("=".repeat(60));

            resolve();
        }

        // Start shutdown animation
        requestAnimationFrame(shutdownStep);
    });
}

/**
 * Quick emergency shutdown without animation
 * Use when immediate termination is required
 */
export function emergencyShutdown(options) {
    const { geometry, material, renderer, socket, animationId } = options;

    console.warn("⚠ EMERGENCY SHUTDOWN");

    if (animationId) cancelAnimationFrame(animationId);
    if (geometry) geometry.dispose();
    if (material) material.dispose();
    if (renderer) {
        renderer.dispose();
        if (renderer.domElement && renderer.domElement.parentElement) {
            renderer.domElement.parentElement.removeChild(renderer.domElement);
        }
    }
    if (socket && socket.readyState === WebSocket.OPEN) {
        socket.close(1000, "Emergency shutdown");
    }

    console.log("Emergency shutdown complete");
}
