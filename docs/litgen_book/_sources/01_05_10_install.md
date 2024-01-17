# Install litgen

## Step 1: install srcML

### Either install srcML from pre-compiled binaries
You can download a pre-compiled version at [srcML.org](https://www.srcml.org/#download)

For example, on ubuntu 20.04:

```bash
wget http://131.123.42.38/lmcrs/v1.0.0/srcml_1.0.0-1_ubuntu20.04.deb
sudo dpkg -i srcml_1.0.0-1_ubuntu20.04.deb
```

### Or build srcML from source

_Note: the build instructions in srcML repository are a bit out of date, which is why these instructions are provided here. It uses a fork of srcML that fixes some compilation issues on the develop branch_

__Install required packages__

On ubuntu:
```bash
sudo apt-get install libarchive-dev antlr libxml2-dev libxslt-dev libcurl4-openssl-dev
````

On macOS:
```bash
brew install antlr2 boost
```

__Clone, build and install srcML__
```bash
git clone https://github.com/pthom/srcML.git -b develop_fix_build
mkdir -p build && cd build
cmake ../srcML && make -j
sudo make install
```

## Step 2: install litgen

```bash
pip install "litgen@git+https://github.com/pthom/litgen"```
```
