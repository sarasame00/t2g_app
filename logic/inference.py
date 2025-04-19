def in_range(value, low, high):
    return low <= value <= high

def infer_ion_type(row):
    rules = {
        "3d_d1": {
            "N": (1, 1),
            "t": (0.1, 0.3),
            "U": (3, 6),
            "J": (0.6, 1),
            "lbd": (0.02, 0.07),
            "g": (0.1, 0.2),
            "B": (0.1, 0.2),
        },
        "4d_d1": {
            "N": (1, 1),
            "t": (0.3, 0.5),
            "U": (1.5, 3),
            "J": (0.4, 0.6),
            "lbd": (0.1, 0.2),
            "g": (0.02, 0.1),
            "B": (0.02, 0.1),
        },
        "5d_d1": {
            "N": (1, 1),
            "t": (0.6, 1.0),
            "U": (1, 3),
            "J": (0.2, 0.5),
            "lbd": (0.2, 0.4),
            "g": (0.0, 0.02),
            "B": (0.0, 0.02),
        }
    }

    for ion, ranges in rules.items():
        match = True
        for param, (low, high) in ranges.items():
            if param not in row:
                continue  # Skip if param not in data
            if not in_range(row[param], low, high):
                match = False
                break
        if match:
            return ion

    return "unknown"
