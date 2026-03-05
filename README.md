# Raster to Vector (DXF for Visio)

Yes — this is a sensible endeavor.

Microsoft Visio can import/edit vector CAD content more reliably from **DXF** than from raw raster formats (JPG/PNG). This project converts raster edges/shapes into DXF polylines so they can be recognized and edited as vector geometry in Visio.

## What this supports

- Input: JPG, PNG, BMP, TIFF, etc. (anything OpenCV can read)
- Output: DXF (R2010)
- Workflow: threshold image -> find contours -> simplify -> write polylines

> Note: Native DWG writing usually requires proprietary SDK/tooling. This project writes DXF directly, which is broadly compatible with Visio. If DWG is absolutely required, convert generated DXF to DWG with a separate CAD converter.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
python raster_to_vector.py input.png output.dxf
```

Useful options:

```bash
python raster_to_vector.py input.png output.dxf \
  --invert \
  --min-area 10 \
  --epsilon 1.5 \
  --scale 0.1
```

## Import into Visio

1. Open Visio.
2. Use **Insert -> CAD Drawing** (or open/import DXF).
3. Ungroup or convert imported geometry as needed for editing.

## Tips for better results

- Use high-contrast source images.
- Pre-clean noise in the raster image.
- Tune `--min-area` and `--epsilon` to balance detail vs smoothness.
- For dark shapes on light backgrounds, `--invert` may improve tracing.
