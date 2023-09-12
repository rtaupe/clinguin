"""
Module that contains the BackendPolicyDto
"""

from pydantic import BaseModel
from typing import Optional
from typing import List

class ContextDto(BaseModel):
    """
    Optional pass to the backend, which handles the context.
    """

    key: str
    value: str

class BackendPolicyDto(BaseModel):
    """
    Needed by the endpoints to get convert the transported json into something useful for the backend.
    """

    function: str
    context: Optional[List[ContextDto]] = []

