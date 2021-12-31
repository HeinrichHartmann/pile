FROM docker.heinrichhartmann.net/pyenv3.8

COPY /dist /dist
RUN cd /dist; pip install *.whl

RUN mkdir -p /work
WORKDIR /work

EXPOSE 8080
