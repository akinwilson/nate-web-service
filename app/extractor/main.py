#!/usr/bin python
import os
import sys
import uvicorn
import logging
from fastapi import FastAPI, Request
from fastapi.logger import logger as fastapi_logger
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from starlette.responses import RedirectResponse

# Relative path import hell! code bellow ensures that when within docker container, imports are still found
# I have fought and fought with relative path imports, and the always end up winning and I have to use
# annoying code like this to make sure everything is importable.
try:
    from vocabConstructor import Retriever, TextProcessor
    from exception_handler import python_exception_handler, validation_exception_handler
    from schema import EndpointResponse, EndpointError, EndpointInput
except ModuleNotFoundError:
    dir = os.path.dirname(os.path.realpath(__file__))
    if dir not in sys.path:
        sys.path.append(dir)
    from vocabConstructor import Retriever, TextProcessor
    from exception_handler import python_exception_handler, validation_exception_handler
    from schema import EndpointResponse, EndpointError, EndpointInput

gunicorn_error_logger = logging.getLogger("gunicorn.error")
gunicorn_logger = logging.getLogger("gunicorn")
uvicorn_access_logger = logging.getLogger("uvicorn.access")
uvicorn_access_logger.handlers = gunicorn_error_logger.handlers

fastapi_logger.handlers = gunicorn_error_logger.handlers


desc = """
API for construction a vocabulary from a webpages text content,returning dictionary with keys of words and values of occurences
"""
app = FastAPI(title="Webpage vocab constructor", description=desc)

app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, python_exception_handler)

if __name__ != "__main__":
    fastapi_logger.setLevel(gunicorn_logger.level)
else:
    fastapi_logger.setLevel(logging.DEBUG)

if os.environ.get("DOCKER_ENV") is not None:
    # only mount when where are inside a docker file

    # mounted coverage report of code tests inside fastapi
    app.mount(
        "/report",
        StaticFiles(directory="/opt/static/", html=True),
        name="test-report-ui",
    )
    # if one visit the root path, you will find the coverage report of the code, along with the code itself
    # ***NOTE** THIS IS CLEARLY A SECURITY CONCERN -> including the coverage report in the root path of the API
    # SINCE YOU ARE ABLE TO SEE THE SOURCE CODE THROUGH IT
    # I AM ONLY DOING THIS FOR THE SAKE THAT IT CAN BE DONE. I WOULD NOT RECOMMEND DOING THIS IN PRODUCTION!!!
    @app.get("/report")
    async def read_report_index():

        return RedirectResponse(url="/report/index.html")


@app.post(
    "/api/extract",
    response_model=EndpointResponse,
    responses={422: {"model": EndpointError}, 500: {"model": EndpointError}},
)
def extract_vocab(request: Request, body: EndpointInput):
    fastapi_logger.info("API extract called")
    fastapi_logger.info(f"Input: {body}")

    url = body.url
    sort_type = body.sort_type or None

    retreiver = Retriever(url=url)
    text = retreiver()
    text_processor = TextProcessor(text=text, sort_type=sort_type)
    vocab = text_processor()
    fastapi_logger.info(f"Constructed vocab: {vocab}")
    result = {"url": url, "sort_type": sort_type, "vocab": vocab}
    return {"error": False, "result": result}


@app.get("/api/health")
def health_check():
    return {"status_code": 200}


if __name__ == "__main__":

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        debug=True,
        log_config="/opt/logging.conf",
    )
