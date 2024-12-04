# Lens Analysis Suite

A Python-based tool for quantitative analysis of lens sharpness characteristics across the image frame. This application helps photographers, reviewers, and manufacturers evaluate lens performance through automated analysis of test chart images.

### Sharpness heatmap

filename: contax_25mm_f28_laplacian_heatmap.png

![Alt text](/docs/contax_25mm_f28_laplacian_heatmap.png)

### Original test image

filename: contax_25mm_f28.jpg

![Alt text](/docs/contax_25mm_f28_cropped.jpg)

### Original test image with Laplacian scores overlaid

filename: contax_25mm_f28_overview_{timestamp}.jpg

![Alt text](/docs/contax_25mm_f28_overview_20241204151729.jpg)

## Creating the physical test poster

In the images above you can see that I am using a right-angle checkerboard pattern.

I printed the checkerboard pattern onto glossy photopaper that comes with adhesive backing (very cheap and source-able on Amazon).

I then stuck those to a piece of foam poster board and propped it up using a 3D printed stand, but it would be more ideal to mount your test pattern to a wall, and mount your camera on a sturdy tripod. Axial misalignment will impact the sharpness scores, so try to align your sensor to be as parallel to the test pattern board as possible.

I snagged the checkerboard pattern from here: https://www.freepik.com/free-vector/right-triangle-pattern-background_158726687.htm

You could also recreate it easily in Photoshop by creating a custom pattern, then using Edit > Fill > Pattern.

Why a right-angle checkerboard? It's the most compatible with all three analysis methods.

## Other notes

Be sure to shoot your test samples at the lowest ISO possible, as the Laplacian Variance test is sensitive to noise. In practice, this becomes tricky at higher F-stops, so I recommend lowering the shutter speed for every f-stop so that the ISO remains between 100 and 200. I would also recommend setting up a 2s delay in your camera's Drive Mode, or using a remote shutter, when you're testing at longer shutter speeds.

This is why a sturdy tripod is essential if you're testing several lenses and repeatedly changing the shutter speed. Still, this application will produce useful results without perfect test images.

## Features

### Analysis Methods
- **Laplacian Variance**: Measures local contrast and edge definition
- **Sobel Gradient**: Analyzes intensity changes in horizontal and vertical directions
- **Tenengrad Algorithm**: Provides noise-resistant edge detection
- All methods produce normalized scores (1-100) for easy comparison

### Image Processing
- Configurable image cropping
- Grid-based analysis with customizable sections
- Preservation of spatial relationships in results

### Visualization
- Interactive heatmap generation
- Color-coded score representation
- Grid coordinate system (A1, B2, etc.)
- Statistical overlays and summaries
- Overview images with score annotations

### Reporting
- Detailed JSON reports for programmatic analysis
- Human-readable text reports
- Complete configuration records
- Statistical summaries
- Individual tile scores

## Requirements

- Python 3.8 or higher
- Operating System: Windows, macOS, or Linux
- Minimum 4GB RAM
- ~100MB storage per lens analysis set

## Installation

1. Clone the repository:
```bash
git clone https://github.com/evanrodgers/lens-analysis-suite.git
cd lens-analysis-suite
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Directory Structure
Organize your test images in the following structure:
```
root_directory/
├── Lens Name 1/
│   ├── lens_name_f1.4.jpg
│   ├── lens_name_f2.0.jpg
│   └── lens_name_f2.8.jpg
├── Lens Name 2/
│   └── ...
```

### Test Chart Requirements
- High-contrast geometric pattern
- Even illumination
- Camera parallel to test chart
- Chart should fill majority of frame
- Must be in perfect focus

### Running the Analysis

1. Start the application:
```bash
python main.py
```

2. Follow the interactive prompts:
   - Enter the path to your lens samples directory
   - Select analysis methods
   - Configure crop margins (0-100%)
   - Set number of horizontal sections (1-20)
   - Choose whether to generate heatmaps

### Output Structure

The application creates three main directories:

#### 1. Reports Directory (`reports/`)
- JSON analysis data
- Human-readable text reports
- Complete configuration records
- Statistical summaries

#### 2. Heatmaps Directory (`heatmaps/`)
- Color-coded visualizations
- One heatmap per analysis method
- Grid coordinates
- Score overlays
- Statistical summaries

#### 3. Working Files Directory (`working_files/`)
- Processed images
- Analysis tiles
- Grid overlays
- Intermediate files

## License

This project is licensed under the Creative Commons Attribution-NonCommercial 4.0 International License (CC BY-NC 4.0). See the [LICENSE](LICENSE) file for details.

## Support

- Create an issue in the GitHub repository

## Acknowledgments

This project uses the following open-source libraries:
- opencv-python
- numpy
- pillow
- scipy
- pandas
- matplotlib
- seaborn
- And others listed in requirements.txt

## Citation

If you use this software in your research, please cite it as:
```
Lens Analysis Suite
Evan Rodgers
Copyright (c) 2024
Licensed under CC BY-NC 4.0
https://creativecommons.org/licenses/by-nc/4.0/
```
