# === Helper Function: Range Check ===
def in_range(value, low, high, tol=1e-4):
    """
    Check if a value is within [low, high], allowing for a small tolerance.

    Parameters
    ----------
    value : float
        The value to check.
    low : float
        Lower bound of range.
    high : float
        Upper bound of range.
    tol : float
        Numerical tolerance to allow slight deviations.

    Returns
    -------
    bool
        True if value is within [low - tol, high + tol], False otherwise.
    """
    return (low - tol) <= value <= (high + tol)


# === Main Function: Ion Type Inference ===
def infer_ion_type(row):
    """
    Infer the type of ion (3d, 4d, 5d) based on simulation parameters.

    Parameters
    ----------
    row : dict-like or pandas Series
        Dictionary of parameter values for a given simulation.

    Returns
    -------
    str
        Inferred ion type ("3d_d1", "4d_d1", "5d_d1"), or "unknown" if no match or format error.
    """
    base_rules = {
        "3d": {
            "t": (0.1, 0.3),
            "U": (3, 6),
            "J": (0.6, 1),
            "lbd": (0.02, 0.07),
            "g": (0.1, 0.2),
            "B": (0.1, 0.2),
        },
        "4d": {
            "t": (0.3, 0.5),
            "U": (1.5, 3),
            "J": (0.4, 0.6),
            "lbd": (0.1, 0.2),
            "g": (0.02, 0.1),
            "B": (0.02, 0.1),
        },
        "5d": {
            "t": (0.6, 1.0),
            "U": (1, 3),
            "J": (0.2, 0.5),
            "lbd": (0.2, 0.4),
            "g": (0.0, 0.02),
            "B": (0.0, 0.02),
        },
    }

    n_values = {
        "d1": 1,
        "d2": 2,
        "d3": 3,
        "d4": 4,
        "d5": 5,
    }

    rules = {}
    for family, params in base_rules.items():
        for d_label, N in n_values.items():
            ion_type = f"{family}_{d_label}"
            rules[ion_type] = {
                "N": (N, N),
                **params
            }


    try:
        for ion, ranges in rules.items():
            match = True
            for param, (low, high) in ranges.items():
                if param not in row:
                    continue  # Missing parameter, ignore
                value = float(row[param])  # Will raise if not numeric
                if not in_range(value, low, high):
                    match = False
                    break

            if match:
                return ion
    except Exception:
        # Catch any error in format (e.g., non-numeric, NaN, etc.)
        return "unknown"

    return "unknown"
