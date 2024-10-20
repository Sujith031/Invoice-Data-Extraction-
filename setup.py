from setuptools import find_packages, setup

setup(
    name="invoice-extraction",
    version="0.0.1",
    author="Sumanth G",
    author_email="your.email@example.com",
    description="A package for invoice data extraction",
    packages=find_packages("src"),
    package_dir={"": "src"},
    install_requires=[
        # Add required dependencies here, for example:
        "pandas>=1.0.0",
        "numpy>=1.18.0",
        "openpyxl",  # if you're dealing with Excel files
        "PyPDF2",    # if you handle PDFs
    ],
    extras_require={
        "dev": ["pytest>=5.0.0"],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
