from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="invoice-extraction",
    version="0.0.1",
    author="G Sujith Goud",
    author_email="bs20b017@smail.iitm.ac.in",
    description="A package for invoice data extraction",
    packages=find_packages("src"),
    package_dir={"": "src"},
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
