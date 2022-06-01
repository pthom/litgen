#!/bin/bash

# wget http://archive.ubuntu.com/ubuntu/pool/main/o/openssl/libssl1.1_1.1.0g-2ubuntu4_amd64.deb
# dpkg -i libssl1.1_1.1.0g-2ubuntu4_amd64.deb


# If you get an error that says "Package libssl1.1 is not installed", run the install of libssl that is commented
# on top of this file
wget http://131.123.42.38/lmcrs/v1.0.0/srcml_1.0.0-1_ubuntu20.04.deb -O /tmp/srcmlcpp.deb
sudo dpkg -i /tmp/srcmlcpp.deb

