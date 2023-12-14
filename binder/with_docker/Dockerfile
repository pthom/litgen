# See doc at https://mybinder.readthedocs.io/en/latest/examples/sample_repos.html#dockerfile-environments

FROM --platform=linux/amd64 jupyter/base-notebook

#
# Initial build of srcML: this was used to create the tgz that is downloaded in the next step
#
#USER root
#RUN mkdir /srcml_build_docker
#COPY srcml_build_docker.sh /srcml_build_docker/srcml_build_docker.sh
#RUN chmod +x /srcml_build_docker/srcml_build_docker.sh
# RUN /srcml_build/build_srcml.sh

#
# Download precompiled srcML
#
USER root
# install dependencies
RUN apt-get update
RUN apt-get install -y libarchive-dev libxml2-dev libxslt-dev libcurl4-openssl-dev
# download srcML and extract to /usr
RUN wget https://traineq.org/SrcmlCpp/srcml_build_docker_amd64_20231115.tgz
RUN cd /usr && tar xvfz /home/jovyan/srcml_build_docker_amd64_20231115.tgz
RUN rm /home/jovyan/srcml_build_docker_amd64_20231115.tgz

# install git
USER root
RUN apt-get install -y git

# cleanup
RUN rm -rf /var/lib/apt/lists/*

#
# Clone & install srcmlcpp
#
USER jovyan
RUN git clone https://github.com/pthom/litgen.git
RUN cd srcmlcpp && pip install -v -e .


USER jovyan
WORKDIR /home/jovyan/srcmlcpp

# Remove this!
# USER root
