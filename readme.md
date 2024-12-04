# Lens Analysis Suite

A Python-based tool for quantitative analysis of lens sharpness characteristics across the image frame. This application helps photographers, reviewers, and manufacturers evaluate lens performance through automated analysis of test chart images.

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
git clone https://github.com/yourusername/lens-analysis.git
cd lens-analysis
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

## Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) for details on how to submit pull requests, report issues, and contribute to the project.

## Support

- Create an issue in the GitHub repository
- Email: support@example.com
- Documentation: [Wiki](https://github.com/yourusername/lens-analysis/wiki)

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
Copyright (c) 2024
Licensed under CC BY-NC 4.0
https://creativecommons.org/licenses/by-nc/4.0/
```
