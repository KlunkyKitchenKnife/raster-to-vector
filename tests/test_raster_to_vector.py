from pathlib import Path

import cv2
import numpy as np

from raster_to_vector import convert_raster_to_dxf, find_vector_paths, load_binary_image


def test_find_vector_paths_simple_rectangle() -> None:
    image = np.zeros((100, 100), dtype=np.uint8)
    cv2.rectangle(image, (20, 20), (80, 80), 255, -1)

    paths = find_vector_paths(image, min_area=20, simplify_epsilon=1.0)

    assert len(paths) >= 1
    assert all(path.shape[1] == 2 for path in paths)


def test_end_to_end_conversion(tmp_path: Path) -> None:
    input_path = tmp_path / "input.png"
    output_path = tmp_path / "output.dxf"

    image = np.zeros((120, 120), dtype=np.uint8)
    cv2.circle(image, (60, 60), 30, 255, -1)
    cv2.imwrite(str(input_path), image)

    convert_raster_to_dxf(input_path, output_path, min_area=20)

    assert output_path.exists()
    text = output_path.read_text(errors="ignore")
    assert "LWPOLYLINE" in text


def test_load_binary_image_otsu(tmp_path: Path) -> None:
    input_path = tmp_path / "input.png"
    image = np.tile(np.arange(0, 255, dtype=np.uint8), (50, 1))
    cv2.imwrite(str(input_path), image)

    binary = load_binary_image(input_path)
    values = np.unique(binary)

    assert set(values.tolist()).issubset({0, 255})
