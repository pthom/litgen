FROM ubuntu:22.04

RUN apt-get update

# Install required build utilities
RUN DEBIAN_FRONTEND="noninteractive" apt-get install -y build-essential git cmake python3 python3-pip python3-venv

# Install utilities
RUN apt-get install -y wget tree

# Install libsssl1.1 (required for srcML)
RUN wget http://archive.ubuntu.com/ubuntu/pool/main/o/openssl/libssl1.1_1.1.0g-2ubuntu4_amd64.deb && \
    dpkg -i libssl1.1_1.1.0g-2ubuntu4_amd64.deb

# Install srcML
RUN wget http://131.123.42.38/lmcrs/v1.0.0/srcml_1.0.0-1_ubuntu20.04.deb && \
    dpkg -i srcml_1.0.0-1_ubuntu20.04.deb

