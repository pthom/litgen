from __future__ import annotations
from skbuild import setup  # This line replaces 'from setuptools import setup'


setup(
    name="lg-mylib",
    version="0.1.0",
    author="Pascal Thomet",
    author_email="pthomet@gmail.com",
    description="lg-mylib, integration tests python module for litgen tests",
    url="https://github.com/pthom/litgen",
    packages=(["lg_mylib"]),
    package_dir={"": "bindings"},
    cmake_install_dir="bindings/lg_mylib",
    include_package_data=True,
    extras_require={"test": ["pytest"]},
    python_requires=">=3.6",
    package_data={"lg_mylib": ["py.typed", "*.pyi"]},
    install_requires=[],
)
