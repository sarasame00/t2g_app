import sys
from pathlib import Path
from plotly.offline import plot

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from plots.visualize import (
    plot_sigmaz_momentum,
    plot_sigmaz_real,
    plot_spin_momentum,
    plot_spin_real,
    plot_orbital_momentum,
    plot_orbital_real
)
from logic.data_loader import load_correl_data

# Path to local test HDF5 file (adjust if needed)
h5_file = PROJECT_ROOT / "data/lat_data/202504291203041430685065.hdf5"
data = load_correl_data(h5_file)

# === Generate and display plots ===
plot(plot_sigmaz_momentum(data), filename="sigmaz_momentum.html", auto_open=True)
plot(plot_sigmaz_real(data), filename="sigmaz_real.html", auto_open=True)
plot(plot_spin_momentum(data), filename="spin_momentum.html", auto_open=True)
plot(plot_spin_real(data), filename="spin_real.html", auto_open=True)
plot(plot_orbital_momentum(data), filename="orbital_momentum.html", auto_open=True)
plot(plot_orbital_real(data), filename="orbital_real.html", auto_open=True)
