# Lens Analysis Suite
## Engineering Implementation Brief

### Core Analysis Algorithms

#### 1. Laplacian Variance Method
```python
def laplacian_variance(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    raw_score = laplacian.var()
    return normalize_score(raw_score, 0, 500)
```
- Converts image to grayscale for intensity analysis
- Uses Laplacian operator to detect edges and rapid intensity changes
- Calculates variance of Laplacian to measure overall sharpness
- Normalizes between 1-100 using predetermined range (0-500)
- Higher values indicate more defined edges and better sharpness

#### 2. Sobel Gradient Method
```python
def sobel_gradient(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    raw_score = np.sqrt(sobelx ** 2 + sobely ** 2).mean()
    return normalize_score(raw_score, 0, 50)
```
- Calculates intensity gradients in x and y directions
- Uses 3x3 Sobel operator for gradient detection
- Combines gradients using Pythagorean theorem
- Takes mean of combined gradient magnitudes
- Normalizes between 1-100 using predetermined range (0-50)

#### 3. Tenengrad Algorithm
```python
def tenengrad(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    tenengrad = np.sqrt(sobelx ** 2 + sobely ** 2)
    threshold = 0.1 * tenengrad.max()
    raw_score = np.mean(tenengrad[tenengrad > threshold])
    return normalize_score(raw_score, 0, 100)
```
- Similar to Sobel but with thresholding to reduce noise
- Threshold set at 10% of maximum gradient value
- Only considers gradients above threshold in final score
- More resistant to image noise than basic Sobel
- Normalizes between 1-100 using predetermined range (0-100)

### Image Processing Pipeline

#### 1. Grid Analysis Implementation
```python
def process_tiles(image, config):
    h, w = image.shape[:2]
    aspect_ratio = w / h
    vertical_sections = max(1, int(config.horizontal_sections / aspect_ratio))
    
    tile_w = w // config.horizontal_sections
    tile_h = h // vertical_sections
    
    tiles_data = []
    for i in range(vertical_sections):
        for j in range(config.horizontal_sections):
            tile = image[i*tile_h:(i+1)*tile_h, j*tile_w:(j+1)*tile_w]
            coord = f"{chr(65 + i)}{j + 1}"
            scores = analyze_tile(tile)
            tiles_data.append({
                "coordinate": coord,
                "scores": scores
            })
    
    return tiles_data
```
- Calculates vertical sections based on aspect ratio
- Divides image into uniform tiles
- Generates A1, A2, B1, B2 style coordinates
- Processes each tile independently
- Maintains spatial relationship data

### Data Structures

#### 1. Analysis Configuration
```python
@dataclass
class AnalysisConfig:
    crop_top: float = 0.0
    crop_bottom: float = 0.0
    crop_left: float = 0.0
    crop_right: float = 0.0
    horizontal_sections: int = 5
    analysis_methods: List[str] = None

    def __post_init__(self):
        if self.analysis_methods is None:
            self.analysis_methods = ["laplacian", "sobel", "tenengrad"]
        
        if not 1 <= self.horizontal_sections <= 20:
            raise ValueError("Horizontal sections must be between 1 and 20")
        
        for crop in [self.crop_top, self.crop_bottom, 
                    self.crop_left, self.crop_right]:
            if not 0 <= crop <= 100:
                raise ValueError("Crop values must be between 0 and 100")
            
        # Convert percentage to decimal
        self.crop_top /= 100
        self.crop_bottom /= 100
        self.crop_left /= 100
        self.crop_right /= 100
```
- Uses dataclass for automatic initialization and validation
- Provides defaults for all parameters
- Implements validation in post_init
- Handles crop percentage conversion

#### 2. Analysis Results JSON Structure
```json
{
    "original_filename": "lens_name_f4.jpg",
    "timestamp": "20241204110003",
    "configuration": {
        "crop_top": 0.0,
        "crop_bottom": 0.0,
        "crop_left": 0.0,
        "crop_right": 0.0,
        "horizontal_sections": 10,
        "analysis_methods": ["laplacian"]
    },
    "tiles": [
        {
            "coordinate": "A1",
            "filename": "lens_name_A1_20241204110003.jpg",
            "scores": {
                "laplacian": 85.4
            }
        }
    ],
    "average_scores": {
        "laplacian": 82.7
    }
}
```
- Complete record of analysis parameters
- Preserves timestamps for tracking
- Maintains spatial relationships
- Includes both individual and average scores
- References associated image files

### Visualization Implementation

#### 1. Heatmap Generation
```python
def plot_heatmap(grid, metric, letters, numbers, output_path, title=None):
    base_width = 12
    fig_width = base_width
    fig_height = (base_width * 2) / 3
    
    plt.figure(figsize=(fig_width, fig_height))
    
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
    
    if title is None:
        title = f'Lens Sharpness Analysis - {metric.capitalize()}'
    plt.title(title, pad=20)
    
    plt.xlabel('Horizontal Position (Left to Right)', labelpad=10)
    plt.ylabel('Vertical Position (Center to Edge)', labelpad=10)
    
    plt.xticks(rotation=0)
    plt.yticks(rotation=0)
    
    stats_text = (f'Min: {grid.min():.1f}  Max: {grid.max():.1f}  '
                 f'Mean: {grid.mean():.1f}')
    plt.figtext(0.99, 0.01, stats_text, ha='right', va='bottom', fontsize=8)
    
    filename = output_path.stem.replace(f"_{metric}_heatmap", "")
    plt.figtext(0.01, 0.01, filename, ha='left', va='bottom', fontsize=8)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
```
- Uses seaborn for enhanced heatmap visualization
- Maintains 3:2 aspect ratio
- Numbers on x-axis, letters on y-axis
- Includes numerical annotations
- Adds filename and statistical summary
- High DPI output for publication quality

### Directory Structure Management

#### 1. Directory Creation
```python
def setup_directory_structure(root_dir):
    reports_dir = root_dir / "reports"
    heatmaps_dir = root_dir / "heatmaps"
    working_files_dir = root_dir / "working_files"
    
    reports_dir.mkdir(exist_ok=True)
    heatmaps_dir.mkdir(exist_ok=True)
    working_files_dir.mkdir(exist_ok=True)
    
    return reports_dir, heatmaps_dir, working_files_dir

def setup_lens_directories(lens_name, reports_dir, heatmaps_dir, working_files_dir):
    lens_reports_dir = reports_dir / lens_name
    lens_heatmaps_dir = heatmaps_dir / lens_name
    lens_working_dir = working_files_dir / lens_name
    
    lens_reports_dir.mkdir(exist_ok=True)
    lens_heatmaps_dir.mkdir(exist_ok=True)
    lens_working_dir.mkdir(exist_ok=True)
    (lens_working_dir / "tiles").mkdir(exist_ok=True)
    
    return lens_reports_dir, lens_heatmaps_dir, lens_working_dir
```
- Uses pathlib for cross-platform compatibility
- Creates directories only when needed
- Maintains consistent structure
- Handles existing directories gracefully

### Logging Implementation

```python
def setup_logging(log_file):
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s')
    
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
```
- Dual output to file and console
- Different verbosity levels for each output
- Consistent timestamp formatting
- Hierarchical logging levels

### Error Handling Strategy

```python
def process_image(self, image_path, output_dir):
    try:
        image = cv2.imread(str(image_path))
        if image is None:
            logging.error(f"Failed to read image: {image_path}")
            return

        logging.debug(f"Processing image: {image_path}")
        
        cropped = self._crop_image(image)
        
        # Process and save outputs...
        
    except Exception as e:
        logging.error(f"Error processing {image_path}: {str(e)}")
        raise
```
- Hierarchical error handling
- Detailed error logging
- Graceful failure modes
- Error propagation when appropriate

### Performance Considerations

1. **Memory Management**
   - Process images in tiles to reduce memory footprint
   - Clear matplotlib figures after saving
   - Use uint8 image type where possible
   - Implement garbage collection for large batch processes

2. **Processing Optimization**
   - Use NumPy vectorized operations
   - Minimize image format conversions
   - Reuse allocated arrays where possible

3. **I/O Efficiency**
   - Batch file operations
   - Use binary formats for intermediate data
   - Implement proper file closing
   - Buffer writes for log files

### File Dependencies
```
visualization.py  - Heatmap generation and visualization
image_processor.py - Core image processing and analysis
sharpness_analyzer.py - Analysis algorithms implementation
reporting.py - Report generation and formatting
main.py - User interface and program orchestration
```

This engineering brief provides the technical implementation details that complement the product specification. It focuses on the actual algorithms, data structures, and coding patterns used in the application.
