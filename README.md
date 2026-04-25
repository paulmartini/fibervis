# fibervis

Tools for computing and visualizing IFU fiber systems.

## Modules

- `src/fibervis/fiber_layout.py` computes hexagonal IFU fiber layouts,
  field-of-view metrics, local arcsecond offsets, and optional RA/Dec
  projections.
- `src/fibervis/fits_rgb.py` builds Lupton RGB images from FITS cubes or
  multi-extension FITS files, overlays an IFU layout, and writes PNG output.
- `src/fibervis/legacy_tools.py` provides Legacy Survey cutout URL and
  download helpers shared by command-line scripts.

## Command-Line Examples

Generate the FITS cutout, write the fiber CSV, and render the overlay in one
command:

```bash
python bin/fiber_overlay.py \
  --get-fits \
  --write-layout \
  --center-ra 125.1886 \
  --center-dec 19.3622 \
  --n-fibers 567 \
  --fiber-diameter 1.0 \
  --separation-ratio 1.1 \
  cutout_125.1886_19.3622.fits ifu_layout.csv ifu_overlay.png
```

Render an overlay PNG from an existing FITS cutout and layout CSV:

```bash
python bin/fiber_overlay.py \
  --center-ra 125.1886 \
  --center-dec 19.3622 \
  cutout_125.1885_19.3626.fits ifu_sky.csv ifu_overlay.png
```

Download matching JPEG and FITS cutouts from the Legacy Survey viewer:

```bash
python bin/get_legacy.py 125.1885 19.3626 -o cutout_125.1885_19.3626
```

Write a layout CSV with arcsecond offsets (`x_arcsec`, `y_arcsec`) relative to
the layout center:

```bash
python bin/write_fiber_layout.py ifu_offsets.csv \
  --n-fibers 567 \
  --fiber-diameter 1.0 \
  --separation-ratio 1.1
```

Write a layout CSV with sky coordinates (`ra_deg`, `dec_deg`):

```bash
python bin/write_fiber_layout.py ifu_sky.csv \
  --n-fibers 567 \
  --fiber-diameter 1.0 \
  --separation-ratio 1.1 \
  --center-ra 125.1886 \
  --center-dec 19.3622
```

## Python Package Example

Import from `fibervis` and build a reusable layout-driven overlay workflow:

```python
from fibervis import IFULayout
from fibervis.fits_rgb import save_fiber_overlay_png
from fibervis.legacy_tools import download_cutout_file

center_ra = 125.1886
center_dec = 19.3622

layout = IFULayout(
    n_fibers=567,
    fiber_diameter=1.0,
    separation_ratio=1.1,
    center_ra=center_ra,
    center_dec=center_dec,
)

download_cutout_file(
    center_ra,
    center_dec,
    file_type="fits",
    output_path="cutout.fits",
)
layout.write_csv("ifu_sky.csv", include_sky=True)
save_fiber_overlay_png("cutout.fits", "ifu_overlay.png", layout)
```

Existing files are skipped by default. Add `--overwrite` to replace them.
