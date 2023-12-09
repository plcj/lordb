FROM amancevice/pandas:alpine-2.1.4

COPY . /root/lordb

WORKDIR /root/lordb

ENV PYTHONPATH "${PYTHONPATH}:/lordb"
