FROM python:3.7-alpine

VOLUME ['/usr/src/oshino']

WORKDIR '/usr/src/oshino'

COPY setup.py .

COPY compose/config.yaml .

RUN python setup.py install

CMD ['oshino-admin', 'start']
