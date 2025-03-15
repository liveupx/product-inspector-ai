# Product Inspector AI

![Product Inspector AI Demo](preview.webp)

## Overview

Product Inspector AI is an open-source quality inspection system designed for production lines and manufacturing environments. Built with Streamlit and OpenCV, this application provides real-time product quality assessment, defect detection, and comprehensive reporting capabilities.

## Features

- **Real-time Quality Inspection**: Detect and analyze products on production lines using computer vision
- **Defect Recognition**: Identify product defects with customizable detection thresholds
- **Product Management**: Add, edit, and manage product information and inspection criteria
- **Batch Processing**: Organize inspections by batches for better traceability
- **Comprehensive Reporting**: Generate PDF and Excel reports with quality statistics
- **Interactive Dashboard**: View inspection metrics and performance analytics
- **Customizable Settings**: Adjust detection parameters to your specific requirements

## Installation

```bash
# Clone the repository
git clone https://github.com/liveupx/product-inspector-ai.git
cd product-inspector-ai

# Install required dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

## System Requirements

- Python 3.7+
- OpenCV
- Streamlit
- Pandas
- Matplotlib
- Plotly
- FPDF

## Usage

### Main Inspection Screen

The main screen provides a live view of the inspection process:

1. Configure product information in the sidebar
2. Adjust detection thresholds as needed
3. Click "Start Inspection" to begin the quality assessment
4. View real-time statistics of processed products

### Product Setup

Use the Product Setup page to:

1. Add new products with detailed information
2. Configure inspection criteria (Standard, Strict, or Permissive)
3. Manage existing products and their parameters

### Dashboard

The dashboard provides analytical insights:

1. View overall inspection statistics
2. Analyze quality distribution and trends
3. Compare performance across different batches
4. Filter data by date ranges

### Reports

Generate and export detailed reports:

1. Create PDF reports with graphs and statistics
2. Export Excel spreadsheets with raw inspection data
3. Filter reports by time period or batch number

## Camera Integration

The system supports multiple camera sources:

- Local webcams
- IP cameras
- Video files (for testing)
- Demo mode with simulated products

## Extending the System

### Custom Detection Models

You can integrate your own machine learning models by:

1. Implementing the model in the `ProductDetector` class
2. Adjusting the detection threshold based on your model's characteristics
3. Customizing the visualization of detection results

### Additional Features

The modular architecture allows for easy extensions:

- Add new quality metrics
- Implement different types of defect detection
- Connect to databases for persistent storage
- Integrate with production line control systems

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenCV for the computer vision capabilities
- Streamlit for the interactive web interface
- The open-source community for various libraries used in this project

## Contact

LiveupX - [@liveupx](https://github.com/liveupx)

Project Link: [https://github.com/liveupx/product-inspector-ai](https://github.com/liveupx/product-inspector-ai)