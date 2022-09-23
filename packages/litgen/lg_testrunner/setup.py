from skbuild import setup  # This line replaces 'from setuptools import setup'

setup(
    name="testrunner",
    version="0.1.0",
    author="Pascal Thomet",
    author_email="pthomet@gmail.com",
    description="testrunner, integration tests python module for litgen tests",
    url="https://github.com/pthom/litgen",
    packages=(["testrunner"]),
    package_dir={"": "bindings"},
    cmake_install_dir="bindings/testrunner",
    include_package_data=True,
    extras_require={"test": ["pytest"]},
    python_requires=">=3.6",
    package_data={"testrunner": ["*.pyi"]},
    install_requires=[],
)
