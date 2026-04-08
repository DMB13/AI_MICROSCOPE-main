# Deployment Guide for AI_MICROSCOPE

## Overview
This guide outlines the steps required to build and deploy the AI_MICROSCOPE application using Briefcase.

## Steps for Building and Deploying the Application

### 1. Create the Project
Run the following command to create a new project for Windows:
```bash
briefcase create windows
```

### 2. Build the Project
Once the project is created, you can build the application by running:
```bash
briefcase build windows
```

### 3. Package the Application
To package the application for distribution, use the command:
```bash
briefcase package windows --no-sign
```

### MSI Generation Process
After packaging, Briefcase will generate an MSI (Microsoft Installer) file that can be used to install the application on Windows systems. This MSI file is located in the `dist` folder of your project. Follow these steps to generate the MSI:
1. Ensure all dependencies are included in the package.
2. Proceed with the packaging command as mentioned above.
3. Locate the generated MSI in the `dist` directory.

To install the application, simply double-click the MSI file and follow the on-screen instructions. Ensure that your hospital workstations comply with any prerequisites defined during the packing phase.

## Technical Section on Dynamic Pathing Logic

When running the application in different environments (frozen vs. development), dynamic pathing is crucial for locating resources correctly. This section explains two important concepts used within the application:

### sys._MEIPASS 
- **Definition:** `sys._MEIPASS` is an attribute that is automatically created by PyInstaller when packaging a Python application. It points to the temporary directory where your application files are unpacked at runtime.
- **Usage:** Use this variable to locate data files shipped with the application in frozen mode.

### Path(__file__)
- **Definition:** `Path(__file__)` provides the path to the current script file, which can be used to determine the script's location during development.
- **Usage:** Combine this with `sys._MEIPASS` to create robust path logic that works seamlessly in both frozen and development environments.

### Example Usage
```python
import os
import sys
from pathlib import Path

if getattr(sys, 'frozen', False):  
    # On frozen mode
    base_path = sys._MEIPASS  
else:  
    # On development mode
    base_path = Path(__file__).parent  

# Use base_path to open resource files

resource_path = os.path.join(base_path, 'resources', 'data.txt')
```

This approach ensures that your application behaves consistently regardless of how it is run.