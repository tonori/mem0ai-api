from pydantic import BaseModel
from typing import Any, Literal
from typing_extensions import TypedDict


class SuccessfulResponse(BaseModel):
    code: int = 0
    data: Any = None


class ErrorResponse(BaseModel):
    code: int = 500
    error: str = "INTERNAL_SERVER_ERROR"
    message: str = "INTERNAL_SERVER_ERROR"


class StoreMemoryResponse(SuccessfulResponse):
    class StoreMemoryExecuteResult(TypedDict):
        id: str
        event: str
        data: str

    def __init__(self, execute_result: StoreMemoryExecuteResult):
        super().__init__(
            data=execute_result
        )
