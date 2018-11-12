FROM ubuntu:latest

RUN apt-get update \
  && apt-get install -y python3-pip python3-dev \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && pip3 install --upgrade pip

RUN apt-get install -y build-essential

RUN apt-get install -y git

RUN cd opt && git clone https://github.com/gsidsid/NEAT-asteroids.git

WORKDIR "/opt/NEAT-asteroids/"

RUN cat requirements.txt | cut -f1 -d"#" | sed '/^\s*$/d' | xargs -n 1 pip install; exit 0

RUN apt-get install sudo

