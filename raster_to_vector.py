#!/usr/bin/env python3
"""Raster image to DXF converter for Visio-friendly vector workflows."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable, List

import cv2
import ezdxf
import numpy as np


class ConversionError(RuntimeError):
    """Raised when conversion cannot proceed."""


def load_binary_image(
    image_path: Path,
    threshold: int | None = None,
    invert: bool = False,
    blur_kernel: int = 5,
) -> np.ndarray:
    """Load image and return binary (black/white) numpy array."""
    image = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise ConversionError(f"Failed to load image at: {image_path}")

    if blur_kernel and blur_kernel > 1:
        image = cv2.GaussianBlur(image, (blur_kernel, blur_kernel), 0)

    if threshold is None:
        mode = cv2.THRESH_BINARY_INV if invert else cv2.THRESH_BINARY
        _, binary = cv2.threshold(image, 0, 255, mode + cv2.THRESH_OTSU)
    else:
        mode = cv2.THRESH_BINARY_INV if invert else cv2.THRESH_BINARY
        _, binary = cv2.threshold(image, threshold, 255, mode)

    return binary


def find_vector_paths(
    binary_image: np.ndarray,
    min_area: float = 4.0,
    simplify_epsilon: float = 1.0,
) -> List[np.ndarray]:
    """Extract contour paths from binary image."""
    contours, _ = cv2.findContours(
        binary_image,
        mode=cv2.RETR_LIST,
        method=cv2.CHAIN_APPROX_NONE,
    )

    vector_paths: List[np.ndarray] = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area < min_area:
            continue
        approx = cv2.approxPolyDP(contour, simplify_epsilon, closed=True)
        if len(approx) < 3:
            continue
        vector_paths.append(approx[:, 0, :])

    if not vector_paths:
        raise ConversionError("No vectorizable contours found. Try adjusting threshold/min-area.")

    return vector_paths


def write_dxf(
    paths: Iterable[np.ndarray],
    output_path: Path,
    scale: float = 1.0,
    layer_name: str = "RASTER_TRACE",
) -> None:
    """Write contour paths to DXF file as lightweight polylines."""
    doc = ezdxf.new(dxfversion="R2010")
    if layer_name not in doc.layers:
        doc.layers.add(layer_name)

    msp = doc.modelspace()

    for path in paths:
        points = [(float(x) * scale, -float(y) * scale) for x, y in path]
        msp.add_lwpolyline(points, close=True, dxfattribs={"layer": layer_name})

    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc.saveas(output_path)


def convert_raster_to_dxf(
    input_image: Path,
    output_dxf: Path,
    threshold: int | None = None,
    invert: bool = False,
    min_area: float = 4.0,
    simplify_epsilon: float = 1.0,
    scale: float = 1.0,
    blur_kernel: int = 5,
) -> None:
    """High-level conversion function."""
    binary = load_binary_image(input_image, threshold=threshold, invert=invert, blur_kernel=blur_kernel)
    paths = find_vector_paths(binary, min_area=min_area, simplify_epsilon=simplify_epsilon)
    write_dxf(paths, output_dxf, scale=scale)



def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Convert raster images (JPG/PNG/etc.) to vector DXF files suitable for Visio import.",
    )
    parser.add_argument("input", type=Path, help="Input raster image path.")
    parser.add_argument("output", type=Path, help="Output DXF path.")
    parser.add_argument("--threshold", type=int, default=None, help="Manual threshold (0-255). Otsu if omitted.")
    parser.add_argument("--invert", action="store_true", help="Invert thresholding (for dark foreground on light bg).")
    parser.add_argument("--min-area", type=float, default=4.0, help="Ignore contours smaller than this pixel area.")
    parser.add_argument("--epsilon", type=float, default=1.0, help="Contour simplification epsilon in pixels.")
    parser.add_argument("--scale", type=float, default=1.0, help="Scale factor from pixels to DXF units.")
    parser.add_argument("--blur-kernel", type=int, default=5, help="Gaussian blur kernel (odd integer >=1).")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.blur_kernel < 1 or args.blur_kernel % 2 == 0:
        parser.error("--blur-kernel must be an odd integer >= 1")

    try:
        convert_raster_to_dxf(
            input_image=args.input,
            output_dxf=args.output,
            threshold=args.threshold,
            invert=args.invert,
            min_area=args.min_area,
            simplify_epsilon=args.epsilon,
            scale=args.scale,
            blur_kernel=args.blur_kernel,
        )
    except ConversionError as exc:
        parser.error(str(exc))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
