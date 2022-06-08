FROM python:3.10
LABEL maintainer="Akinola Antony Wilson <akinola.antony.wilson@gmail.com>"

# running as root == BAD PRACTICE

WORKDIR /opt

ENV GUNICORN_WORKERS=$GUNICORN_WORKERS \
    GUNICORN_TIMEOUT=$GUNICORN_TIMEOUT \
    LOGLEVEL=$LOGLEVEL

# env variable for checking whether app is running inside container (then using app.mount(...) in main.py file or not)
ENV DOCKER_ENV="DOCKER"

COPY requirements.txt ./ 
RUN python3 -m pip --no-cache-dir install --upgrade pip 
RUN python3 -m pip install -r requirements.txt
RUN rm requirements.txt 


COPY app/extractor ./

# serving html coverage report
RUN mkdir static 
COPY htmlcov static

# should be using the standard var/log location inside container
RUN mkdir log

# script for initing server
COPY start_server.sh ./
# letting server start script be executable within container
RUN chmod +x ./start_server.sh

EXPOSE 80
CMD [ "./start_server.sh" ]
