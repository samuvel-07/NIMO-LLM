// JARVIS Desktop — Preload Script
// Secure IPC bridge between main process and renderer

const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('jarvis', {
    // Main → Renderer: shutdown request
    onShutdownRequest: (callback) => {
        ipcRenderer.on('main:initiate-shutdown', () => callback());
    },

    // Main → Renderer: blur mode info (native acrylic vs WebGL fallback)
    onBlurMode: (callback) => {
        ipcRenderer.on('main:blur-mode', (event, data) => callback(data));
    },

    // Renderer → Main: GPU disposal complete, safe to quit
    notifyShutdownComplete: () => {
        ipcRenderer.send('renderer:shutdown-complete');
    }
});
