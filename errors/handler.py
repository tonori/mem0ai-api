from fastapi import Request, status
from fastapi.responses import JSONResponse
from .exception import UnauthorizedException
from response import ErrorResponse


def unauthorized_exception_handler(request: Request, exc: UnauthorizedException):
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=ErrorResponse(
            code=status.HTTP_401_UNAUTHORIZED,
            error="Unauthorized_Error",
            message="Unauthorized"
        ).dict()
    )
