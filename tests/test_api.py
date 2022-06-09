import pytest
from fastapi.testclient import TestClient
from extractor.main import app
from typing import Dict, Set
import logging
import random
import copy

client = TestClient(app)


def test_healthcheck():
    STATUS_CODE = 200
    r = client.get("/api/health")
    assert r.status_code == STATUS_CODE, f"Status code of health check did not return correct response code. Expected: {STATUS_CODE}, Got: {r.status_code}"
    assert r.json()['status_code'] == STATUS_CODE, f"Health check didn't return expected json object containing status code. . Expected: {STATUS_CODE}, Got {r.json()['status_code']}" 
    

def test_bad_url_response_code():
    STATUS_CODE = 422
    body = {"url": "reddit.com", "sort_type": None}
    r = client.post("/api/extract", json=body)
    assert r.status_code == STATUS_CODE, f"Incorrect status code return for malformed url. Expected: {STATUS_CODE}. Got: {r.status_code}"
    assert r.json()['error'], f"Error key returned for malformed url. Expected: True. Got: {r.json()['error']}"



def test_bad_sort_type_response_code():
    STATUS_CODE = 422
    body = {"url": "https://www.reddit.com/", "sort_type": "inversed_alphabetically"}
    r = client.post("/api/extract", json=body)
    assert r.status_code == STATUS_CODE, f"Returned status code for bad sort_type incorrect. Expected: {STATUS_CODE}, Got: {r.status_code}"


def test_no_sort_type_provided_response():
    STATUS_CODE = 200
    body = {"url": "https://www.reddit.com/"}
    r = client.post("/api/extract", json=body)
    assert r.status_code == STATUS_CODE, f"Returned incorrect status code for no sort_type provided. Expected: {STATUS_CODE}, Got: {r.status_code}"
    assert not r.json()['error'], f"Return error bool incorrect for no sort type provided. Expected: False, Got: {r.json()['error']}"
    assert r.json()['result']['sort_type'] == None, f"Returned sort type of none provided is incorrect. Expected: None, got {r.json()['result']['sort_type']}"




def test_set_object_response_for_empty_vocab():
    STATUS_CODE = 200
    body = {"url": "https://www.blank.org/"}
    r = client.post("/api/extract",json=body)
    assert r.status_code == STATUS_CODE, f"Returned incorrect status code for empty vocab to be returned. Expected: {STATUS_CODE}, Got: {r.status_code}"
    assert not r.json()['error'], f"Return error bool incorrect for no sort type provided. Expected: False, Got: {r.json()['error']}"
    assert len(r.json()['result']['vocab']) == 0 , f"Returned object should be empty vocabulary. Expected: empty dict, Got {r.json()['result']['vocab']}"

    

def test_sorting_alphabetically():
    STATUS_CODE = 200
    body = {"url": "https://reddit.com", "sort_type": "alphabetically"}
    r = client.post("/api/extract", json=body)
    assert r.status_code == STATUS_CODE, f"Returned incorrect status code for alphabetcially sorting returned. Expected: {STATUS_CODE}, Got: {r.status_code}"
    assert not r.json()['error'], f"Return error bool incorrect for alphabetcially sorting provided. Expected: False, Got: {r.json()['error']}"
    alpha_sorted = list(r.json()["result"]["vocab"].keys())
    alpha_resorted = copy.copy(alpha_sorted) # need copy to avoid random.shuffle tracing up the previous frame and sorting original object
    random.shuffle(alpha_resorted)  # shuffles in place, hence the copy
    alpha_resorted = sorted(alpha_resorted)
    assert alpha_resorted == alpha_sorted, f"Returned alphabetically sorted dictionary doesn't follow alphabetical order.Expected: {alpha_sorted[:10]}. Got: {alpha_resorted[:10]}"




def test_sorting_frequency_based():
    STATUS_CODE = 200
    body = {"url": "https://reddit.com", "sort_type": "frequency"}
    r = client.post("/api/extract", json=body)
    assert r.status_code == STATUS_CODE, f"Returned incorrect status code for frequency sorting returned. Expected: {STATUS_CODE}, Got: {r.status_code}"
    assert not r.json()['error'], f"Return error bool incorrect for frequency sorting provided. Expected: False, Got: {r.json()['error']}"
    
    freq_sorted = list(dict(r.json()["result"]["vocab"]).values())
    freq_resorted = copy.copy(freq_sorted)
    random.shuffle(freq_resorted)
    freq_resorted = sorted(freq_resorted, reverse=True)
    assert freq_resorted == freq_sorted, f"Returned frequency sorted dictionary doesn't follow  order. Expected count order: {freq_sorted[:10]}. Got: {freq_resorted[:10]}"

