# fibervis

Tools for computing and visualizing IFU fiber systems.

## Modules

- `src/fibervis/fiber_layout.py` computes hexagonal IFU fiber layouts,
  field-of-view metrics, local arcsecond offsets, and optional RA/Dec
  projections.
- `src/fibervis/fits_rgb.py` builds Lupton RGB images from FITS cubes or
  multi-extension FITS files, overlays an IFU layout, and writes PNG output.

## Examples

```python
from fibervis import IFULayout
from fibervis.fits_rgb import save_fiber_overlay_png

layout = IFULayout(
    n_fibers=567,
    fiber_diameter=1.0,
    separation_ratio=1.1,
    center_ra=125.1886,
    center_dec=19.3622,
)

print(layout.metrics())
layout.write_csv("ifu_coords.csv")

save_fiber_overlay_png(
    "cutout.fits",
    "ifu_overlay.png",
    layout,
    red=2,
    green=1,
    blue=0,
    scales=(1.0, 1.5, 2.5),
    q=10,
    stretch=0.2,
)
```

Write a layout CSV from the command line:

```bash
python bin/write_fiber_layout.py ifu_offsets.csv \
  --n-fibers 567 \
  --fiber-diameter 1.0 \
  --separation-ratio 1.1
```

When no center is provided, the output coordinate columns are `x_arcsec` and
`y_arcsec`, measured relative to `(0, 0)` at the IFU center.

```bash
python bin/write_fiber_layout.py ifu_sky.csv \
  --n-fibers 567 \
  --fiber-diameter 1.0 \
  --separation-ratio 1.1 \
  --center-ra 125.1886 \
  --center-dec 19.3622
```

When `--center-ra` and `--center-dec` are provided together, the output
coordinate columns are `ra_deg` and `dec_deg`.

Create an RGB fiber overlay PNG from a Legacy Survey FITS cutout and a fiber
CSV. By default, the plot includes a stats box in the upper-left corner:

```bash
python bin/fiber_overlay.py \
  --center-ra 125.1886 \
  --center-dec 19.3622 \
  cutout_125.1885_19.3626.fits ifu_sky.csv ifu_overlay.png
```

## Legacy Survey Cutouts

Download matching JPEG and FITS cutouts from the Legacy Survey viewer:

```bash
python get_legacy.py 125.1885 19.3626 -o cutout_125.1885_19.3626
```

Existing files are skipped by default. Add `--overwrite` to replace them.
