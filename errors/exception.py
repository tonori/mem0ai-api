from fastapi import HTTPException, status


class ErrorHttpException(HTTPException):
    code: int
    error: str
    message: str

    def __init__(self, code: int = 500, error: str = "INTERNAL_SERVER_ERROR",
                 message: str = "INTERNAL_SERVER_ERROR") -> None:
        super().__init__(
            status_code=200,
            detail={"code": code, "error": error, "message": message},
        )
        self.code = code
        self.error = error
        self.message = message


class UnauthorizedException(ErrorHttpException):
    def __init__(self):
        super().__init__(
            code=status.HTTP_401_UNAUTHORIZED,
            message="UNAUTHORIZED",
            error="Authorization_Error"
        )
