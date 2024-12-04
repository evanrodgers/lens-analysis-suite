import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import logging


def load_analysis_data(json_path: Path) -> tuple:
    """
    Load and parse the lens analysis JSON file.

    Args:
        json_path: Path to the JSON file containing analysis data

    Returns:
        Tuple of (data dict, list of metrics)
    """
    try:
        with open(json_path) as f:
            data = json.load(f)

        # Validate data structure
        if 'tiles' not in data or not data['tiles']:
            raise ValueError("JSON file must contain a 'tiles' array with analysis data")

        if 'scores' not in data['tiles'][0]:
            raise ValueError("Each tile must contain a 'scores' object with analysis metrics")

        # Extract available metrics
        metrics = list(data['tiles'][0]['scores'].keys())
        return data, metrics

    except json.JSONDecodeError:
        raise ValueError("Invalid JSON format in analysis file")
    except Exception as e:
        raise ValueError(f"Error reading analysis file: {str(e)}")


def create_data_grid(data: dict, metric: str) -> tuple:
    """
    Convert the JSON data into a 2D numpy array for heatmap plotting.
    Grid is oriented to match the test chart where:
    - Letters (A-F) are rows (y-axis)
    - Numbers (1-10) are columns (x-axis)

    Args:
        data: Dictionary containing the analysis data
        metric: Name of the metric to plot

    Returns:
        Tuple of (grid array, row labels, column labels)
    """
    # Find grid dimensions from the data
    coords = [tile['coordinate'] for tile in data['tiles']]
    letters = sorted(set(coord[0] for coord in coords))  # Letters (A, B, C...) for rows
    numbers = sorted(set(int(coord[1:]) for coord in coords))  # Numbers (1, 2, 3...) for columns

    # Initialize grid with letters as rows (y) and numbers as columns (x)
    grid = np.zeros((len(letters), len(numbers)))

    # Create mapping for letters to row indices
    row_map = {letter: idx for idx, letter in enumerate(letters)}

    # Fill the grid
    for tile in data['tiles']:
        letter = tile['coordinate'][0]
        number = int(tile['coordinate'][1:])
        row = row_map[letter]      # Letter determines y position
        col = number - 1           # Number determines x position
        grid[row, col] = tile['scores'][metric]

    return grid, letters, numbers


def plot_heatmap(grid: np.ndarray, metric: str, letters: list, numbers: list,
                output_path: Path, title: str = None) -> None:
    """
    Create and save a heatmap visualization matching the test chart orientation.

    Args:
        grid: 2D numpy array of scores
        metric: Name of the metric being visualized
        letters: List of row labels (letters)
        numbers: List of column labels (numbers)
        output_path: Path where the heatmap should be saved
        title: Optional custom title for the plot
    """
    # Calculate figure size for 3:2 aspect ratio
    base_width = 12
    fig_width = base_width
    fig_height = (base_width * 2) / 3

    plt.figure(figsize=(fig_width, fig_height))

    # Create the heatmap
    ax = sns.heatmap(
        grid,
        annot=True,
        fmt='.1f',
        cmap='Blues',
        cbar_kws={
            'label': f'{metric.capitalize()} Score',
            'orientation': 'vertical'
        },
        xticklabels=numbers,  # Numbers for x-axis (columns)
        yticklabels=letters   # Letters for y-axis (rows)
    )

    # Set title
    if title is None:
        title = f'Lens Sharpness Analysis - {metric.capitalize()}'
    plt.title(title, pad=20)

    # Add labels
    plt.xlabel('Horizontal Position (Left to Right)', labelpad=10)
    plt.ylabel('Vertical Position (Center to Edge)', labelpad=10)

    # Rotate labels for better readability
    plt.xticks(rotation=0)
    plt.yticks(rotation=0)

    # Add statistics
    stats_text = (f'Min: {grid.min():.1f}  Max: {grid.max():.1f}  '
                 f'Mean: {grid.mean():.1f}')
    plt.figtext(0.99, 0.01, stats_text, ha='right', va='bottom', fontsize=8)

    # Add filename at the bottom
    filename = output_path.stem.replace(f"_{metric}_heatmap", "")
    plt.figtext(0.01, 0.01, filename, ha='left', va='bottom', fontsize=8)

    # Save plot
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()


def generate_heatmaps(json_path: Path, output_dir: Path) -> None:
    """
    Generate heatmaps for all metrics in the analysis data.

    Args:
        json_path: Path to the JSON file containing analysis data
        output_dir: Directory where heatmaps should be saved
    """
    try:
        # Load and validate data
        logging.debug(f"Loading analysis data from {json_path}")
        data, metrics = load_analysis_data(json_path)

        # Get base filename without timestamp
        base_name = json_path.stem.split('_analysis_')[0]

        logging.debug(f"Generating {len(metrics)} heatmaps for {base_name}")

        # Generate heatmaps for each metric
        for metric in metrics:
            logging.debug(f"Processing {metric} data...")

            # Create the data grid
            grid, letters, numbers = create_data_grid(data, metric)

            # Generate output filename
            output_path = output_dir / f"{base_name}_{metric}_heatmap.png"

            # Create and save the heatmap
            plot_heatmap(grid, metric, letters, numbers, output_path)

            logging.debug(f"Saved heatmap to: {output_path}")
            logging.debug(f"Score range: {grid.min():.1f} - {grid.max():.1f}, "
                        f"Average: {grid.mean():.1f}")

    except Exception as e:
        logging.error(f"Error generating heatmaps: {str(e)}")
        raise