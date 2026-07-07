"""Server-rendered gallery thumbnails: small inferno PNGs of plane densities.

Navigation aids, not measurement surfaces: brightness is gamma-compressed
(t = (rho/rho_max)^GAMMA) so faint outer lobes stay visible - a VISUAL LIBERTY
disclosed in the gallery UI. The frontend cross-section renderer mirrors the
same GAMMA and the same matplotlib LUT (web/src/lib/colormap.ts, luts.ts), so
densities look identical everywhere.
"""

import io
from functools import lru_cache

import matplotlib

matplotlib.use("Agg")

from matplotlib import image as mpl_image  # noqa: E402

from atomsim.plane import plane_grid  # noqa: E402
from atomsim.systems import get_system  # noqa: E402

GAMMA = 0.5


@lru_cache(maxsize=512)
def render_thumbnail(n: int, l: int, m: int, system: str, basis: str, size: int) -> bytes:
    """Inferno PNG of |psi|^2 on the y=0 plane; row order flipped so +z is up."""
    sys_ = get_system(system)
    pg = plane_grid(
        n, l, m, quantity="density", basis=basis,
        Z=sys_.Z, mu_ratio=sys_.mu_ratio.value, resolution=size,
    )
    rho = pg.values
    vmax = float(rho.max())
    t = (rho / vmax) ** GAMMA if vmax > 0.0 else rho
    buf = io.BytesIO()
    mpl_image.imsave(buf, t[::-1], cmap="inferno", vmin=0.0, vmax=1.0, format="png")
    return buf.getvalue()
