
# <img src="https://raw.githubusercontent.com/sarasame00/t2g_app/main/app/assets/icon.png" width="22">&nbsp;  t₂g-App



t₂g-App is an interactive Dash app for exploring quantum simulation results of models with strong spin-orbit coupling. It supports both lattice and single-site models, allowing users to inspect correlation functions in real and momentum space and across different physical parameters.

- Live app: [https://t2g-app.onrender.com](https://t2g-app.onrender.com)
- Terminal app: Run locally from the command line
- Desktop app: In progress (see try-pyinstaller branch)

---

## 🔍 Features
### Single-site model (ss)
- Visualize energy maps over 2D parameter grids
- Choose between ion types (3d, 4d, 5d) and vary U, J, g, B, ξ
- Interactive colorbars and ion-specific value filtering

### Lattice model (lat)

- Plot correlation functions:
  - Real-space: ⟨δ𝕋ᵢ δ𝕋ⱼ⟩, ⟨δ𝕎ᵢ δ𝕎ⱼ⟩, ⟨δσ_zᵢ δσ_zⱼ⟩
  - Momentum-space along symmetry path Γ–X–M–R
- Analyze how correlations evolve with parameters like t, U, J, g, ξ
- Supports multiple hopping values for comparative studies

## ⚙️ How Sync Works (Local Use Only)
When running locally, the app provides a "Sync" page to fetch simulation results directly from Google Drive:

- You choose a model and ion types
- The app checks which simulations are missing locally
- It downloads only those needed, using a background thread
- Files are saved to a local cache (`./data/`)

> ⚠️ The sync page is not functional in the hosted version on Render since it  doesn't support persistent storage or background threads.

## 🚀 Run the app

### ▶  Option 1: Use the hosted Web version

Visit:
👉 https://t2g-app.onrender.com

Note: The “Sync” tab is not functional in this hosted version.

### ▶  Option 2: Run locally

Clone the repo and install dependencies:

```bash
git clone https://github.com/sarasame00/t2g_app.git
cd t2g_app
pip install -r requirements.txt
python app.py
```

## 📊 Try local plots (without Dash)
Use `test_local_plot.py` to generate standalone HTML plots from HDF5 data:
```bash
python test_local_plot.py
```

## 🧪 Work in progress: Desktop app

A PyInstaller-based desktop version is under development in the `try-pyinstaller` branch. It's experimental and not yet stable.
```bash
git checkout try-pyinstaller
```

## 📁 Project Structure

- `app.py` – Dash entrypoint
- `plots/` – Visualization logic
- `logic/` – Data loading and transformation utilities
- `sync/` – File download tools (used locally)
- `test_local_plot.py` – Basic Plotly testing script

