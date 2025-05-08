# T2G App

🌀 Visual dashboard for single-site and lattice simulations using Dash + Electron + Google Drive.

## 📦 Setup

```bash
# 1. Clone the repo
git clone https://github.com/sarasame00/t2g_app
cd t2g_app

# 2. Create a virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run it
python run.py
```

Or launch as a desktop app with Electron:

```bash
cd electron
npm install
npm start
```
## 🧪 Dev Notes
- run.py is the entry point for the Python server
- Google Drive creds go in drive_service_account.json
- Lattice & single-site data fetched dynamically
