FROM python:3.7-alpine

WORKDIR '/usr/src/oshino'

COPY oshino ./oshino
COPY requirements ./requirements
COPY tests ./tests
COPY README.md ./README.md
COPY setup.py .

COPY compose/config.yaml .


RUN python setup.py install 
RUN pip install -r ./requirements/test.txt

CMD ["/usr/local/bin/oshino", "--config=config.yaml"]
