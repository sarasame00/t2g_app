const { app, BrowserWindow } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const http = require('http'); 
const DASH_URL = 'http://127.0.0.1:8050';

let mainWindow;
let pyProc;

function waitForDashReady(callback, retries = 120) {
    const tryConnect = () => {
      http.get(`${DASH_URL}/_dash-layout`, (res) => {
        if (res.statusCode === 200) {
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
    width: 1280,
    height: 900,
    webPreferences: {
      nodeIntegration: false
    },
    title: "t2g App",
    icon: path.join(__dirname, 'icon.png') 
  });

  mainWindow.loadURL('http://127.0.0.1:8050');

  mainWindow.on('closed', function () {
    mainWindow = null;
    if (pyProc) {
      pyProc.kill();
    }
  });
}

function startPythonServer() {
  const script = path.join(__dirname, '..', 'app', 'run.py');
  pyProc = spawn('/Users/sarasalesmerino/Desktop/ICMAB/t2g_app/venv/bin/python', [script], { stdio: 'ignore' });

}

app.whenReady().then(() => {
    startPythonServer();
    waitForDashReady(createWindow); 
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
