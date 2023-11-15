#!/bin/bash

set -e

TOP_DIR=/srcml_build_docker
cd $TOP_DIR

# Install dependencies
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y build-essential git cmake
apt-get install -y libarchive-dev antlr libxml2-dev libxslt-dev libcurl4-openssl-dev

# Get recent cmake
wget https://github.com/Kitware/CMake/releases/download/v3.26.5/cmake-3.26.5-linux-x86_64.tar.gz
tar -xvf cmake-3.26.5-linux-x86_64.tar.gz

# Build srcML from source
git clone https://github.com/pthom/srcML.git -b develop_fix_build
mkdir build
cd build
$TOP_DIR/cmake-3.26.5-linux-x86_64/bin/cmake ../srcML -DCMAKE_INSTALL_PREFIX=$TOP_DIR/srcml_install
make -j 4
make install

# Make tarball of srcML install
cd $TOP_DIR/srcml_install
tar cvfz srcml_build_docker.tgz bin/ include/ lib/ share/

# Copy tarball to host
scp srcml_build_docker.tgz $1
