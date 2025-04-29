# === Imports ===
import numpy as np

# === Rotation Utilities ===

def rot_mat(theta, u):
    """
    Computes the integer-valued 3×3 rotation matrix for a rotation of angle `theta` (in degrees)
    around an arbitrary axis `u`, using the Rodrigues rotation formula.

    Parameters:
    - theta (float): Rotation angle in degrees.
    - u (array-like): 3D axis vector to rotate around (will be normalized internally).

    Returns:
    - np.ndarray (3x3 int): Rounded integer rotation matrix.
    """

    # Normalize the rotation axis
    u = u / np.sqrt(np.dot(u, u))

    # Convert angle from degrees to radians
    theta *= np.pi / 180

    # Build skew-symmetric matrix K for cross-product operator: K·v = u × v
    K = np.array([
        np.cross([1, 0, 0], u),  # row corresponding to x
        np.cross([0, 1, 0], u),  # row corresponding to y
        np.cross([0, 0, 1], u)   # row corresponding to z
    ])

    # Rodrigues' rotation formula:
    R = np.eye(3) + np.sin(theta) * K + (1 - np.cos(theta)) * (K @ K)

    # Return rounded version as integer matrix (for discrete symmetry operations)
    return np.round(R).astype(np.int32)

# ------------------------------------------------------------------------------
# Define the full cubic symmetry group (Oh) including inversion
# ------------------------------------------------------------------------------

# Generate Oh group (rotation + inversion symmetry)
Ohsym = [
    rot_mat(0,   (1, 0, 0)),   # Identity

    # 180° rotations around principal axes
    rot_mat(180, (1, 0, 0)),   
    rot_mat(180, (0, 1, 0)),
    rot_mat(180, (0, 0, 1)),

    # 180° rotations around face diagonals
    rot_mat(180, (1, 1, 0)),
    rot_mat(180, (-1, 1, 0)),
    rot_mat(180, (1, 0, 1)),
    rot_mat(180, (1, 0, -1)),
    rot_mat(180, (0, -1, -1)),
    rot_mat(180, (0, -1, 1)),

    # 90° rotations around principal axes
    rot_mat(90, (1, 0, 0)),
    rot_mat(90, (0, 1, 0)),
    rot_mat(90, (0, 0, 1)),

    # 270° rotations (90° in opposite direction)
    rot_mat(90, (-1, 0, 0)),
    rot_mat(90, (0, -1, 0)),
    rot_mat(90, (0, 0, -1)),

    # 120° rotations around body diagonals
    rot_mat(120, (1, 1, 1)),
    rot_mat(120, (-1, 1, 1)),
    rot_mat(120, (1, -1, 1)),
    rot_mat(120, (1, 1, -1)),
    rot_mat(120, (1, -1, -1)),
    rot_mat(120, (-1, 1, -1)),
    rot_mat(120, (-1, -1, 1)),
    rot_mat(120, (-1, -1, -1)),
]

# Add improper rotations (inversion through origin)
Ohsym += [-s for s in Ohsym]

# ------------------------------------------------------------------------------
# Fourier Transform Utilities
# ------------------------------------------------------------------------------

def antifourier(k_sz, irrBZ, func, xmin=0, xmax=16, axis=0):
    """
    Computes real-space correlation profile from momentum-space data 
    via inverse Fourier transform over symmetry-expanded Brillouin zone.

    Parameters:
    - k_sz: int
        Size of the k-grid (typically the number of points along each axis).
    - irrBZ: np.ndarray
        Array of irreducible Brillouin zone points (n_q, 3).
    - func: np.ndarray
        Function values at each irrBZ point.
    - xmin, xmax: int
        Range of real-space distances to compute.
    - axis: int
        Axis along which to project.

    Returns:
    - xsites: np.ndarray
        Distances (integer sites).
    - profile: np.ndarray
        Real-space correlation function profile.
    """

    # Generate real-space positions
    xsites = np.arange(xmin, xmax)

    # Build k-grid indices
    k_idxs = np.transpose(np.indices((k_sz,) * 3), (1, 2, 3, 0))

    # Fourier kernel e^{-i k.x}
    euler_factor = np.exp(
        -1j * 2 * np.pi * k_idxs[:, :, :, axis, None] * xsites[None, None, None, :]
        / k_sz
    )

    # Initialize full Brillouin zone with zeros
    func_expand = np.zeros((k_sz, k_sz, k_sz))

    # Symmetrize function into full BZ using Oh operations
    for i, q in enumerate(irrBZ):
        for s in Ohsym:
            kx, ky, kz = (s @ q) % k_sz
            func_expand[kx, ky, kz] = func[i]

    # Sum Fourier series to real space
    profile = np.sum(euler_factor * func_expand[:, :, :, None], axis=(0, 1, 2)).real
    profile /= k_sz**3

    return xsites, profile

def take_borders(irrBZ, func):
    """
    Extract a high-symmetry path (Γ → X → M → R) and associated function values.

    Parameters:
    - irrBZ: np.ndarray
        Momentum points (n_q, 3).
    - func: np.ndarray
        Function values at those points.

    Returns:
    - dist_path: np.ndarray
        Cumulative distances along high-symmetry path.
    - func_path: np.ndarray
        Function values interpolated along the path.
    """

    # Infer full k-grid size
    k_sz = np.max(irrBZ) * 2

    # Identify different path segments
    GXpath = np.where((irrBZ[:, 1] == 0) & (irrBZ[:, 2] == 0))               # Γ → X
    XMpath = np.where((irrBZ[:, 0] == k_sz // 2) & (irrBZ[:, 2] == 0))       # X → M
    GMpath = np.where((irrBZ[:, 0] == irrBZ[:, 1]) & (irrBZ[:, 2] == 0))     # Γ → M
    GRpath = np.where((irrBZ[:, 0] == irrBZ[:, 1]) & (irrBZ[:, 2] == irrBZ[:, 1]))  # Γ → R
    XRpath = np.where((irrBZ[:, 0] == k_sz // 2) & (irrBZ[:, 2] == irrBZ[:, 1]))    # X → R
    MRpath = np.where((irrBZ[:, 1] == k_sz // 2) & (irrBZ[:, 0] == k_sz // 2))      # M → R

    # Concatenate function values along full path
    func_path = np.concatenate((
        func[GXpath][:-1],
        func[XMpath][:-1],
        func[GMpath][:0:-1],
        func[GRpath][:-1],
        func[XRpath][:0:-1],
        func[XMpath][:-1],
        func[MRpath]
    ))

    # Concatenate k-points
    irrBZ_path = np.concatenate((
        irrBZ[GXpath][:-1],
        irrBZ[XMpath][:-1],
        irrBZ[GMpath][:0:-1],
        irrBZ[GRpath][:-1],
        irrBZ[XRpath][:0:-1],
        irrBZ[XMpath][:-1],
        irrBZ[MRpath]
    ))

    # Compute cumulative distances
    delta_path = np.concatenate((
        np.array([0]),
        np.sqrt(np.sum((irrBZ_path[1:] - irrBZ_path[:-1])**2, axis=1))
    ))

    A = np.tril(np.ones(delta_path.size))
    dist_path = A @ delta_path

    # Normalize to 2π/a units
    return dist_path / k_sz * 2 * np.pi, func_path
