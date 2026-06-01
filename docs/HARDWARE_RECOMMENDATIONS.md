# AI Microscope - Hardware Recommendations

## Overview

This document provides hardware recommendations for deploying the AI Microscope application in clinical environments. The system requires specific hardware configurations to ensure reliable performance for bacterial identification.

## Minimum Requirements

### System Specifications
- **Processor**: Intel Core i5 8th Gen or AMD Ryzen 5 2600 (or equivalent)
- **RAM**: 8GB DDR4
- **Storage**: 10GB free disk space (SSD recommended)
- **GPU**: Integrated graphics or dedicated GPU with 2GB VRAM
- **Operating System**: Windows 10/11 (64-bit) or Ubuntu Linux 20.04+

### Camera Requirements
- **Resolution**: Minimum 1280x720 (720p)
- **Frame Rate**: 30 FPS or higher
- **Interface**: USB 3.0 or HDMI capture card
- **Focus**: Manual focus capability for microscope mounting

### Microscope Compatibility
- **Mount**: Standard C-mount or adapter for microscope
- **Lighting**: LED illumination with adjustable intensity
- **Magnification**: 40x to 1000x objective lenses

## Recommended Configuration

### Clinical Deployment (Optimal)

#### Processor
- Intel Core i7 10th Gen or AMD Ryzen 7 3700X (or equivalent)
- 6 cores / 12 threads minimum
- Base clock: 3.0GHz or higher

#### Memory
- 16GB DDR4 3200MHz (dual channel recommended)
- 32GB DDR4 for high-throughput environments

#### GPU
- NVIDIA GeForce RTX 3060 (6GB VRAM) or equivalent
- CUDA cores: 3584 or higher
- Supports TensorFlow GPU acceleration

#### Storage
- 500GB NVMe SSD (system drive)
- 1TB HDD or SSD for data storage
- Backup storage: External HDD or cloud backup

#### Camera
- Sony IMX series or equivalent
- Resolution: 1920x1080 (1080p) or higher
- Frame Rate: 60 FPS
- USB 3.2 Gen 1 interface
- Global shutter preferred

### Microscope System
- **Type**: Brightfield compound microscope
- **Objectives**: 4x, 10x, 40x, 100x (oil immersion)
- **Eyepieces**: 10x widefield
- **Stage**: Mechanical stage with X-Y controls
- **Condenser**: Abbe condenser with iris diaphragm
- **Light Source**: LED illumination (cool white)

## Network Requirements

### Local Network
- **Bandwidth**: 100 Mbps Ethernet (wired connection recommended)
- **Latency**: <10ms to local servers

### Cloud Backup (Optional)
- **Upload Speed**: 10 Mbps minimum
- **Connection**: Stable internet connection

## Power Requirements

- **Voltage**: 110-240V AC, 50/60Hz
- **UPS**: Uninterruptible Power Supply recommended
  - Capacity: 600VA minimum
  - Runtime: 10-15 minutes for safe shutdown
- **Surge Protection**: Required for all equipment

## Environmental Conditions

### Temperature
- Operating: 15°C to 35°C (59°F to 95°F)
- Storage: -20°C to 60°C (-4°F to 140°F)

### Humidity
- Operating: 20% to 80% non-condensing
- Storage: 10% to 90% non-condensing

### Cleanliness
- Dust-free environment recommended
- Regular cleaning of microscope optics
- Air filtration in dusty environments

## Peripheral Requirements

### Display
- Resolution: 1920x1080 minimum
- Size: 24 inches or larger
- Color accuracy: sRGB or better

### Input Devices
- Keyboard and mouse
- Touch screen (optional but recommended)

### Printer
- For printing clinical reports
- Color printer recommended
- A4 paper size

## Software Requirements

### Operating System
- Windows 10/11 Pro (64-bit) with latest updates
- Ubuntu Linux 20.04 LTS or 22.04 LTS

### Dependencies
- Python 3.11.0 or higher
- TensorFlow 2.18.1 with Keras 3.x
- CUDA 12.x (for GPU acceleration, optional)
- cuDNN 8.x (for GPU acceleration, optional)

### Optional Software
- Antivirus software
- Remote desktop software
- Backup software

## Performance Benchmarks

### Inference Performance (CPU)
- Model load time: ~10-15 seconds
- First inference: ~2 seconds
- Subsequent inferences: ~0.5-1 second per image

### Inference Performance (GPU - RTX 3060)
- Model load time: ~5-8 seconds
- First inference: ~1 second
- Subsequent inferences: ~0.1-0.2 seconds per image

### System Response Time
- Camera startup: <2 seconds
- Image capture: <1 second
- Report generation: <2 seconds

## Scalability Considerations

### Single Workstation
- Recommended for small clinics
- 1-5 users
- 50-100 diagnoses per day

### Multi-Workstation Deployment
- Central server for database storage
- Network-attached storage (NAS)
- Shared backup solution
- 10-50 users
- 500-1000 diagnoses per day

### Cloud Integration
- Optional cloud backup for disaster recovery
- Remote access capabilities
- Secure VPN connection required

## Maintenance Requirements

### Daily
- Backup database
- Check camera calibration
- Verify system health

### Weekly
- Clean microscope optics
- Update virus definitions
- Check disk space

### Monthly
- System updates
- Full system backup
- Performance review

### Annually
- Professional microscope service
- Hardware assessment
- Software license review

## Cost Estimate (USD)

### Minimum Configuration
- Computer: $800-1,000
- Camera: $200-300
- Microscope: $1,500-2,500
- Peripherals: $200-300
- **Total: $2,700-4,100**
- **Note**: 8GB RAM minimum, 16GB recommended for 1.2GB model

### Recommended Configuration
- Computer: $1,500-2,000
- Camera: $500-800
- Microscope: $3,000-5,000
- Peripherals: $500-700
- UPS: $100-200
- **Total: $5,600-8,700**

## Vendor Recommendations

### Computer Hardware
- Dell, HP, Lenovo (business class)
- Custom builds from reputable system integrators

### Camera Systems
- Sony, Basler, FLIR (industrial cameras)
- AmScope, Omano (microscope cameras)

### Microscopes
- Olympus, Nikon, Zeiss (premium)
- AmScope, Motic (mid-range)
- Celestron, Swift (entry-level)

### Support and Service
- Choose vendors with local service availability
- Consider extended warranties for clinical deployment
- Verify spare parts availability

## Compliance Considerations

### Medical Device Classification
- Check local regulatory requirements
- May require medical-grade hardware certification
- Verify compliance with electrical safety standards

### Data Security
- Hardware encryption support (TPM 2.0)
- Secure boot capability
- Physical security for workstations

## Troubleshooting

### Common Issues

#### Slow Performance
- Check CPU and memory usage
- Verify GPU drivers are up to date
- Close unnecessary applications

#### Camera Connection Issues
- Check USB cable connections
- Verify camera drivers
- Try different USB port

#### Model Load Failures
- Verify sufficient RAM
- Check disk space
- Restart application

### Support Contacts
- Technical support: [contact information]
- Hardware vendor: [vendor support]
- Software vendor: [software support]

## Version History

- **v1.0** - Initial recommendations document
- **v2.1.0** - Updated for TensorFlow 2.18.1 compatibility
- Updated model size to 1.2GB (best_clinical_rugged_1777619657.keras)
- Updated RAM recommendations (8GB minimum, 16GB recommended)
- Added GPU acceleration details
