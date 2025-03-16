from setuptools import setup, find_packages

setup(
    name="product-inspector-ai",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "streamlit",
        "opencv-python",
        "numpy",
        "pandas",
        "matplotlib",
        "plotly",
        "fpdf",
    ],
    author="LiveupX",
    author_email="contact@example.com",
    description="Product quality inspection system with computer vision",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/liveupx/product-inspector-ai",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)