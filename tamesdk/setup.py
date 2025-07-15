"""
Setup script for TameSDK.

This file provides backward compatibility for older build systems.
The main configuration is in pyproject.toml.
"""

from setuptools import setup, find_packages

if __name__ == "__main__":
    setup(
        name="tamesdk",
        version="1.0.0",
        packages=find_packages(),
        python_requires=">=3.8",
        install_requires=[
            "httpx>=0.24.0",
            "pyyaml>=6.0",
        ],
    )