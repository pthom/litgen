## Local installation

### Step 1: install srcML


#### Precompiled version
You can download a pre-compiled version at [srcML.org](https://www.srcml.org/#download).

For example, on ubuntu 20.04:
```bash
wget http://131.123.42.38/lmcrs/v1.0.0/srcml_1.0.0-1_ubuntu20.04.deb
sudo dpkg -i srcml_1.0.0-1_ubuntu20.04.deb
```

#### Build from source
Alternatively, you can build srcML from source.

Below is an example on how to compile srcML on a debian based machine:

```bash
# install required packages
sudo apt-get install libarchive-dev antlr libxml2-dev libxslt-dev libcurl4-openssl-dev
# clone and build srcML, using a fork that fixes some build issues
git clone https://github.com/pthom/srcML.git -b develop_fix_build
mkdir -p build && cd build
cmake ../srcML && make -j
sudo make install
```

Below is an example on how to compile srcML on a macOS:
```bash
# install required packages
brew install antlr2 boost

# clone and build srcML, using a fork that fixes some build issues
git clone https://github.com/pthom/srcML.git -b develop_fix_build
mkdir -p build && cd build
cmake ../srcML && make -j
sudo make install
```

_Note: The [build instructions](https://github.com/srcML/srcML/blob/master/BUILD.md) in srcML repository are a bit out of date, which is why these instructions are provided here._

### Step 2: install srcmlcpp

#### Install from source
An installation from source is the recommended way:

```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate
# Install srcmlcpp
git clone git@github.com:pthom/srcmlcpp.git
cd srcmlcpp
pip install -v -e .
```

#### Install without checking out the code
Alternatively, you can install srcmlcpp without checking its code out:
```bash
pip install "srcmlcpp @ git+https://github.com/pthom/srcmlcpp"
```
