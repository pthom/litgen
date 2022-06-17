from skbuild import setup  # This line replaces 'from setuptools import setup'


# from setuptools import setup

setup(
    name="lg-imgui",
    version="0.1.0",
    author="Pascal Thomet",
    author_email="pthomet@gmail.com",
    description="lg-imgui, bindings for imgui, using litgen",
    url="https://github.com/pthom/litgen/example",
    packages=(["lg_imgui"]),
    package_dir={"": "bindings"},
    cmake_install_dir="bindings/lg_imgui",
    include_package_data=True,
    extras_require={"test": ["pytest"]},
    python_requires=">=3.6",
    package_data={"lg_imgui": ["*.pyi"]},
)
