#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name="tamesdk",
    version="1.0.0",
    description="Runtime control for AI agents",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "httpx>=0.24.0",
    ],
    entry_points={
        "console_scripts": [
            "tamesdk=tamesdk.cli:main",
        ],
    },
)