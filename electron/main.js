const { app, BrowserWindow } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const http = require('http');

const DASH_URL = 'http://127.0.0.1:8050';

let mainWindow;
let pyProc;

function getPythonBinaryPath() {
  if (app.isPackaged) {
    return path.join(process.resourcesPath, 'app.asar.unpacked', 'run');
  } else {
    return path.join(__dirname, 'run'); // development mode
  }
}

function waitForDashReady(callback, retries = 120) {
  const tryConnect = () => {
    http.get(`${DASH_URL}/_dash-layout`, (res) => {
      if (res.statusCode === 200) {
        console.log("✅ Dash server is up!");
        mainWindow.setBounds({ width: 1280, height: 900 });
        mainWindow.setResizable(true);
        mainWindow.setAlwaysOnTop(false);
        // mainWindow.setFrame(true);  ❌ REMOVE this line
        mainWindow.loadURL(DASH_URL);
        callback();
      } else {
        retryLater();
      }
    }).on('error', retryLater);
  };

  const retryLater = () => {
    if (retries > 0) {
      console.log(`⏳ Waiting for Dash layout... (${retries})`);
      setTimeout(() => waitForDashReady(callback, retries - 1), 500);
    } else {
      console.error("❌ Dash layout not available in time.");
    }
  };

  tryConnect();
}


function createWindow () {
  mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    resizable: false,
    frame: true,
    alwaysOnTop: true,
    show: false,
    webPreferences: {
      nodeIntegration: false
    }
  });

  // Load splash screen (inline HTML)
  mainWindow.loadURL("data:text/html," + encodeURIComponent(`
    <html>
      <head>
        <title>Loading...</title>
        <style>
          body {
            background-color: #f0f0f0;
            font-family: sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
          }
          h1 {
            color: #555;
            animation: pulse 1.5s infinite;
          }
          @keyframes pulse {
            0% { opacity: 0.6; }
            50% { opacity: 1; }
            100% { opacity: 0.6; }
          }
        </style>
      </head>
      <body>
        <h1>Starting T2G App...</h1>
      </body>
    </html>
  `));

  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });
}


function startPythonServer() {
  const script = getPythonBinaryPath();
  pyProc = spawn(script);

  pyProc.stdout?.on('data', (data) => {
    console.log(`[Python] ${data}`);
  });

  pyProc.stderr?.on('data', (data) => {
    console.error(`[Python ERROR] ${data}`);
  });

  pyProc.on('close', (code) => {
    console.log(`[Python] Process exited with code ${code}`);
  });
}

app.whenReady().then(() => {
  createWindow();               // show splash first
  startPythonServer();          // launch Dash backend
  waitForDashReady(showDash);   // switch to Dash when ready
});


app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (mainWindow === null) {
    createWindow();
  }
});

function showDash() {
  console.log("✅ Dash server is up!");
  mainWindow.setBounds({ width: 1280, height: 900 });
  mainWindow.setResizable(true);
  mainWindow.setAlwaysOnTop(false);
  mainWindow.loadURL(DASH_URL);
}

