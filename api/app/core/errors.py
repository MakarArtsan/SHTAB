"""Единый формат ошибок: {"error": {"code", "message", "details"}}.

`message` — человеческий текст по-русски, его показывают пользователю.
"""

from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


class AccessDenied(Exception):
    """Запрошены данные вне поддерева пользователя.

    Причину наружу не раскрываем: ответ одинаков и для «нет прав»,
    и для «нет такого узла», чтобы по коду ответа нельзя было разведать дерево.
    """

# Тексты по кодам ответа. Пользователю не показываем ни номер ошибки, ни стек.
_MESSAGES: dict[int, str] = {
    400: "Не удалось обработать запрос. Проверьте данные и попробуйте ещё раз.",
    401: "Нужно войти заново.",
    403: "Недостаточно прав для этого действия.",
    404: "Не нашли то, что вы запросили.",
    409: "Такая запись уже есть.",
    422: "Проверьте заполненные поля.",
    429: "Слишком много запросов подряд. Подождите немного.",
    500: "Что-то пошло не так на нашей стороне. Мы уже знаем и разбираемся.",
}

_CODES: dict[int, str] = {
    400: "bad_request",
    401: "unauthorized",
    403: "forbidden",
    404: "not_found",
    409: "conflict",
    422: "validation_error",
    429: "rate_limited",
    500: "internal_error",
}


def error_response(status: int, details: Any | None = None) -> JSONResponse:
    body: dict[str, Any] = {
        "code": _CODES.get(status, "error"),
        "message": _MESSAGES.get(status, _MESSAGES[500]),
    }
    if details is not None:
        body["details"] = details
    return JSONResponse(status_code=status, content={"error": body})


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(StarletteHTTPException)
    async def _http_error(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        return error_response(exc.status_code)

    @app.exception_handler(AccessDenied)
    async def _access_denied(_: Request, __: AccessDenied) -> JSONResponse:
        return error_response(403)

    @app.exception_handler(RequestValidationError)
    async def _validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
        fields = [".".join(str(p) for p in err["loc"][1:]) for err in exc.errors()]
        return error_response(422, {"fields": fields})
