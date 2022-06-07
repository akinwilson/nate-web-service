#!/usr/bin/env python3 

import os 
import sys 

import uvicorn 

from vocabConstructor import Retriever, TextProcessor

from fastapi import FastAPI, Request
from fastapi.logger import logger 
from fastapi.exceptions import RequestValidationError
from exception_handler import python_exception_handler, validation_exception_handler

from schema import * 


app = FastAPI(title="Webpage vocab constructor", 
              description="API for construction a vocabulary from a webpages text content, returning dictionary with keys of words and values of occurences")

app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, python_exception_handler)



@app.post("/api/v1/extract",
        response_model=EndpointResponse,
        responses={422: {"model": EndpointError},
                   500: {"model": EndpointError}})



def extract_vocab(request:Request, body:EndpointInput):
    logger.info("API extract called")
    logger.info(f"Input: {body}")
    url = body.url 
    sort_type = body.sort_type or None 

    retreiver = Retriever(url=url)
    text = retreiver()
    text_processor = TextProcessor(text=text, sort_type=sort_type)
    vocab = text_processor()

    logger.info(f"Constructed vocab: {vocab}")
    result = {  
        "url": url, 
        "sort_type": sort_type,
        "vocab": vocab
    }
    return {
        "error":False,
        "result": result 
    }

if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=8080,
                reload=True, debug=True, log_config="logging.conf"
                )
