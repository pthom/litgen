FROM ubuntu:22.04

RUN apt-get update

# Install required build utilities
RUN DEBIAN_FRONTEND="noninteractive" apt-get install -y build-essential git cmake python3 python3-pip python3-venv wget tree

# install_x11vnc
# /start_x_vnc.sh will start a "X server + vnc server + window manager" accessible via VNC
# -> you can connect to it via VNC on the port 5900 of the localhost
RUN DEBIAN_FRONTEND="noninteractive"  apt-get install -y x11vnc xvfb icewm
RUN mkdir ~/.vnc &&\
    x11vnc -storepasswd xxx ~/.vnc/passwd &&\
    echo 'export DISPLAY=:0' >> ~/.bashrc &&\
    echo "Xvfb -screen 0 1280x1024x16 & sleep 1 && icewm & x11vnc -forever  -ncache 10" > /start_x_vnc.sh &&\
    chmod +x /start_x_vnc.sh && \
    apt-get install -y libglapi-mesa

# Install libs required by immvision
RUN apt-get install -y libopencv-dev libsdl2-dev libgl1-mesa-dev

# Install pipewire (PipeWire multimedia server), required by sdl
RUN apt-get install -y pipewire


# Install libsssl1.1 (required for srcML)
#RUN wget http://archive.ubuntu.com/ubuntu/pool/main/o/openssl/libssl1.1_1.1.0g-2ubuntu4_amd64.deb && \
#    dpkg -i libssl1.1_1.1.0g-2ubuntu4_amd64.deb \
# For Arm based OSes (M1 for example)
#RUN wget http://archive.ubuntu.com/ubuntu/pool/main/o/openssl/libssl1.1_1.1.0g-2ubuntu4_arm64.deb && \
#    dpkg -i libssl1.1_1.1.0g-2ubuntu4_arm64.deb


# Install srcML via dpkg (For Intel Hosts)
#RUN wget http://131.123.42.38/lmcrs/v1.0.0/srcml_1.0.0-1_ubuntu20.04.deb && \
#    dpkg -i srcml_1.0.0-1_ubuntu20.04.deb

# Install srcML via manual compil (needed for ARM Hosts, such ac Mac M1)
RUN apt-get update && apt-get install --no-install-recommends -y \
    curl \
    zip \
    g++ \
    make \
    ninja-build \
    antlr \
    libantlr-dev \
    libxml2-dev \
    libxml2-utils \
    libxslt1-dev \
    libarchive-dev \
    libssl-dev \
    libcurl4-openssl-dev \
    cpio \
    man \
    file \
    dpkg-dev \
    libboost-all-dev
RUN git clone https://github.com/srcML/srcML.git
# Need to patch and add `include <algorithm>`, see https://github.com/srcML/srcML/pull/1829
RUN sed -i '1s/^/#include <algorithm>\n/' /srcML/src/parser/UTF8CharBuffer.cpp
RUN cd srcML && mkdir build && cd build && cmake .. && make -j 4 && cp bin/srcml /usr/local/bin/

# RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-aarch64.sh # Warning, ARM version

# Install poetry
RUN pip install poetry
