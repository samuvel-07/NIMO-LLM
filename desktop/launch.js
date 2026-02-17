// JARVIS Desktop — Launcher
// Spawns electron.exe with ELECTRON_RUN_AS_NODE removed from environment
// This is required because the host IDE/shell sets ELECTRON_RUN_AS_NODE=1
// which forces electron.exe into Node.js mode, breaking all Electron APIs.

const { spawn } = require('child_process');
const path = require('path');

// Get the path to electron.exe from the npm package
const electronPath = require('electron');

// Build a clean environment WITHOUT ELECTRON_RUN_AS_NODE
const cleanEnv = Object.fromEntries(
    Object.entries(process.env).filter(([key]) => key !== 'ELECTRON_RUN_AS_NODE')
);

// Forward all args after 'launch.js' to electron
const args = ['.', ...process.argv.slice(2)];

console.log('[JARVIS Launcher] Spawning Electron...');
console.log('[JARVIS Launcher] Binary:', electronPath);
console.log('[JARVIS Launcher] Args:', args.join(' '));

const child = spawn(electronPath, args, {
    stdio: 'inherit',
    cwd: __dirname,
    env: cleanEnv,
    windowsHide: false
});

child.on('close', (code) => {
    console.log('[JARVIS Launcher] Electron exited with code:', code);
    process.exit(code);
});

child.on('error', (err) => {
    console.error('[JARVIS Launcher] Failed to start Electron:', err.message);
    process.exit(1);
});
