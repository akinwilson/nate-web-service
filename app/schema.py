#!/usr/bin/env python3

from typing import Optional,Dict 
import validators
from pydantic import BaseModel, Field,validator 

class EndpointInput(BaseModel):
    url: str = Field( ... , example="https://www.reddit.com/", title="URL of page to extract word occurrences")
    sort_type: Optional[str] = Field( None , example="frequency", title="Whether to perform sorting (frequency-based or alphabetically) on the returned vocabulary. Valid options are: ")

    @validator('sort_type')
    def valid_sort_type(cls, v):
        sort_options = ['frequency', 'alphabetically']
        assert v in [None] + sort_options , f'{v} not valid sort option provided. Valid sort options are:{sort_options}'
        return v

    @validator('url')
    def valid_url(cls,v):
        assert validators.url(v), f"'{v}' is not valid URL"
        return v
