#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GDB融合工具安装脚本
"""

from setuptools import setup, find_packages

setup(
    name="gdb_fusion_tool",
    version="0.1.0",
    description="GDB融合工具 - 用于融合多个GDB文件",
    author="Manus AI",
    author_email="info@example.com",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "fiona>=1.8.0",
        "geopandas>=0.10.0",
        "shapely>=1.7.0",
        "tqdm>=4.50.0",
    ],
    entry_points={
        "console_scripts": [
            "gdb-fusion=gdb_fusion_tool.src.__main__:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.6",
)

