# Dependencies

This project requires the following Python packages:

```
streamlit
opencv-python
numpy
pandas
matplotlib
plotly
fpdf
```

## Installation

Install the required dependencies using pip:

```bash
pip install streamlit opencv-python numpy pandas matplotlib plotly fpdf
```

For development, you can install these packages with specific versions:

```bash
pip install streamlit==1.31.0 opencv-python==4.8.1.78 numpy==1.26.3 pandas==2.1.4 matplotlib==3.8.2 plotly==5.18.0 fpdf==1.7.2
```

## Virtual Environment (Recommended)

It's recommended to use a virtual environment for development:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```