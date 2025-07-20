#!/usr/bin/env python3

from setuptools import setup, find_packages


with open("README.md", "r", encoding='utf-8') as fh:
    long_decription = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith('#')]




setup(
    name="Shelly-CLI",
    version="0.1.0",
    author="Gibson Kemboi",
    author_email="gibsonsgibson88@gmail.com",
    description="A cli tool to make your git life just easy",
    url="https://github.com/Domains18/shelly.git",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "shelly=shelly.main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False
)