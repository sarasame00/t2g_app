import plotly.graph_objects as go
import plotly.express as px
from dash import html
from logic.sym_utils import take_borders, antifourier


def plot_orbital_momentum(data, t_values=None, fixed_range=None):
    """Plot orbital momentum correlation along iBZ path.

    Parameters
    ----------
    data : dict or list of dict
        Dictionary or list of dictionaries containing correlation data.
    t_values : list of float, optional
        Corresponding hopping t values for multiple data entries.
    fixed_range : list or tuple, optional
        If provided, sets fixed y-axis range.

    Returns
    -------
    go.Figure
        Plotly figure showing orbital momentum correlations.
    """
    fig = go.Figure()

    if isinstance(data, list):
        for idx, d in enumerate(data):
            orbcharge = 4 * (d["corrdiag"] - d["corroffd"])
            dist, orbcharge_k = take_borders(d["irrBZ"], orbcharge)
            fig.add_trace(go.Scatter(
                x=dist, y=orbcharge_k, mode='lines',
                name=f't={t_values[idx]:.2f} eV' if t_values else None
            ))
            k_sz = d["k_sz"]
    else:
        orbcharge = 4 * (data["corrdiag"] - data["corroffd"])
        dist, orbcharge_k = take_borders(data["irrBZ"], orbcharge)
        fig.add_trace(go.Scatter(x=dist, y=orbcharge_k, mode='lines'))
        k_sz = data["k_sz"]

    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        yaxis_title="⟨ δ𝕋<sub>q</sub> δ𝕋<sub>q</sub> ⟩",
        xaxis=dict(
            tickmode="array",
            tickvals=[dist[i * (k_sz // 2)] for i in range(8)],
            ticktext=["Γ", "X", "M", "Γ", "R", "X", "M", "R"]
        ),
        showlegend=False
    )

    if fixed_range:
        fig.update_yaxes(range=fixed_range)

    for x in [dist[i * 12] for i in range(8)]:
        fig.add_vline(x=x, line_width=0.5, line_color="black")

    return fig


def plot_orbital_real(data, t_values=None, fixed_range=None):
    """Plot orbital real-space correlations.

    Parameters
    ----------
    data : dict or list of dict
        Dictionary or list of dictionaries containing correlation data.
    t_values : list of float, optional
        Corresponding hopping t values for multiple data entries.
    fixed_range : list or tuple, optional
        If provided, sets fixed y-axis range.

    Returns
    -------
    go.Figure
        Plotly figure showing orbital real-space correlations.
    """
    fig = go.Figure()

    if isinstance(data, list):
        for idx, d in enumerate(data):
            orbcharge = 4 * (d["corrdiag"] - d["corroffd"])
            x, orbcharge_r = antifourier(d["k_sz"], d["irrBZ"], orbcharge)
            fig.add_trace(go.Scatter(
                x=x, y=orbcharge_r, mode='lines+markers',
                name=f't={t_values[idx]:.2f} eV' if t_values else None
            ))
    else:
        orbcharge = 4 * (data["corrdiag"] - data["corroffd"])
        x, orbcharge_r = antifourier(data["k_sz"], data["irrBZ"], orbcharge)
        fig.add_trace(go.Scatter(x=x, y=orbcharge_r, mode='markers+lines'))

    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        yaxis_title="⟨ δ𝕋<sub>i</sub> δ𝕋<sub>j</sub> ⟩",
        xaxis=dict(
            tickmode="array",
            tickvals=[0, 3, 6, 9, 12, 15],
            ticktext=[0, 3, 6, 9, 12, 15]
        ),
        yaxis=dict(
            tickmode="array",
            tickvals=[-0.15, -0.1, -0.05, 0, 0.05, 0.1, 0.15],
            range=[-0.18, 0.18]
        ),
        showlegend=False
    )

    if fixed_range:
        fig.update_yaxes(range=fixed_range)

    return fig


def plot_spin_momentum(data, t_values=None, fixed_range=None):
    """Plot spin momentum correlation along iBZ path.

    Parameters
    ----------
    data : dict or list of dict
        Dictionary or list of dictionaries containing correlation data.
    t_values : list of float, optional
        Corresponding hopping t values for multiple data entries.
    fixed_range : list or tuple, optional
        If provided, sets fixed y-axis range.

    Returns
    -------
    go.Figure
        Plotly figure showing spin momentum correlations.
    """
    fig = go.Figure()

    if isinstance(data, list):
        for idx, d in enumerate(data):
            spincharge = 2 * (3 * d["corrdiag"] + d["corroffd"])
            dist, spin_k = take_borders(d["irrBZ"], spincharge)
            fig.add_trace(go.Scatter(
                x=dist, y=spin_k, mode='lines',
                name=f't={t_values[idx]:.2f} eV' if t_values else None
            ))
            k_sz = d["k_sz"]
    else:
        spincharge = 2 * (3 * data["corrdiag"] + data["corroffd"])
        dist, spin_k = take_borders(data["irrBZ"], spincharge)
        fig.add_trace(go.Scatter(x=dist, y=spin_k, mode='lines'))
        k_sz = data["k_sz"]

    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        yaxis_title="⟨ δ𝕎<sub>q</sub> δ𝕎<sub>q</sub> ⟩",
        xaxis=dict(
            tickmode="array",
            tickvals=[dist[i * (k_sz // 2)] for i in range(8)],
            ticktext=["Γ", "X", "M", "Γ", "R", "X", "M", "R"]
        ),
        showlegend=False
    )

    if fixed_range:
        fig.update_yaxes(range=fixed_range)

    for x in [dist[i * 12] for i in range(8)]:
        fig.add_vline(x=x, line_width=0.5, line_color="black")

    return fig

def plot_spin_real(data, t_values=None, fixed_range=None):
    """Plot spin real-space correlations.

    Parameters
    ----------
    data : dict or list of dict
        Dictionary or list of dictionaries containing correlation data.
    t_values : list of float, optional
        Corresponding hopping t values for multiple data entries.
    fixed_range : list or tuple, optional
        If provided, sets fixed y-axis range.

    Returns
    -------
    go.Figure
        Plotly figure showing spin real-space correlations.
    """
    fig = go.Figure()

    if isinstance(data, list):
        for idx, d in enumerate(data):
            spincharge = 2 * (3 * d["corrdiag"] + d["corroffd"])
            x, spin_r = antifourier(d["k_sz"], d["irrBZ"], spincharge)
            fig.add_trace(go.Scatter(
                x=x, y=spin_r, mode='markers+lines',
                name=f't={t_values[idx]:.2f} eV' if t_values else None
            ))
    else:
        spincharge = 2 * (3 * data["corrdiag"] + data["corroffd"])
        x, spin_r = antifourier(data["k_sz"], data["irrBZ"], spincharge)
        fig.add_trace(go.Scatter(x=x, y=spin_r, mode='markers+lines'))

    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        yaxis_title="⟨ δ𝕎<sub>i</sub> δ𝕎<sub>j</sub> ⟩",
        xaxis=dict(
            tickmode="array",
            tickvals=[0, 3, 6, 9, 12, 15]
        ),
        yaxis=dict(
            tickmode="array",
            tickvals=[-0.15, -0.1, -0.05, 0, 0.05, 0.1, 0.15],
            range=[-0.18, 0.18]
        ),
        showlegend=False
    )

    if fixed_range:
        fig.update_yaxes(range=fixed_range)

    return fig


def plot_nn_correlation_vs_t(data_list, t_values):
    """Plot nearest-neighbor orbital and spin-orbital correlations vs hopping t.

    Parameters
    ----------
    data_list : list of dict
        List of dictionaries, each containing simulation correlation data.
    t_values : list of float
        List of hopping t values corresponding to each dataset.

    Returns
    -------
    go.Figure
        Plotly figure comparing ⟨ δ𝕋 δ𝕋 ⟩ and ⟨ δ𝕎 δ𝕎 ⟩ at nearest-neighbor distance.
    """
    corr_AW = []
    corr_AT = []

    for data in data_list:
        orbcharge = 4 * (data["corrdiag"] - data["corroffd"])
        spincharge = 2 * (3 * data["corrdiag"] + data["corroffd"])

        x_orb, orb_r = antifourier(data["k_sz"], data["irrBZ"], orbcharge)
        x_spin, spin_r = antifourier(data["k_sz"], data["irrBZ"], spincharge)

        corr_AT.append(orb_r[1])  # Orbital correlation at first neighbor
        corr_AW.append(spin_r[1])  # Spin-orbital correlation at first neighbor

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=t_values, y=corr_AT,
        mode="markers+lines",
        name="⟨ δ𝕋 δ𝕋 ⟩ (Orbital)",
        marker_symbol="triangle-up",
        marker_color="#2145eb",
        line=dict(color="#2145eb"),
    ))

    fig.add_trace(go.Scatter(
        x=t_values, y=corr_AW,
        mode="markers+lines",
        name="⟨ δ𝕎 δ𝕎 ⟩ (Spin-Orbital)",
        marker_symbol="square",
        marker_color="#f83337",
        line=dict(color="#f83337"),
    ))

    fig.update_layout(
        xaxis_title="t (eV)",
        yaxis_title="Nearest-Neighbor Correlation",
        xaxis_type="log",
        margin=dict(l=10, r=10, t=10, b=10),
        font=dict(size=12),
        showlegend=False
    )

    return fig


def plot_sigmaz_momentum(data, t_values=None, fixed_range=None):
    """Plot sigma_z correlation along iBZ path.

    Parameters
    ----------
    data : dict or list of dict
        Dictionary or list of dictionaries containing correlation data.
    t_values : list of float, optional
        Corresponding hopping t values for multiple data entries.
    fixed_range : list or tuple, optional
        If provided, sets fixed y-axis range.

    Returns
    -------
    go.Figure
        Plotly figure showing σ_z momentum-space correlations.
    """
    fig = go.Figure()

    if isinstance(data, list):
        for idx, d in enumerate(data):
            fullspin = 6 * d["corrdiag"] - 4 * d["corroffd"]
            dist, spin_k = take_borders(d["irrBZ"], fullspin)
            fig.add_trace(go.Scatter(
                x=dist, y=spin_k, mode='lines',
                name=f't={t_values[idx]:.2f} eV' if t_values else None
            ))
            k_sz = d["k_sz"]
    else:
        fullspin = 6 * data["corrdiag"] - 4 * data["corroffd"]
        dist, spin_k = take_borders(data["irrBZ"], fullspin)
        fig.add_trace(go.Scatter(x=dist, y=spin_k, mode='lines'))
        k_sz = data["k_sz"]

    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        yaxis_title="⟨ δσ<sub>z</sub> δσ<sub>z</sub> ⟩",
        xaxis=dict(
            tickmode="array",
            tickvals=[dist[i * (k_sz // 2)] for i in range(8)],
            ticktext=["Γ", "X", "M", "Γ", "R", "X", "M", "R"]
        ),
        showlegend=False
    )

    for x in [dist[i * 12] for i in range(8)]:
        fig.add_vline(x=x, line_width=0.5, line_color="black")

    if fixed_range:
        fig.update_yaxes(range=fixed_range)

    return fig


def plot_sigmaz_real(data, t_values=None, fixed_range=None):
    """Plot sigma_z real-space correlations.

    Parameters
    ----------
    data : dict or list of dict
        Dictionary or list of dictionaries containing correlation data.
    t_values : list of float, optional
        Corresponding hopping t values for multiple data entries.
    fixed_range : list or tuple, optional
        If provided, sets fixed y-axis range.

    Returns
    -------
    go.Figure
        Plotly figure showing σ_z real-space correlations.
    """
    fig = go.Figure()

    if isinstance(data, list):
        for idx, d in enumerate(data):
            fullspin = 6 * d["corrdiag"] - 4 * d["corroffd"]
            x, spin_r = antifourier(d["k_sz"], d["irrBZ"], fullspin)
            fig.add_trace(go.Scatter(
                x=x, y=spin_r, mode='markers+lines',
                name=f't={t_values[idx]:.2f} eV' if t_values else None
            ))
    else:
        fullspin = 6 * data["corrdiag"] - 4 * data["corroffd"]
        x, spin_r = antifourier(data["k_sz"], data["irrBZ"], fullspin)
        fig.add_trace(go.Scatter(x=x, y=spin_r, mode='markers+lines'))

    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        yaxis_title="⟨ δσ<sub>z</sub> δσ<sub>z</sub> ⟩",
        xaxis=dict(
            tickmode="array",
            tickvals=[0, 3, 6, 9, 12, 15]
        ),
        yaxis=dict(
            tickmode="array",
            tickvals=[-0.15, -0.1, -0.05, 0, 0.05, 0.1, 0.15],
            range=[-0.18, 0.18]
        ),
        showlegend=False
    )

    if fixed_range:
        fig.update_yaxes(range=fixed_range)

    return fig


def empty_plot(message=""):
    """Return an empty plot with a message (used for errors or no data).

    Parameters
    ----------
    message : str
        Text to display as the plot title.

    Returns
    -------
    go.Figure
        Blank Plotly figure with centered message.
    """
    fig = go.Figure()
    fig.update_layout(
        title=message,
        xaxis={'visible': False},
        yaxis={'visible': False},
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=0, r=0, t=50, b=0)
    )
    return fig


def build_legend_correl():
    """Build a legend section for correlation types used in plots.

    Returns
    -------
    dash.html.Div
        Dash HTML component representing the legend.
    """
    colors = {
        "Orbital": "#2145eb",
        "Spin-Orbital": "#f83337"
    }

    corr_section = html.Div([
        html.Div("Correlation Type", style={"fontWeight": "bold", "marginBottom": "5px"}),
        html.Div([
            html.Div([
                html.Span("▲", style={"color": colors["Orbital"], "marginRight": "6px", "verticalAlign": "middle"}),
                html.Span("⟨ δ𝕋 δ𝕋 ⟩ (orbital-orbital)")
            ], style={"marginBottom": "5px"}),

            html.Div([
                html.Span("■", style={"color": colors["Spin-Orbital"], "marginRight": "6px", "verticalAlign": "middle"}),
                html.Span("⟨ δ𝕎 δ𝕎 ⟩ (spin-orbital)")
            ])
        ])
    ], style={"marginTop": "5px"})
    return corr_section


def build_legend_t(t_values):
    """Build a legend section displaying the t values used in plots.

    Parameters
    ----------
    t_values : list of float
        List of hopping t values displayed in plots.

    Returns
    -------
    dash.html.Div
        Dash HTML component representing the legend.
    """
    t_colors = px.colors.qualitative.Plotly
    t_section = html.Div([
        html.Div("Hopping t values", style={"fontWeight": "bold", "marginTop": "10px", "marginBottom": "5px"}),
        html.Ul([
            html.Li([
                html.Span("■", style={"color": t_colors[i % len(t_colors)], "marginRight": "6px", "fontSize": "14px", "verticalAlign": "middle"}),
                f"t = {t:.2f} eV"
            ]) for i, t in enumerate(sorted(t_values))
        ], style={"listStyleType": "none", "paddingLeft": "0"})
    ], style={"marginTop": "5px"})

    return t_section
