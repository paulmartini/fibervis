"""
Example: Slit-head design drawings.

Demonstrates creating a linear and a curved slit head and producing
design-drawing plots.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import fibervis

# -------------------------------------------------------------------
# 1.  Linear slit – 20 fibres, 100-µm core, touching
# -------------------------------------------------------------------
linear = fibervis.linear_slit(
    n_fibers=20,
    fiber_diameter=100.0,
    focal_ratio=4.0,
    name="Linear slit (20 fibres)",
)
print(f"Linear slit: {linear}")
print(f"  Slit length: {linear.slit_length:.1f} µm")
print(f"  Dispersion direction: {linear.dispersion_direction()}")

fig1, ax1 = fibervis.plot_slit(
    linear,
    show_index=True,
    title=linear.name,
)
fig1.savefig("slit_linear.png", dpi=150, bbox_inches="tight")
print("Saved slit_linear.png")

# -------------------------------------------------------------------
# 2.  Curved slit – 20 fibres on a 10 000-µm radius arc
# -------------------------------------------------------------------
curved = fibervis.curved_slit(
    n_fibers=20,
    fiber_diameter=100.0,
    radius=10_000.0,
    focal_ratio=4.0,
    name="Curved slit (20 fibres, R=10 mm)",
)
print(f"\nCurved slit: {curved}")
print(f"  Slit length: {curved.slit_length:.1f} µm")

fig2, ax2 = fibervis.plot_slit(
    curved,
    show_index=True,
    title=curved.name,
)
fig2.savefig("slit_curved.png", dpi=150, bbox_inches="tight")
print("Saved slit_curved.png")

# -------------------------------------------------------------------
# 3.  Throughput as a function of fiber length for various attenuation
#     coefficients
# -------------------------------------------------------------------
import numpy as np

lengths = np.linspace(0, 30, 200)  # 0–30 m

fig3, ax3 = plt.subplots(figsize=(6, 4))
for alpha_db in [0.05, 0.10, 0.20, 0.50]:
    throughputs = [fibervis.fiber_attenuation(L, alpha_db) for L in lengths]
    fibervis.plot_throughput(
        lengths,
        throughputs,
        ax=ax3,
        label=f"{alpha_db:.2f} dB/m",
        xlabel="Fiber length (m)",
        ylabel="Transmission",
        title="Fiber bulk attenuation",
    )
ax3.legend(title="Attenuation coeff.")
fig3.savefig("fiber_attenuation.png", dpi=150, bbox_inches="tight")
print("Saved fiber_attenuation.png")

plt.close("all")
print("Done.")
