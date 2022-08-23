FROM docker.heinrichhartmann.net/pyenv3.8

COPY /dist /dist
RUN cd /dist; pip install *.whl

RUN mkdir -p /pile
WORKDIR /pile

EXPOSE 8080
