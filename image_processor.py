import cv2
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass
import logging
from datetime import datetime

from sharpness_analyzer import SharpnessAnalyzer
from reporting import generate_reports, add_shadow_text


@dataclass
class AnalysisConfig:
    """Configuration settings for image analysis."""
    crop_top: float = 0.0
    crop_bottom: float = 0.0
    crop_left: float = 0.0
    crop_right: float = 0.0
    horizontal_sections: int = 5
    analysis_methods: List[str] = None

    def __post_init__(self):
        if self.analysis_methods is None:
            self.analysis_methods = ["laplacian", "sobel", "tenengrad"]

        # Validate configuration
        if not 1 <= self.horizontal_sections <= 20:
            raise ValueError("Horizontal sections must be between 1 and 20")

        for crop in [self.crop_top, self.crop_bottom, self.crop_left, self.crop_right]:
            if not 0 <= crop <= 100:
                raise ValueError("Crop values must be between 0 and 100")

        # Convert percentage to decimal
        self.crop_top /= 100
        self.crop_bottom /= 100
        self.crop_left /= 100
        self.crop_right /= 100


class ImageProcessor:
    """Handles all image processing operations including cropping and analysis."""

    def __init__(self, config: AnalysisConfig):
        self.config = config
        self.analyzer = SharpnessAnalyzer()
        self.timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    def process_image(self, image_path: Path, working_dir: Path, reports_dir: Path) -> None:
        """
        Process a single image file.

        Args:
            image_path: Path to the image file
            working_dir: Directory for intermediate files (tiles, etc.)
            reports_dir: Directory for final analysis reports
        """
        # Create tiles directory in working directory
        tiles_dir = working_dir / "tiles"
        tiles_dir.mkdir(exist_ok=True)

        # Read and process image
        image = cv2.imread(str(image_path))
        if image is None:
            logging.error(f"Failed to read image: {image_path}")
            return

        logging.debug(f"Processing image: {image_path}")

        try:
            # Process image
            cropped = self._crop_image(image)

            # Save processed version to working directory
            cv2.imwrite(str(working_dir / f"{image_path.stem}_cropped.jpg"), cropped)

            # Process tiles and generate reports
            tiles_data = self._process_tiles(cropped, image_path.stem, tiles_dir)
            self._create_overview(cropped, tiles_data, image_path.stem, working_dir)
            generate_reports(image_path, tiles_data, self.config, self.timestamp, reports_dir)

            logging.debug(f"Successfully processed image: {image_path}")

        except Exception as e:
            logging.error(f"Error processing {image_path}: {str(e)}")
            raise

    def _crop_image(self, image: np.ndarray) -> np.ndarray:
        """Apply cropping based on configuration."""
        h, w = image.shape[:2]
        top = int(h * self.config.crop_top)
        bottom = int(h * (1 - self.config.crop_bottom))
        left = int(w * self.config.crop_left)
        right = int(w * (1 - self.config.crop_right))
        return image[top:bottom, left:right]

    def _process_tiles(self, image: np.ndarray, base_filename: str, tiles_dir: Path) -> List[Dict]:
        """
        Split image into tiles and analyze each one.

        Args:
            image: Input image to process
            base_filename: Base name for output files
            tiles_dir: Directory to save tile images
        """
        h, w = image.shape[:2]
        aspect_ratio = w / h
        vertical_sections = max(1, int(self.config.horizontal_sections / aspect_ratio))

        tile_w = w // self.config.horizontal_sections
        tile_h = h // vertical_sections

        tiles_data = []
        for i in range(vertical_sections):
            for j in range(self.config.horizontal_sections):
                tile = image[i * tile_h:(i + 1) * tile_h, j * tile_w:(j + 1) * tile_w]
                coord = f"{chr(65 + i)}{j + 1}"
                scores = self._analyze_tile(tile)

                tile_with_overlay = self._create_tile_overlay(tile, coord, scores)
                tile_filename = f"{base_filename}_{coord}_{self.timestamp}.jpg"
                cv2.imwrite(str(tiles_dir / tile_filename), tile_with_overlay)

                tiles_data.append({
                    "coordinate": coord,
                    "filename": tile_filename,
                    "scores": scores
                })

        return tiles_data

    def _analyze_tile(self, tile: np.ndarray) -> Dict[str, float]:
        """Apply selected analysis methods to a tile."""
        scores = {}
        for method in self.config.analysis_methods:
            if method == "laplacian":
                scores["laplacian"] = self.analyzer.laplacian_variance(tile)
            elif method == "sobel":
                scores["sobel"] = self.analyzer.sobel_gradient(tile)
            elif method == "tenengrad":
                scores["tenengrad"] = self.analyzer.tenengrad(tile)
        return scores

    def _create_tile_overlay(self, tile: np.ndarray, coord: str, scores: Dict[str, float]) -> np.ndarray:
        """Create overlay with coordinate and scores on tile."""
        overlay = tile.copy()
        h = overlay.shape[0]
        y_pos = h - 50

        text = f"Coordinate: {coord}"
        overlay = add_shadow_text(overlay, text, (30, y_pos), 0.5, 1)
        y_pos -= 75

        for method, score in scores.items():
            text = f"{method}: {score:.1f}"
            overlay = add_shadow_text(overlay, text, (30, y_pos), 0.5, 1)
            y_pos -= 75

        return overlay

    def _create_overview(self, image: np.ndarray, tiles_data: List[Dict],
                         base_filename: str, output_dir: Path) -> None:
        """Create overview image with grid and scores."""
        overview = image.copy()
        h, w = overview.shape[:2]

        # Draw grid lines
        for i in range(self.config.horizontal_sections):
            x = int(w * (i + 1) / self.config.horizontal_sections)
            cv2.line(overview, (x, 0), (x, h), (255, 255, 255), 2)

        vertical_sections = len(set(tile["coordinate"][0] for tile in tiles_data))
        for i in range(vertical_sections):
            y = int(h * (i + 1) / vertical_sections)
            cv2.line(overview, (0, y), (w, y), (255, 255, 255), 2)

        # Add coordinates and scores
        for tile_data in tiles_data:
            coord = tile_data["coordinate"]
            row = ord(coord[0]) - 65
            col = int(coord[1:]) - 1

            x = int(w * col / self.config.horizontal_sections) + 60
            y = int(h * row / vertical_sections) + int(h / (2 * vertical_sections))

            text = f"{coord}"
            overview = add_shadow_text(overview, text, (x, y), 1.0, 2)

            y_offset = 120
            for method, score in tile_data["scores"].items():
                text = f"{method}: {score:.1f}"
                overview = add_shadow_text(overview, text, (x, y + y_offset), 0.7, 2)
                y_offset += 105

        # Save the overview image
        output_path = output_dir / f"{base_filename}_overview_{self.timestamp}.jpg"
        cv2.imwrite(str(output_path), overview)
        logging.debug(f"Created overview image: {output_path}")