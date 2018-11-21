FROM python:3.7-alpine

WORKDIR '/usr/src/oshino'

COPY oshino ./oshino
COPY requirements ./requirements
COPY README.md ./README.md
COPY setup.py .

COPY compose/config.yaml .

RUN python setup.py install

CMD ["/usr/local/bin/oshino", "--config=config.yaml"]
