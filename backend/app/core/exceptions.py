from fastapi import HTTPException, status


class ConflictError(HTTPException):
    def __init__(self, detail: str) -> None:
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class UnauthorizedError(HTTPException):
    def __init__(self, detail: str = "인증이 필요합니다.") -> None:
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class ForbiddenError(HTTPException):
    def __init__(self, detail: str = "접근 권한이 없습니다.") -> None:
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class NotFoundError(HTTPException):
    def __init__(self, detail: str = "대상을 찾을 수 없습니다.") -> None:
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class BadRequestError(HTTPException):
    def __init__(self, detail: str) -> None:
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class RateLimitError(HTTPException):
    def __init__(self, detail: str = "요청 횟수가 너무 많습니다. 잠시 후 다시 시도해 주세요.") -> None:
        super().__init__(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=detail)


class PayloadTooLargeError(HTTPException):
    def __init__(self, detail: str = "요청 본문 크기가 허용 범위를 초과했습니다.") -> None:
        super().__init__(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=detail)


class SecurityError(HTTPException):
    def __init__(self, detail: str = "보안 정책에 따라 요청이 차단되었습니다.") -> None:
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)
