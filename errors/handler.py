from fastapi import Request, status
from fastapi.responses import JSONResponse
from .exception import UnauthorizedException
from response import ErrorResponse
from qdrant_client.http.exceptions import UnexpectedResponse


def unauthorized_exception_handler(request: Request, exc: UnauthorizedException):
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=ErrorResponse(
            code=status.HTTP_401_UNAUTHORIZED,
            error="Unauthorized_Error",
            message="Unauthorized"
        ).dict()
    )


def qdrant_client_unexpected_handler(request: Request, exc: UnexpectedResponse):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            code=exc.status_code,
            error="UnexpectedResponse_Error",
            message="Collection doesn't exist!"
        ).dict()
    )
