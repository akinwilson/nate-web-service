#!/bin/sh 
set -x 
echo "Running pytest in order to produce HTML test coverage report."
echo "Report will be mounted as static file with fastAPI and visible via the endpoint 0.0.0.0:8080/report"
echo "Take note of the security implications of mounted the report like this! Code is visible!"
echo ""
echo "Running pytest ..."
pytest
echo ""
echo "Building docker image..."
echo ""
docker build . -t nate-web-server:latest

echo "Finished"

