import pytest
from fastapi.testclient import TestClient
from extractor.main import app
from typing import Dict
import logging
import random
import copy

logger = logging.getLogger()
logger.setLevel(logging.INFO)

client = TestClient(app)


def test_api_error_response():
    pass


@pytest.mark.parametrize(
    "testing_case, url, sort_type",
    [
        (
            "Response of unsorted vocab construction request, sort_type=None with valid url",
            "https://www.reddit.com/",
            None,
        ),
        (
            "Response of unsorted vocab construction request, with sort_type unspecified and valid url",
            "https://www.reddit.com/",
            "",
        ),
    ],
)
def test_api_response(testing_case, url, sort_type):
    """
    Testing api vocab construction
    """
    headers = {}
    body = {"url": url, "sort_type": sort_type}
    if sort_type == "":
        del body["sort_type"]
    response = client.post("/api/extract", headers=headers, json=body)
    try:
        assert response.status_code == 200
    except AssertionError:
        logger.info(
            f"Case:{testing_case}.\nTest failed for Expected status code 200, got {response.status_code}\nResponse:{response.json()}"
        )
        raise

    response_json = response.json()
    try:
        assert isinstance(response_json["result"], Dict)
    except AssertionError:
        logger.info(
            f"Case:{testing_case}.\nThe result was supposed to be a python dictionary. Got type {type(response_json['result'])}"
        )
        raise


@pytest.mark.parametrize(
    "testing_case, url, sort_type",
    [
        (
            "Response of frequency-based vocab construction request, sort_type=frequency",
            "https://www.reddit.com/",
            "frequency",
        ),
        (
            "Response of frequency-based sorted construction request, sort_type=alphabetically",
            "https://www.reddit.com/",
            "alphabetically",
        ),
    ],
)
def test_sort_based_extraction(testing_case, url, sort_type):
    """testing api sorted vocab extraction"""
    headers = {}
    body = {"url": url, "sort_type": sort_type}
    response = client.post("/api/extract", headers=headers, json=body)
    try:
        assert response.status_code == 200
    except AssertionError:
        logger.info(
            f"Case:{testing_case}.\nExpected status code 200, got {response.status_code}\nResponse:{response.json()}"
        )
        raise
    response_json = response.json()

    from pprint import pprint

    try:
        assert not response_json["error"]
    except AssertionError:
        logger.info("Got failed response")

    if response_json["result"]["sort_type"] == "alphabetically":
        try:
            print("*" * 20)
            pprint(type(response_json["result"]["vocab"]))
            print("*" * 20)
            alpha_sorted = list(response_json["result"]["vocab"].keys())
            alpha_resorted = copy.copy(alpha_sorted)
            random.shuffle(alpha_resorted)  # shuffles in place
            alpha_resorted = sorted(alpha_resorted)
            assert alpha_resorted == alpha_sorted
        except AssertionError:
            logger.info(
                f"Case:{testing_case}. FALED\n Returned order {alpha_sorted[:10]}\n Reordered order {alpha_resorted[:10]}"
            )
            raise

    if response_json["result"]["sort_type"] == "frequency":
        try:
            freq_sorted = list(dict(response_json["result"]["vocab"]).values())
            freq_resorted = copy.copy(freq_sorted)
            random.shuffle(freq_resorted)
            freq_resorted = sorted(freq_resorted, reverse=True)

            assert freq_sorted == freq_resorted
        except AssertionError:
            logger.info(
                f"Case:{testing_case}. FALED\nOriginal order: {freq_sorted[:10]}\nReordered order : {freq_sorted[:10]}"
            )
            raise
