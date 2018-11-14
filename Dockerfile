FROM ubuntu:latest

RUN apt-get update \
	&& apt-get install -y python3-pip python3-dev \
	&& cd /usr/local/bin \
	&& ln -s /usr/bin/python3 python \
        && pip3 install --upgrade pip

RUN apt-get install -y build-essential
RUN apt-get install -y git
RUN apt-get install sudo

WORKDIR "/opt/"

RUN git clone https://github.com/gsidsid/NEAT-asteroids .
RUN cat requirements.txt | cut -f1 -d"#" | sed '/^\s*$/d' | xargs -n 1 pip install; exit 0

WORKDIR "/opt/setup"

# Extraction tools
RUN sudo apt-get install wget
RUN wget http://heasarc.gsfc.nasa.gov/FTP/software/fitsio/c/cfitsio_latest.tar.gz
RUN tar -xvf cfitsio_latest.tar.gz
RUN cd cfitsio && sudo ./configure && sudo make && sudo make funpack && cp ./funpack ../../

# Analysis tools
RUN git clone https://github.com/astropy/astropy
RUN cd astropy && python setup.py install

# Execution tools
RUN wget https://www.astromatic.net/download/sextractor/sextractor-2.19.5-1.x86_64.rpm
RUN sudo apt-get install alien -y
RUN sudo alien -i sextractor-2.19.5-1.x86_64.rpm
RUN git clone git://github.com/astropy/ccdproc.git
RUN cd ccdproc && python setup.py build && python setup.py install

WORKDIR "/opt/"
RUN mkdir sexout
RUN chmod u+x f.sh

ADD . .