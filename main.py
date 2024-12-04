import os
import logging
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass

from sharpness_analyzer import SharpnessAnalyzer
from image_processor import ImageProcessor, AnalysisConfig
from visualization import generate_heatmaps


def setup_logging(log_file: Path) -> None:
    """
    Set up logging to both file and console with different levels.

    Args:
        log_file: Path to the log file
    """
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # Set up file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Set up console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)


def get_yes_no_input(prompt: str, default: bool = True) -> bool:
    """
    Get yes/no input from user with a default value.
    """
    default_str = "Y/n" if default else "y/N"
    response = input(f"{prompt} [{default_str}]: ").strip().lower()
    return response.startswith('y') if response else default


def get_user_config() -> tuple[AnalysisConfig, bool]:
    """
    Interactive configuration setup for analysis parameters.
    Returns tuple of (AnalysisConfig, generate_heatmaps_flag)
    """
    print("\nLens Test Image Analysis Configuration")
    print("=====================================")

    # Available analysis methods with descriptions
    available_methods = {
        '1': ('laplacian', 'Laplacian method - default, most sensitive'),
        '2': ('sobel', 'Sobel method - use only for high-noise images'),
        '3': ('tenengrad', 'Tenengrad - use only for high-noise images')
    }

    # Get analysis methods
    print("\nAvailable analysis methods:")
    for key, (method, description) in available_methods.items():
        print(f"{key}: {description}")
    print("4: All methods")

    choice = input("\nSelect analysis methods (press Enter for default [Laplacian], "
                   "or enter comma-separated numbers, e.g. '1,2' or '4' for all): ").strip()

    # Handle method selection
    if not choice:
        methods = ['laplacian']
    elif choice == '4':
        methods = [method for method, _ in available_methods.values()]
    else:
        try:
            selected = [available_methods[n.strip()][0]
                        for n in choice.split(',')
                        if n.strip() in available_methods]
            methods = selected if selected else ['laplacian']
        except:
            print("Invalid selection. Using default (Laplacian method).")
            methods = ['laplacian']

    # Get crop values with new percentage range (0-100)
    def get_crop_value(side: str) -> float:
        while True:
            try:
                value = float(input(f"Enter {side} margin crop percentage (0-100): ").strip())
                if 0 <= value <= 100:
                    return value
                print("Value must be between 0 and 100.")
            except ValueError:
                print("Please enter a valid number.")

    crop_top = get_crop_value("top")
    crop_bottom = get_crop_value("bottom")
    crop_left = get_crop_value("left")
    crop_right = get_crop_value("right")

    # Get number of sections
    while True:
        try:
            sections = int(input("\nEnter number of horizontal sections (1-20): ").strip())
            if 1 <= sections <= 20:
                break
            print("Number must be between 1 and 20.")
        except ValueError:
            print("Please enter a valid number.")

    # Ask about heatmap generation up front
    generate_heatmaps_flag = get_yes_no_input("\nWould you like to generate heatmap visualizations?")

    return (AnalysisConfig(
        crop_top=crop_top,
        crop_bottom=crop_bottom,
        crop_left=crop_left,
        crop_right=crop_right,
        horizontal_sections=sections,
        analysis_methods=methods
    ), generate_heatmaps_flag)


def setup_directory_structure(root_dir: Path) -> tuple[Path, Path, Path]:
    """
    Create the reports, heatmaps, and working_files directories inside the root directory.

    Args:
        root_dir: Path to the root directory containing lens samples

    Returns:
        Tuple of (reports_dir, heatmaps_dir, working_files_dir)
    """
    reports_dir = root_dir / "reports"
    heatmaps_dir = root_dir / "heatmaps"
    working_files_dir = root_dir / "working_files"

    reports_dir.mkdir(exist_ok=True)
    heatmaps_dir.mkdir(exist_ok=True)
    working_files_dir.mkdir(exist_ok=True)

    return reports_dir, heatmaps_dir, working_files_dir


def process_lens_directory(lens_dir: Path, config: AnalysisConfig,
                           reports_dir: Path, heatmaps_dir: Path,
                           working_files_dir: Path,
                           generate_heatmaps_flag: bool) -> None:
    """
    Process all images in a single lens directory.

    Args:
        lens_dir: Path to directory containing lens samples
        config: Analysis configuration
        reports_dir: Path to reports directory
        heatmaps_dir: Path to heatmaps directory
        working_files_dir: Path to working files directory
        generate_heatmaps_flag: Whether to generate heatmaps
    """
    lens_name = lens_dir.name
    logging.info(f"Processing {lens_name}...")

    # Create output directories for this lens
    lens_reports_dir = reports_dir / lens_name
    lens_heatmaps_dir = heatmaps_dir / lens_name
    lens_working_dir = working_files_dir / lens_name

    lens_reports_dir.mkdir(exist_ok=True)
    if generate_heatmaps_flag:
        lens_heatmaps_dir.mkdir(exist_ok=True)
    lens_working_dir.mkdir(exist_ok=True)
    (lens_working_dir / "tiles").mkdir(exist_ok=True)

    # Initialize processor
    processor = ImageProcessor(config)

    # Process each JPEG in the lens directory
    jpeg_files = sorted(list(lens_dir.glob("*.jp*g")))
    if not jpeg_files:
        logging.warning(f"No JPEG files found in {lens_dir}")
        return

    for jpeg_file in jpeg_files:
        aperture = jpeg_file.stem.split('_')[-1]  # Assumes filename format ending with fX.X
        logging.info(f"- Analyzing {aperture} sample...")
        logging.debug(f"Processing file: {jpeg_file}")

        try:
            # Process the image
            processor.process_image(jpeg_file, lens_working_dir, lens_reports_dir)

            # Generate heatmap if requested
            if generate_heatmaps_flag:
                latest_json = lens_reports_dir / f"{jpeg_file.stem}_analysis_{processor.timestamp}.json"
                if latest_json.exists():
                    generate_heatmaps(latest_json, lens_heatmaps_dir)
                else:
                    logging.error(f"Analysis JSON not found for {jpeg_file.name}")

        except Exception as e:
            logging.error(f"Error processing {jpeg_file.name}: {str(e)}")


def main():
    """
    Main program entry point. Handles user interaction and orchestrates
    the image analysis process.
    """
    try:
        # Get directory path from user
        while True:
            directory_path = input("\nPlease enter the path to your lens samples directory: ").strip()
            root_dir = Path(directory_path)
            if root_dir.is_dir():
                break
            print("Invalid directory path. Please try again.")

        # Set up logging
        log_file = root_dir / "lens_analysis.log"
        setup_logging(log_file)
        logging.info("Starting lens analysis application")

        # Get user configuration (including heatmap preference)
        config, generate_heatmaps_flag = get_user_config()

        # Set up directory structure
        reports_dir, heatmaps_dir, working_files_dir = setup_directory_structure(root_dir)
        logging.info(f"Created output directories in {root_dir}")

        # Get all lens directories (excluding output directories)
        excluded_dirs = {'reports', 'heatmaps', 'working_files'}
        lens_dirs = [d for d in root_dir.iterdir()
                     if d.is_dir() and d.name not in excluded_dirs]

        if not lens_dirs:
            logging.error("No lens directories found")
            return

        logging.info(f"Found {len(lens_dirs)} lens directories to process")

        # Process each lens directory
        for lens_dir in sorted(lens_dirs):
            process_lens_directory(
                lens_dir,
                config,
                reports_dir,
                heatmaps_dir,
                working_files_dir,
                generate_heatmaps_flag
            )

        logging.info("Analysis complete!")
        logging.info(f"Reports can be found in: {reports_dir}")
        if generate_heatmaps_flag:
            logging.info(f"Heatmaps can be found in: {heatmaps_dir}")

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        raise


if __name__ == "__main__":
    main()