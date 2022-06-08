#!/bin/sh 
gunicorn --workers ${GUNICORN_WORKERS}  --bind :8080 --timeout ${GUNICORN_TIMEOUT} --worker-class uvicorn.workers.UvicornWorker  main:app