# Lens Analysis Suite
## Comprehensive Product Specification

### Overview
The Lens Analysis Suite is a Python-based tool for analyzing lens sharpness characteristics across the image frame. It processes test chart images to generate quantitative measurements and visual representations of lens performance.

### Core Purpose
- Provide objective measurements of lens sharpness across the image frame
- Enable comparison between different lenses
- Document lens performance at various apertures
- Generate standardized analysis reports and visualizations

### Target Users
- Lens reviewers and testing facilities
- Photography equipment manufacturers
- Professional photographers
- Camera/lens rental companies
- Photography enthusiasts

### Input Requirements

#### Test Chart Requirements
- High-contrast geometric pattern with consistent detail across frame
- Even illumination
- Camera must be perfectly parallel to test chart
- Chart must fill majority of frame
- Chart must be perfectly in focus

#### Image Requirements
- File format: JPEG
- Minimum resolution: 1000x1000 pixels
- Recommended: 24MP or higher
- Must be properly exposed (no clipping)

#### Directory Structure
```
root_directory/
├── Lens Name 1/
│   ├── lens_name_f1.4.jpg
│   ├── lens_name_f2.0.jpg
│   └── lens_name_f2.8.jpg
├── Lens Name 2/
│   └── ...
├── reports/
├── working_files/
└── heatmaps/
```

#### Naming Convention
- Lens folders: Descriptive name (e.g., "Canon FD 24mm F2.8")
- Image files: Must end with aperture value (e.g., "lens_name_f2.8.jpg")

### Analysis Methods

#### 1. Laplacian Variance Method
- Measures local contrast and edge definition
- Most sensitive to fine detail
- Default analysis method
- Score range: 1-100 normalized

#### 2. Sobel Gradient Method
- Analyzes intensity changes in horizontal and vertical directions
- Better for high-noise images
- Score range: 1-100 normalized

#### 3. Tenengrad Algorithm
- Thresholded gradient analysis
- Most noise-resistant
- Score range: 1-100 normalized

### Configuration Options

#### Image Cropping
- Independent top, bottom, left, and right margins
- Range: 0-100% for each edge
- Used to exclude test chart edges or unwanted artifacts

#### Grid Analysis
- Horizontal sections: 1-20 user-configurable
- Vertical sections: Automatically calculated based on aspect ratio
- Grid coordinates: 
  - Letters (A,B,C...) for vertical position
  - Numbers (1,2,3...) for horizontal position
  - A1 is top-left, extends to bottom-right (e.g., F10)

### Output Structure

#### 1. Working Files Directory
Location: `working_files/<lens_name>/`
- Cropped source image
- Overview image with grid overlay
- Individual analysis tiles
- Each tile includes:
  - Coordinate label (e.g., "A1")
  - Analysis scores overlay
  - Timestamp

#### 2. Reports Directory
Location: `reports/<lens_name>/`
- JSON analysis report
  - Complete configuration settings
  - Scores for each grid position
  - Statistical summaries
  - Timestamps and filenames
- Human-readable text report
  - Detailed analysis explanation
  - Configuration summary
  - Results by grid position

#### 3. Heatmaps Directory
Location: `heatmaps/<lens_name>/`
- One heatmap per analysis method
- Features:
  - 3:2 aspect ratio
  - Color-coded score representation
  - Grid coordinates (letters on Y-axis, numbers on X-axis)
  - Numerical score overlay
  - Statistical summary
  - Original filename overlay
  - Score colorbar
  - Proper axis labels

### User Interface

#### Command Line Interface
1. Initial Setup
```
Please enter the path to your lens samples directory:
```

2. Analysis Method Selection
```
Available analysis methods:
1: Laplacian method - default, most sensitive
2: Sobel method - use only for high-noise images
3: Tenengrad - use only for high-noise images
4: All methods

Select analysis methods (press Enter for default [Laplacian],
or enter comma-separated numbers, e.g. '1,2' or '4' for all):
```

3. Crop Configuration
```
Enter top margin crop percentage (0-100):
Enter bottom margin crop percentage (0-100):
Enter left margin crop percentage (0-100):
Enter right margin crop percentage (0-100):
```

4. Grid Configuration
```
Enter number of horizontal sections (1-20):
```

5. Output Configuration
```
Would you like to generate heatmap visualizations? [Y/n]:
```

### Processing Features

#### Grid Analysis
- Uniform tile sizing
- Maintains aspect ratio
- Includes coordinate overlays
- Preserves spatial relationships

#### Error Handling
- Validates input images
- Checks directory permissions
- Validates configuration values
- Provides clear error messages

### Performance Requirements

#### Processing Time
- < 20 seconds per 24MP image
- Batch processing support
- Progress reporting

#### Resource Usage
- Memory: < 2GB RAM
- Storage: ~100MB per lens analysis set
- CPU: Maximum 2 cores

### Quality Assurance

#### Input Validation
- Image format checking
- Resolution verification
- Configuration bounds checking
- Directory permission verification

#### Output Validation
- Score normalization verification
- Grid calculation accuracy
- File integrity checks
- Report completeness verification

### Logging

#### File Location
- Root directory: lens_analysis.log

#### Log Levels
- DEBUG: Detailed processing information
- INFO: Progress and completion status
- WARNING: Non-critical issues
- ERROR: Critical failures

#### Content
- Timestamps
- Process status
- Error details
- File operations

### Dependencies
```
Pillow>=10.0.0
opencv-python>=4.8.0
numpy>=1.24.0
scipy>=1.11.0
matplotlib>=3.7.0
seaborn>=0.12.0
```

### Installation Requirements
- Python 3.8 or higher
- Virtual environment recommended
- Dependencies installed via pip
- Write permissions in working directory

### Recommended Usage

1. **Setup**
   - Create dedicated directory for lens samples
   - Organize images by lens
   - Use consistent naming convention

2. **Analysis**
   - Start with default Laplacian method
   - Use 5-10 horizontal sections
   - Apply minimal cropping initially
   - Generate heatmaps for visualization

3. **Interpretation**
   - Higher scores indicate better sharpness
   - Compare center vs. corner performance
   - Look for symmetry in results
   - Consider multiple apertures

### Future Enhancement Considerations

1. **Analysis Methods**
   - MTF (Modulation Transfer Function)
   - Chromatic aberration detection
   - Distortion measurement
   - Focus uniformity analysis

2. **User Interface**
   - Graphical interface
   - Batch configuration
   - Real-time preview
   - Interactive visualization

3. **Output Options**
   - PDF report generation
   - CSV export
   - Comparative analysis
   - Trend tracking

4. **Integration**
   - API development
   - Database storage
   - Cloud backup
   - Photography tool integration
