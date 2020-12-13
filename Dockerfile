FROM docker.heinrichhartmann.net:5000/python3.8

COPY /dist /dist
RUN cd /dist; pip install *.whl

RUN mkdir -p /work
WORKDIR /work
