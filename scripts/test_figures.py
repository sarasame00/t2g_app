
from plotly.offline import plot
import sys

sys.path.append("/Users/sarasalesmerino/Desktop/ICMAB/t2g_app/")

from plots.visualize_test import plot_sigmaz_momentum, plot_sigmaz_real  
from logic.data_loader import load_correl_data


data = load_correl_data('/Users/sarasalesmerino/Desktop/ICMAB/t2g_app/data/lat_data/202504291203041430685065.hdf5')

# === Generate Figures ===
fig_momentum = plot_sigmaz_momentum(data)
fig_real = plot_sigmaz_real(data)

# === Show plots in browser ===
plot(fig_momentum, filename="sigmaz_momentum.html", auto_open=True)
plot(fig_real, filename="sigmaz_real.html", auto_open=True)
