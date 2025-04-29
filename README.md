# T2G App

Visual dashboard for exploring orbital-spin-lattice correlations in t₂g electron systems — built using Dash, Electron, and Google Drive.

- Dynamic energy and correlation plots (single-site and lattice models)
- Automatic file sync from Google Drive
- Offline-ready: works without internet after syncing
- Cross-platform desktop app (macOS .dmg, Windows .exe)
- Research-grade tool developed at ICMAB-CSIC

---

## Setup (for developers)

```bash
# 1. Clone the repo
git clone https://github.com/yourusername/t2g_app
cd t2g_app

# 2. Create a Python virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Run the app (development server)
python app/run.py
```

Or launch the app as a **Desktop Application** with Electron:

```bash
cd electron
npm install
npm start
```

This starts the Python server and opens the Electron window automatically.

---

## Main Features

- **Google Drive Sync**:  
  Fetches simulation metadata and missing data files automatically.

- **Single-Site Model**:  
  Explore local and synchronized **energy maps** by tuning interaction parameters (U, J, B, λ, g).

- **Lattice Model**:  
  Visualize **correlation functions** along high-symmetry paths (Γ→X→M→R) for varying hopping values (`t`).

- **Sync Manager**:  
  Check missing simulation files and download only what's missing from Drive.

- **Offline Mode**:  
  Once files are downloaded, the app works **completely offline**.

- **Built with**:  
    - Python 3.10+
    - Dash & Plotly
    - Electron
    - Google Drive API
    - Electron Builder

---

## Credentials

Place your Google Drive service account JSON here:

```
sync/drive_service_account.json
```

(Private — do not commit this file to Git.)

---

## Dev Notes

- `app/run.py` is the main entry point for the Dash server.
- All simulation logic is under:
  - `logic/`
  - `sync/`
  - `plots/`
- Electron manages launching the server + desktop frontend (`electron/main.js`).
- Data is dynamically fetched if missing, otherwise cached locally under `data/`.

---

##  Build a desktop installer

### Build `.app` or `.exe` installer:

```bash
cd electron
npm run dist
```

- Creates `.dmg` installer on macOS
- Creates `.exe` installer on Windows
- (No manual config needed — auto-detects OS)

Find final builds under:

```
electron/dist/
```

---
