import plotly.graph_objects as go
from logic.sym_utils import take_borders, antifourier


def plot_orbital_momentum(data):
    orbcharge = 4 * (data["corrdiag"] - data["corroffd"])
    dist, orbcharge_k = take_borders(data["irrBZ"], orbcharge)
    k_sz = data["k_sz"]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dist, y=orbcharge_k, mode='lines'))

    fig.update_layout(
        margin=dict(l=20, r=20, t=40, b=10),
        yaxis_title="⟨ δ𝕋<sub>q</sub> δ𝕋<sub>q</sub> ⟩",
        xaxis=dict(
            tickmode="array",
            tickvals=[dist[i * (k_sz // 2)] for i in range(8)],
            ticktext=["", "", "", "", "", "", "", ""]
        ),
    )

    for x in [dist[i * 12] for i in range(8)]:
        fig.add_vline(x=x, line_width=0.5, line_color="black")

    return fig


def plot_orbital_real(data):
    orbcharge = 4 * (data["corrdiag"] - data["corroffd"])
    x, orbcharge_r = antifourier(data["k_sz"], data["irrBZ"], orbcharge)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=orbcharge_r, mode='markers+lines'))

    fig.update_layout(
        margin=dict(l=20, r=20, t=40, b=10),
        yaxis_title="⟨ δ𝕋<sub>i</sub> δ𝕋<sub>j</sub> ⟩",
        xaxis=dict(tickmode="array", tickvals=[0, 3, 6, 9, 12, 15], ticktext=["", "", "", "", "", ""]),
        yaxis=dict(tickmode="array", tickvals=[-0.15, -0.1, -0.05, 0, 0.05, 0.1, 0.15], range=[-0.18, 0.18])
    )

    return fig


def plot_spin_momentum(data):
    spincharge = 2 * (3 * data["corrdiag"] + data["corroffd"])
    dist, spin_k = take_borders(data["irrBZ"], spincharge)
    k_sz = data["k_sz"]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dist, y=spin_k, mode='lines'))

    fig.update_layout(
        margin=dict(l=20, r=20, t=10, b=10),
        xaxis_title="q along iBZ path",
        yaxis_title="⟨ δ𝕎<sub>q</sub> δ𝕎<sub>q</sub> ⟩",
        xaxis=dict(
            tickmode="array",
            tickvals=[dist[i * (k_sz // 2)] for i in range(8)],
            ticktext=["Γ", "X", "M", "Γ", "R", "X", "M", "R"]
        ),
    )

    for x in [dist[i * 12] for i in range(8)]:
        fig.add_vline(x=x, line_width=0.5, line_color="black")

    return fig


def plot_spin_real(data):
    spincharge = 2 * (3 * data["corrdiag"] + data["corroffd"])
    x, spin_r = antifourier(data["k_sz"], data["irrBZ"], spincharge)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=spin_r, mode='markers+lines'))

    fig.update_layout(
        margin=dict(l=20, r=20, t=10, b=10),
        xaxis_title="x<sub>j</sub> - x<sub>i</sub>",
        yaxis_title="⟨ δ𝕎<sub>i</sub> δ𝕎<sub>j</sub> ⟩",
        xaxis=dict(tickmode="array", tickvals=[0, 3, 6, 9, 12, 15]),
        yaxis=dict(tickmode="array", tickvals=[-0.15, -0.1, -0.05, 0, 0.05, 0.1, 0.15], range=[-0.18, 0.18])
    )

    return fig

'''

def plot_nn_correlation_vs_t(t_values, correlation_AW, correlation_AT):
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=t_values, y=correlation_AW,
        mode="markers+lines",
        name="A=W",
        marker_symbol="square",
        marker_color="red"
    ))

    fig.add_trace(go.Scatter(
        x=t_values, y=correlation_AT,
        mode="markers+lines",
        name="A≠T",
        marker_symbol="triangle-up",
        marker_color="blue"
    ))

    fig.update_layout(
        xaxis_title="t (eV)",
        yaxis_title="⟨ δA δA' ⟩",
        xaxis_type="log",     # <-- log x-axis
        yaxis_type="linear",
        margin=dict(l=20, r=20, t=40, b=0),
        legend=dict(title="Type")
    )

    return fig
'''

def empty_plot(message=""):
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