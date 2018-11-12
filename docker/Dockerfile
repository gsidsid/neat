FROM ubuntu:latest

RUN apt-get update \
  && apt-get install -y python3-pip python3-dev \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && pip3 install --upgrade pip

RUN apt-get install -y build-essential

RUN apt-get install -y git

RUN cd opt && git clone https://github.com/gsidsid/NEAT-asteroids.git

WORKDIR "/opt"

RUN cat requirements.txt | xargs -n 1 pip install

