// JARVIS Desktop — Electron Main Process
// Native frameless window with acrylic blur, ordered lifecycle cleanup

const { app, BrowserWindow, screen, ipcMain } = require('electron');
const path = require('path');
const os = require('os');

// ── Acrylic support detection ────────────────────────────────────────
// Windows 11 (build 22000+) supports backgroundMaterial: 'acrylic'
// Windows 10 and below: fallback to WebGL-rendered blurred gradient
function isAcrylicSupported() {
    if (process.platform !== 'win32') return false;
    const release = os.release(); // e.g. '10.0.22631'
    const parts = release.split('.');
    const build = parseInt(parts[2] || '0', 10);
    const supported = build >= 22000;
    console.log(`[JARVIS] Windows build: ${build}, acrylic: ${supported ? 'native' : 'fallback'}`);
    return supported;
}

const nativeAcrylic = isAcrylicSupported();

// ── GPU acceleration flags (must be before app.whenReady) ────────────
app.commandLine.appendSwitch('enable-gpu-rasterization');
app.commandLine.appendSwitch('enable-zero-copy');
app.commandLine.appendSwitch('disable-software-rasterizer');

// ── State ────────────────────────────────────────────────────────────
// ── Safety: Prevent crash dialogs ────────────────────────────────────
process.on('uncaughtException', (err) => {
    console.error("[JARVIS] Main process crash prevented:", err);
});

// ── State ────────────────────────────────────────────────────────────
let mainWindow = null;
let isQuitting = false;

// ── Safety: Robust IPC Sender ────────────────────────────────────────
function safeSend(channel, data) {
    if (mainWindow && !mainWindow.isDestroyed()) {
        try {
            mainWindow.webContents.send(channel, data);
        } catch (e) {
            console.error(`[JARVIS] Failed to send ${channel}:`, e);
        }
    }
}

// ── Window creation ──────────────────────────────────────────────────
function createWindow() {
    const primaryDisplay = screen.getPrimaryDisplay();
    const { width: screenWidth, height: screenHeight } = primaryDisplay.workAreaSize;

    const winWidth = 300;
    const winHeight = 300;
    const x = Math.round((screenWidth - winWidth) / 2);
    // Position at bottom center, leaving space for taskbar
    const y = screenHeight - winHeight - 20;

    console.log(`[JARVIS] Creating window at (${x}, ${y}), screen: ${screenWidth}x${screenHeight}`);
    console.log(`[JARVIS] process.type: ${process.type}`);
    console.log(`[JARVIS] Electron: ${process.versions.electron}`);

    mainWindow = new BrowserWindow({
        width: winWidth,
        height: winHeight,
        x,
        y,
        frame: false,
        transparent: true,
        resizable: false,
        movable: false,
        hasShadow: false,
        alwaysOnTop: true,

        // Fully transparent background (Critical for no-square look)
        backgroundColor: '#00000000',

        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            preload: path.join(__dirname, 'preload.js'),
            backgroundThrottling: false  // keep render loop alive when unfocused
        }
    });

    mainWindow.setMenuBarVisibility(false);
    mainWindow.setMenu(null);

    mainWindow.loadFile('index.html');

    // ── Console forwarding ───────────────────────────────────
    mainWindow.webContents.on('console-message', (event, level, message) => {
        const lvl = ['LOG', 'WARN', 'ERROR'][level] || 'INFO';
        console.log(`[R:${lvl}] ${message}`);
    });

    mainWindow.webContents.on('did-finish-load', () => {
        console.log('[JARVIS] Page loaded');
        // Tell renderer which blur mode is active
        safeSend('main:blur-mode', {
            native: nativeAcrylic,
            mode: nativeAcrylic ? 'acrylic' : 'webgl-fallback'
        });
    });

    mainWindow.webContents.on('did-fail-load', (event, code, desc) => {
        console.error(`[JARVIS] Load failed: ${code} ${desc}`);
    });

    mainWindow.webContents.on('render-process-gone', (event, details) => {
        console.error('[JARVIS] Renderer crashed:', details.reason);
    });

    // ── Dev Tools: Only in development ───────────────────────────────────
    if (!app.isPackaged) {
        mainWindow.webContents.openDevTools({ mode: 'detach' });
    }

    mainWindow.on('closed', () => {
        mainWindow = null;
    });
}

// ── IPC: Ordered shutdown protocol ───────────────────────────────────
//
// Shutdown sequence:
//   1. User presses S / close button / app.quit()
//   2. Main sends  main:initiate-shutdown  →  renderer
//   3. Renderer cancels rAF, fades out, disposes GPU, forces context loss
//   4. Renderer sends  renderer:shutdown-complete  →  main
//   5. Main calls app.quit()
//

let shutdownTimer = null;

ipcMain.on('renderer:shutdown-complete', () => {
    console.log('[JARVIS] Renderer confirmed GPU disposal — quitting');
    if (shutdownTimer) clearTimeout(shutdownTimer);
    isQuitting = true;
    app.quit();
});

function initiateShutdown() {
    if (isQuitting) return;

    if (mainWindow && !mainWindow.isDestroyed()) {
        console.log('[JARVIS] Sending shutdown signal to renderer');
        safeSend('main:initiate-shutdown');

        // Safety timeout — force quit if renderer doesn't respond in 5s
        shutdownTimer = setTimeout(() => {
            console.warn('[JARVIS] Renderer unresponsive — force quitting');
            isQuitting = true;
            app.quit();
        }, 5000);
    } else {
        isQuitting = true;
        app.quit();
    }
}

// ── App lifecycle ────────────────────────────────────────────────────

app.on('before-quit', (event) => {
    if (!isQuitting) {
        // Intercept quit — give renderer time to clean up
        event.preventDefault();
        initiateShutdown();
    }
});

app.whenReady().then(() => {
    console.log('[JARVIS] App ready');
    createWindow();
});

app.on('window-all-closed', () => {
    if (!isQuitting) {
        isQuitting = true;
    }
    app.quit();
});
