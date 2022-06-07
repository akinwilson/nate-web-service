#!/usr/bin/env python3

from typing import Optional,Dict, Union, Set, List
import validators
from pydantic import BaseModel, Field,validator 


class EndpointInput(BaseModel):
    '''
    Input values for page vocab constructor endpoint
    '''
    _valid_sort_options: List[str] = ['frequency', 'alphabetically']
    url: str = Field( ... , example="https://www.reddit.com/", title="URL of page to extract word occurrences")
    sort_type: Optional[str] = Field(None, example="frequency", title=f"What sorting typing to perform. Options are {_valid_sort_options}")

    @validator('sort_type')
    def valid_sort_type(cls, v):
        sort_options = ['frequency', 'alphabetically']
        assert v in [None] + cls._valid_sort_options , f'{v} not valid sorting option provided. Valid sort options are:{cls._valid_sort_options}'
        return v

    @validator('url')
    def valid_url(cls,v):
        assert validators.url(v), f"'{v}' is not valid URL"
        return v


class EndpointResult(BaseModel):
    '''
    Constructed vocabulary result
    '''
    url: str = Field( ... , example="https://www.reddit.com/", title="URL of page to extract word occurrences")
    sort_type: Optional[str] = Field( None , example="frequency", title="Whether sorting (frequency-based or alphabetically) was performed")
    vocab: Dict = Field(..., example="{'words':10, 'from':9, 'webpage':5}", title="Constructed vocabulary dictionary") 


class EndpointResponse(BaseModel):
    error: bool = Field(..., example=False, title="Whether there occured an error")
    result: EndpointResult = ... 


class EndpointError(BaseModel):
    error: bool = Field( ... , example=True, title="Whether an error occured or not")
    message: str = Field( ... , example='', title="Error message")