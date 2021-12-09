FROM ubuntu:20.04 AS buildenv

COPY requirements.txt /requirements.txt
RUN apt-get update && \
    apt-get install --yes --no-install-recommends \
    make g++ python3.8 python3.8-dev python3-virtualenv
RUN virtualenv /venv
RUN /bin/sh /venv/bin/activate && \
    /venv/bin/pip install -r /requirements.txt

FROM ubuntu:20.04

RUN apt-get update && \
    apt-get install --yes python3.8 libpython3.8 && \
    useradd -d /work -s /bin/false worker
COPY main.py /work/main.py
COPY --from=buildenv /venv /venv
USER worker
WORKDIR /work

EXPOSE  8080
ENTRYPOINT ["/venv/bin/uwsgi"]
CMD ["--http", ":8080", "--virtualenv", "/venv", "--wsgi-file", "/work/main.py", "--callable", "uwsgi_entrypoint", "--processes", "4"]
