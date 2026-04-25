# fibervis

**fibervis** is a Python library with tools to produce visualizations of fiber
systems for astronomical spectrographs.  It includes:

- **Sky-projection images** of different fiber arrangements (hexagonal,
  square, annular, and custom).
- **Filling factor & attenuation calculations** — geometric filling factor,
  focal-ratio degradation (FRD) throughput, and bulk fiber attenuation.
- **Slit-head design drawings** — linear and curved slit layouts rendered as
  publication-quality Matplotlib figures.

---

## Installation

```bash
pip install .
```

Dependencies: `numpy`, `matplotlib`, `scipy`.

---

## Quick start

```python
import fibervis

# Create a 7-fiber hexagonal bundle (100-µm cores, f/4)
bundle = fibervis.hexagonal_arrangement(7, fiber_diameter=100.0, focal_ratio=4.0)

# Project onto the sky (plate scale 0.2 arcsec/µm)
sky = fibervis.sky_projection(bundle, plate_scale=0.2)

# Compute the geometric filling factor
ff = fibervis.filling_factor(bundle)
print(f"Filling factor: {ff:.3f}")

# Plot the arrangement
fig, ax = fibervis.plot_arrangement(sky, xlabel='x (")', ylabel='y (")',
                                    title="7-fiber hexagonal IFU")
fig.savefig("hex_ifu.png", dpi=150, bbox_inches="tight")

# Linear slit head
slit = fibervis.linear_slit(20, fiber_diameter=100.0)
fig, ax = fibervis.plot_slit(slit, show_index=True)
fig.savefig("slit.png", dpi=150, bbox_inches="tight")
```

---

## Modules

| Module | Contents |
|---|---|
| `fibervis.fiber` | `Fiber`, `FiberBundle` core classes |
| `fibervis.arrangements` | `hexagonal_arrangement`, `square_arrangement`, `annular_arrangement`, `custom_arrangement`, `sky_projection` |
| `fibervis.filling` | `filling_factor`, `focal_ratio_degradation`, `fiber_attenuation`, `total_throughput` |
| `fibervis.slit` | `SlitHead`, `linear_slit`, `curved_slit` |
| `fibervis.plot` | `plot_arrangement`, `plot_slit`, `plot_throughput`, `plot_filling_factor` |

---

## Examples

See the `examples/` directory:

- `examples/sky_projection_example.py` — hexagonal IFU, sky projection, filling factor comparison.
- `examples/slit_head_example.py` — linear and curved slit heads, attenuation vs. length.

---

## Running tests

```bash
pip install pytest
pytest
```

---

## License

GPL v3 — see [LICENSE](LICENSE).
