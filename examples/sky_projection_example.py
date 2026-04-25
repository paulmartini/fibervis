"""
Example: Sky projection of a hexagonal fiber bundle.

Demonstrates creating a hexagonally packed fiber arrangement, projecting it
onto the sky, and plotting the result.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import fibervis

# -------------------------------------------------------------------
# 1.  Create a 19-fiber hexagonal bundle (2 rings + centre)
# -------------------------------------------------------------------
bundle = fibervis.hexagonal_arrangement(
    n_fibers=19,
    fiber_diameter=100.0,   # 100-µm core diameter
    focal_ratio=4.0,
    cladding=10.0,          # 10-µm cladding around each core
)
print(f"Bundle: {bundle}")
print(f"Bounding box: {bundle.bounding_box()}")

# -------------------------------------------------------------------
# 2.  Project onto the sky
#     Assume a plate scale of 0.2 arcsec/µm
# -------------------------------------------------------------------
plate_scale = 0.2  # arcsec / µm
sky = fibervis.sky_projection(bundle, plate_scale)

# -------------------------------------------------------------------
# 3.  Filling factor
# -------------------------------------------------------------------
ff = fibervis.filling_factor(bundle)
print(f"Filling factor (bounding box): {ff:.3f}")

# -------------------------------------------------------------------
# 4.  Focal-ratio degradation throughput
# -------------------------------------------------------------------
t_frd = fibervis.focal_ratio_degradation(4.0, 3.6)
print(f"FRD throughput (f/4.0 → f/3.6): {t_frd:.3f}")

# -------------------------------------------------------------------
# 5.  Plot focal-plane arrangement
# -------------------------------------------------------------------
fig1, ax1 = fibervis.plot_arrangement(
    bundle,
    title="Hexagonal bundle – focal plane (µm)",
    xlabel="x (µm)",
    ylabel="y (µm)",
    show_index=True,
)
ax1.annotate(
    f"Filling factor = {ff:.2f}",
    xy=(0.05, 0.95),
    xycoords="axes fraction",
    va="top",
    fontsize=9,
)
fig1.savefig("hex_bundle_focal_plane.png", dpi=150, bbox_inches="tight")
print("Saved hex_bundle_focal_plane.png")

# -------------------------------------------------------------------
# 6.  Plot sky-projection
# -------------------------------------------------------------------
sky_ff = fibervis.filling_factor(sky)
fig2, ax2 = fibervis.plot_arrangement(
    sky,
    facecolor="tomato",
    title='Hexagonal bundle – sky projection (arcsec)',
    xlabel='x (")',
    ylabel='y (")',
)
ax2.annotate(
    f"Filling factor = {sky_ff:.2f}",
    xy=(0.05, 0.95),
    xycoords="axes fraction",
    va="top",
    fontsize=9,
)
fig2.savefig("hex_bundle_sky.png", dpi=150, bbox_inches="tight")
print("Saved hex_bundle_sky.png")

# -------------------------------------------------------------------
# 7.  Compare filling factors for different arrangements
# -------------------------------------------------------------------
bundles = {
    "Hexagonal\n(19 fib.)": fibervis.hexagonal_arrangement(19, 100.0, cladding=10.0),
    "Square\n(4×4)": fibervis.square_arrangement(4, 4, 100.0, cladding=10.0),
    "Annular\n(2 rings)": fibervis.annular_arrangement(2, 100.0, cladding=10.0),
}
fig3, ax3 = fibervis.plot_filling_factor(
    bundles,
    title="Filling factor comparison",
)
fig3.savefig("filling_factor_comparison.png", dpi=150, bbox_inches="tight")
print("Saved filling_factor_comparison.png")

plt.close("all")
print("Done.")
