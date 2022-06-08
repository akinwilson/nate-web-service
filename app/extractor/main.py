#!/usr/bin python

import os 
import sys 

import uvicorn 
import logging 




from vocabConstructor import Retriever, TextProcessor

from fastapi import FastAPI, Request
from fastapi.logger import logger  as fastapi_logger
from fastapi.exceptions import RequestValidationError
from exception_handler import python_exception_handler, validation_exception_handler


from schema import * 


gunicorn_error_logger = logging.getLogger("gunicorn.error")
gunicorn_logger = logging.getLogger("gunicorn")
uvicorn_access_logger = logging.getLogger("uvicorn.access")
uvicorn_access_logger.handlers = gunicorn_error_logger.handlers

fastapi_logger.handlers = gunicorn_error_logger.handlers


if __name__ != "__main__":
    fastapi_logger.setLevel(gunicorn_logger.level)
else:
    fastapi_logger.setLevel(logging.DEBUG)


app = FastAPI(title="Webpage vocab constructor", 
              description="API for construction a vocabulary from a webpages text content, returning dictionary with keys of words and values of occurences")

app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, python_exception_handler)



@app.post("/api/v1/extract",
        response_model=EndpointResponse,
        responses={422: {"model": EndpointError},
                   500: {"model": EndpointError}})

def extract_vocab(request:Request, body:EndpointInput):
    fastapi_logger.info("API extract called")
    fastapi_logger.info(f"Input: {body}")
    
    url = body.url 
    sort_type = body.sort_type or None 

    retreiver = Retriever(url=url)
    text = retreiver()
    text_processor = TextProcessor(text=text, sort_type=sort_type)
    vocab = text_processor()

    fastapi_logger.info(f"Constructed vocab: {vocab}")
    result = {  
        "url": url, 
        "sort_type": sort_type,
        "vocab": vocab
    }
    return {
        "error":False,
        "result": result 
    }


@app.get("/api/v1/health")
def health_check():
    return {"data":200}


if __name__ == "__main__":

    uvicorn.run("main:app", host="0.0.0.0", port=8080,
                reload=True, debug=True, log_config="/opt/logging.conf"
                )

