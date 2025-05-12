import numpy as np

# === Rotation Utilities ===

def rot_mat(theta, u):
    """
    Compute integer-valued 3x3 rotation matrix using Rodrigues' formula.

    Parameters
    ----------
    theta : float
        Rotation angle in degrees.
    u : array-like
        3D axis vector to rotate around (normalized internally).

    Returns
    -------
    np.ndarray
        Rounded 3x3 integer-valued rotation matrix.
    """
    u = u / np.sqrt(np.dot(u, u))  # Normalize axis vector
    theta *= np.pi / 180  # Convert angle to radians

    # Compute cross-product matrix (skew-symmetric)
    K = np.array([
        np.cross([1, 0, 0], u),
        np.cross([0, 1, 0], u),
        np.cross([0, 0, 1], u)
    ])

    # Apply Rodrigues' rotation formula: R = I + sin(theta)*K + (1 - cos(theta))*K^2
    R = np.eye(3) + np.sin(theta) * K + (1 - np.cos(theta)) * (K @ K)
    return np.round(R).astype(np.int32)  # Round to integers for discrete symmetry


# === Define Full Oh Symmetry Group (Rotation + Inversion) ===

# Generate Oh symmetry group elements using basic rotations
Ohsym = [
    rot_mat(0,   (1, 0, 0)),  # Identity

    # 180° rotations around primary axes
    rot_mat(180, (1, 0, 0)), rot_mat(180, (0, 1, 0)), rot_mat(180, (0, 0, 1)),

    # 180° rotations around face diagonals
    rot_mat(180, (1, 1, 0)), rot_mat(180, (-1, 1, 0)), rot_mat(180, (1, 0, 1)),
    rot_mat(180, (1, 0, -1)), rot_mat(180, (0, -1, -1)), rot_mat(180, (0, -1, 1)),

    # 90° rotations around primary axes
    rot_mat(90, (1, 0, 0)), rot_mat(90, (0, 1, 0)), rot_mat(90, (0, 0, 1)),

    # 270° (i.e., 90° in opposite direction)
    rot_mat(90, (-1, 0, 0)), rot_mat(90, (0, -1, 0)), rot_mat(90, (0, 0, -1)),

    # 120° rotations around body diagonals
    rot_mat(120, (1, 1, 1)), rot_mat(120, (-1, 1, 1)), rot_mat(120, (1, -1, 1)),
    rot_mat(120, (1, 1, -1)), rot_mat(120, (1, -1, -1)), rot_mat(120, (-1, 1, -1)),
    rot_mat(120, (-1, -1, 1)), rot_mat(120, (-1, -1, -1))
]

# Add inversion symmetry (negate each rotation matrix)
Ohsym += [-s for s in Ohsym]


# === Fourier Transform Utilities ===

def antifourier(k_sz, irrBZ, func, xmin=0, xmax=16, axis=0):
    """
    Compute real-space profile from momentum-space data via inverse FT.

    Parameters
    ----------
    k_sz : int
        Size of the cubic k-grid.
    irrBZ : np.ndarray
        Irreducible Brillouin zone points (n_q, 3).
    func : np.ndarray
        Function values at irrBZ points.
    xmin : int
        Minimum real-space distance.
    xmax : int
        Maximum real-space distance.
    axis : int
        Axis along which to compute correlation profile.

    Returns
    -------
    xsites : np.ndarray
        Real-space distance bins.
    profile : np.ndarray
        Computed real-space correlation profile.
    """
    xsites = np.arange(xmin, xmax)

    # Build 3D grid of momentum indices
    k_idxs = np.transpose(np.indices((k_sz,) * 3), (1, 2, 3, 0))

    # Precompute Fourier kernel e^{-i k.x} for each position along selected axis
    euler_factor = np.exp(
        -1j * 2 * np.pi * k_idxs[:, :, :, axis, None] * xsites[None, None, None, :] / k_sz
    )

    # Initialize full Brillouin zone with zeros
    func_expand = np.zeros((k_sz, k_sz, k_sz))

    # Fill BZ symmetrically from irrBZ using Oh operations
    for i, q in enumerate(irrBZ):
        for s in Ohsym:
            kx, ky, kz = (s @ q) % k_sz
            func_expand[kx, ky, kz] = func[i]

    # Perform inverse FFT over expanded volume
    profile = np.sum(euler_factor * func_expand[:, :, :, None], axis=(0, 1, 2)).real
    profile /= k_sz**3
    return xsites, profile


def take_borders(irrBZ, func):
    """
    Extract function values along high-symmetry path in BZ.

    Parameters
    ----------
    irrBZ : np.ndarray
        BZ momentum coordinates (n_q, 3).
    func : np.ndarray
        Function values defined on irrBZ points.

    Returns
    -------
    dist_path : np.ndarray
        Cumulative distance along the high-symmetry path.
    func_path : np.ndarray
        Interpolated function values along the path.
    """
    k_sz = np.max(irrBZ) * 2  # Infer full grid size assuming symmetric BZ

    # Identify high-symmetry paths in reciprocal space
    GXpath = np.where((irrBZ[:, 1] == 0) & (irrBZ[:, 2] == 0))               # Γ → X
    XMpath = np.where((irrBZ[:, 0] == k_sz // 2) & (irrBZ[:, 2] == 0))       # X → M
    GMpath = np.where((irrBZ[:, 0] == irrBZ[:, 1]) & (irrBZ[:, 2] == 0))     # Γ → M
    GRpath = np.where((irrBZ[:, 0] == irrBZ[:, 1]) & (irrBZ[:, 2] == irrBZ[:, 1]))  # Γ → R
    XRpath = np.where((irrBZ[:, 0] == k_sz // 2) & (irrBZ[:, 2] == irrBZ[:, 1]))    # X → R
    MRpath = np.where((irrBZ[:, 1] == k_sz // 2) & (irrBZ[:, 0] == k_sz // 2))      # M → R

    # Build full high-symmetry path sequence
    func_path = np.concatenate((
        func[GXpath][:-1],
        func[XMpath][:-1],
        func[GMpath][:0:-1],
        func[GRpath][:-1],
        func[XRpath][:0:-1],
        func[XMpath][:-1],
        func[MRpath]
    ))

    irrBZ_path = np.concatenate((
        irrBZ[GXpath][:-1],
        irrBZ[XMpath][:-1],
        irrBZ[GMpath][:0:-1],
        irrBZ[GRpath][:-1],
        irrBZ[XRpath][:0:-1],
        irrBZ[XMpath][:-1],
        irrBZ[MRpath]
    ))

    # Compute cumulative Euclidean distances along the path
    delta_path = np.concatenate((
        np.array([0]),
        np.sqrt(np.sum((irrBZ_path[1:] - irrBZ_path[:-1]) ** 2, axis=1))
    ))

    # Integrate distances using lower-triangular sum
    A = np.tril(np.ones(delta_path.size))
    dist_path = A @ delta_path

    # Convert to reciprocal units (2π/a)
    return dist_path / k_sz * 2 * np.pi, func_path
