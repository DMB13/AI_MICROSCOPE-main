# Technical Architecture: Dynamic Pathing Logic

This document outlines the dynamic pathing logic used in the AI_MICROSCOPE application to handle both development and production environments. This is crucial for ensuring that the application can run seamlessly regardless of how it's deployed.

## Environment Handling

### Development Environment
In a development environment, the code utilizes `Path(__file__)` to resolve model paths. This is part of the standard library `pathlib` and allows the script to determine its own location, creating paths relative to the script.

**Example from `src/dmbaimicroscope/app.py`:**
```python
from pathlib import Path

# Resolve the path to the models based on the current file location
model_path = Path(__file__).parent / 'models' / 'model_file.pkl'
```

### Production Environment (Frozen MSI)
When the application is packaged as a frozen executable (e.g., using PyInstaller), it uses `sys._MEIPASS`. This attribute holds the path to the temporary folder where the bundled app and its dependencies are extracted at runtime. The application should use this to locate resources bundled within the executable.

**Example from `src/dmbaimicroscope/inference/inference.py`:**
```python
import sys
from pathlib import Path

# Check if running in a frozen environment
if getattr(sys, 'frozen', False):
    model_path = Path(sys._MEIPASS) / 'models' / 'model_file.pkl'
else:
    model_path = Path(__file__).parent / 'models' / 'model_file.pkl'
```

## Guidance for Future Maintainers
- **Preserve Path Logic:** When modifying code that loads files or models, ensure that the logic for determining the file path remains intact. Always check whether the environment is frozen or development to use the appropriate path resolution method.
- **Testing in Both Environments:** Test any changes in both development and production environments to verify that paths resolve correctly in each scenario. This can prevent runtime errors related to file loading.
- **Document Changes:** If modifications require changes to path logic, document them clearly in this file and ensure that any new paths are validated for both environments.

This dynamic pathing logic is essential for the reliability and portability of the AI_MICROSCOPE application across different deployment platforms.