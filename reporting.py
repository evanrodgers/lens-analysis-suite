import cv2
import numpy as np
import json
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import asdict


def add_shadow_text(img: np.ndarray, text: str, org: Tuple[int, int],
                    font_scale: float, thickness: int) -> np.ndarray:
    """
    Add text to an image with a semi-transparent black background for improved readability.
    Font sizes are increased by 3x from the original implementation.

    Args:
        img: Input image
        text: Text to overlay
        org: Bottom-left position of the text (x, y)
        font_scale: Size of the font (will be multiplied by 3)
        thickness: Thickness of the font (will be adjusted for larger text)

    Returns:
        Image with overlaid text and background
    """
    # Increase font size and thickness for better visibility
    adjusted_scale = font_scale * 3.0
    adjusted_thickness = max(thickness * 2, 2)  # Increase thickness but ensure minimum of 2

    # Calculate text size for background rectangle
    text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX,
                                adjusted_scale, adjusted_thickness)[0]

    # Add extra padding for larger text
    padding = 15  # Increased padding for larger text

    # Define background rectangle coordinates
    bg_pts = np.array([
        [org[0] - padding, org[1] + padding],
        [org[0] + text_size[0] + padding, org[1] + padding],
        [org[0] + text_size[0] + padding, org[1] - text_size[1] - padding],
        [org[0] - padding, org[1] - text_size[1] - padding]
    ], dtype=np.int32)

    # Create semi-transparent background (50% opacity)
    overlay = img.copy()
    cv2.fillPoly(overlay, [bg_pts], (0, 0, 0))
    alpha = 0.5  # Set to exactly 50% opacity
    img = cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0)

    # Add text in white on the semi-transparent background
    cv2.putText(img, text, org, cv2.FONT_HERSHEY_SIMPLEX,
                adjusted_scale, (255, 255, 255), adjusted_thickness)

    return img


def generate_reports(image_path: Path, tiles_data: List[Dict], config: object,
                     timestamp: str, reports_dir: Path) -> None:
    """
    Generate both JSON and text reports for the analysis results.

    Args:
        image_path: Path to the original image
        tiles_data: Analysis results for each tile
        config: Analysis configuration settings
        timestamp: Timestamp for the analysis run
        reports_dir: Directory to save the reports
    """
    # Calculate average scores across all tiles
    average_scores = _calculate_average_scores(tiles_data)

    # Update tile filenames to be relative to working directory
    tiles_data = _update_tile_paths(tiles_data)

    # Prepare report data structure
    report_data = {
        "original_filename": image_path.name,
        "timestamp": timestamp,
        "configuration": asdict(config),
        "tiles": tiles_data,
        "average_scores": average_scores
    }

    # Create base filename using source image name
    base_filename = image_path.stem

    # Generate JSON report
    json_path = reports_dir / f"{base_filename}_analysis_{timestamp}.json"
    _generate_json_report(report_data, json_path)

    # Generate text report
    text_path = reports_dir / f"{base_filename}_report_{timestamp}.txt"
    _generate_text_report(report_data, text_path)


def _update_tile_paths(tiles_data: List[Dict]) -> List[Dict]:
    """
    Update tile filenames to be relative paths instead of absolute.

    Args:
        tiles_data: List of dictionaries containing tile data

    Returns:
        Updated tiles data with relative paths
    """
    updated_tiles = []
    for tile in tiles_data:
        updated_tile = tile.copy()
        # Keep only the filename without full path
        updated_tile["filename"] = Path(tile["filename"]).name
        updated_tiles.append(updated_tile)
    return updated_tiles


def _calculate_average_scores(tiles_data: List[Dict]) -> Dict[str, float]:
    """
    Calculate average scores for each analysis method across all tiles.
    """
    all_scores = {}
    for tile in tiles_data:
        for method, score in tile["scores"].items():
            if method not in all_scores:
                all_scores[method] = []
            all_scores[method].append(score)

    return {method: sum(scores) / len(scores)
            for method, scores in all_scores.items()}


def _generate_json_report(report_data: Dict, json_path: Path) -> None:
    """
    Generate a detailed JSON report containing all analysis data.

    Args:
        report_data: Dictionary containing all analysis results and configuration
        json_path: Path where the JSON report should be saved
    """
    with open(json_path, 'w') as f:
        json.dump(report_data, f, indent=4)


def _generate_text_report(report_data: Dict, text_path: Path) -> None:
    """
    Generate a human-readable text report with detailed analysis explanation.

    Args:
        report_data: Dictionary containing all analysis results and configuration
        text_path: Path where the text report should be saved
    """
    with open(text_path, 'w') as f:
        f.write(f"Lens Test Analysis Report\n")
        f.write(f"========================\n\n")

        # Basic information
        f.write(f"Original Image: {report_data['original_filename']}\n")
        f.write(f"Analysis Date: {report_data['timestamp']}\n\n")

        # Configuration details
        config = report_data['configuration']
        f.write("Configuration Settings\n")
        f.write("---------------------\n")
        f.write(f"Crop values:\n")
        f.write(f"  - Top: {config['crop_top']:.1%}\n")
        f.write(f"  - Bottom: {config['crop_bottom']:.1%}\n")
        f.write(f"  - Left: {config['crop_left']:.1%}\n")
        f.write(f"  - Right: {config['crop_right']:.1%}\n")
        f.write(f"Horizontal sections: {config['horizontal_sections']}\n")
        f.write(f"Analysis methods: {', '.join(config['analysis_methods'])}\n\n")

        # Analysis methods explanation
        f.write("Analysis Methods Description\n")
        f.write("---------------------------\n")
        f.write("Each analysis method produces a normalized score from 1-100:\n\n")
        f.write("1. Laplacian Variance Method:\n")
        f.write("   Measures local pixel intensity variations to detect edges.\n")
        f.write("   Higher scores indicate sharper, more defined edges.\n\n")
        f.write("2. Sobel Gradient Method:\n")
        f.write("   Calculates intensity gradients in horizontal and vertical directions.\n")
        f.write("   Higher scores indicate stronger edge definition and contrast.\n\n")
        f.write("3. Tenengrad Algorithm:\n")
        f.write("   Uses thresholded Sobel gradients for noise-resistant edge detection.\n")
        f.write("   Higher scores indicate better overall image sharpness.\n\n")

        # Pre-processing explanation
        f.write("Pre-processing Steps\n")
        f.write("-------------------\n")
        f.write("1. Image Cropping:\n")
        f.write("   Applied specified margin crops to focus on the relevant image area.\n\n")

        # Results summary
        f.write("Results Summary\n")
        f.write("--------------\n")
        for method, avg_score in report_data["average_scores"].items():
            f.write(f"{method.capitalize()} - Average score: {avg_score:.1f}\n")

        # Detailed results
        f.write("\nDetailed Results by Tile\n")
        f.write("----------------------\n")
        for tile in report_data["tiles"]:
            f.write(f"\nTile {tile['coordinate']}:\n")
            for method, score in tile["scores"].items():
                f.write(f"  - {method}: {score:.1f}\n")