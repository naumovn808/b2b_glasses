import base64
import json
import logging
from typing import Any, Dict, Iterator, Optional, Tuple
from urllib import error as urllib_error
from urllib import parse as urllib_parse
from urllib import request as urllib_request

from django.conf import settings

try:
    import requests
except ImportError:  # pragma: no cover - fallback until image rebuild installs requests
    requests = None

logger = logging.getLogger(__name__)


class OneCAPIError(Exception):
    """Ошибка, возвращённая REST API 1С."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        error_code: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.payload = payload or {}


class OneCConnectionError(OneCAPIError):
    """Сетевая ошибка или таймаут при обращении к 1С."""


class OneCClient:
    """
    Синхронный HTTP-клиент для взаимодействия с HTTP-сервисом 1С (REST API + Basic Auth).
    Использует requests.Session при наличии библиотеки requests и автоматически
    переключается на urllib.request, если контейнер ещё не пересобран.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        timeout: Optional[int] = None,
    ):
        self.base_url = (base_url or settings.ONE_C_BASE_URL).rstrip("/")
        self.username = username if username is not None else settings.ONE_C_API_USER
        self.password = password if password is not None else settings.ONE_C_API_PASSWORD
        self.timeout = timeout or getattr(settings, "ONE_C_TIMEOUT", 30)

        self.session = None
        if requests is not None:
            self.session = requests.Session()
            if self.username:
                self.session.auth = (self.username, self.password)
            self.session.headers.update(
                {
                    "Accept": "application/json",
                    "Content-Type": "application/json; charset=utf-8",
                }
            )

    def _build_url(self, path: str) -> str:
        clean_path = "/" + path.lstrip("/")
        return f"{self.base_url}{clean_path}"

    def _basic_auth_header(self) -> Optional[str]:
        if not self.username:
            return None
        token = base64.b64encode(
            f"{self.username}:{self.password}".encode("utf-8")
        ).decode("ascii")
        return f"Basic {token}"

    def _send_via_requests(
        self,
        method: str,
        url: str,
        params: Optional[Dict[str, Any]],
        json_body: Optional[Dict[str, Any]],
        timeout: int,
    ) -> Tuple[int, bytes]:
        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=json_body,
                timeout=timeout,
            )
            return response.status_code, response.content
        except requests.Timeout as exc:
            logger.error("1C API timeout [%s %s]: %s", method, url, exc)
            raise OneCConnectionError(
                "Превышено время ожидания ответа от 1С.",
                error_code="TIMEOUT",
            ) from exc
        except requests.RequestException as exc:
            logger.error("1C API connection error [%s %s]: %s", method, url, exc)
            raise OneCConnectionError(
                f"Не удалось подключиться к 1С: {exc}",
                error_code="CONNECTION_ERROR",
            ) from exc

    def _send_via_urllib(
        self,
        method: str,
        url: str,
        params: Optional[Dict[str, Any]],
        json_body: Optional[Dict[str, Any]],
        timeout: int,
    ) -> Tuple[int, bytes]:
        full_url = url
        if params:
            query = urllib_parse.urlencode(
                {k: v for k, v in params.items() if v is not None}
            )
            if query:
                sep = "&" if "?" in full_url else "?"
                full_url = f"{full_url}{sep}{query}"

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json; charset=utf-8",
        }
        auth_header = self._basic_auth_header()
        if auth_header:
            headers["Authorization"] = auth_header

        body_bytes = None
        if json_body is not None:
            body_bytes = json.dumps(json_body, ensure_ascii=False).encode("utf-8")

        req = urllib_request.Request(
            full_url, data=body_bytes, headers=headers, method=method
        )
        try:
            with urllib_request.urlopen(req, timeout=timeout) as resp:
                return resp.status, resp.read()
        except urllib_error.HTTPError as exc:
            return exc.code, exc.read()
        except TimeoutError as exc:
            logger.error("1C API timeout [%s %s]: %s", method, full_url, exc)
            raise OneCConnectionError(
                "Превышено время ожидания ответа от 1С.",
                error_code="TIMEOUT",
            ) from exc
        except urllib_error.URLError as exc:
            logger.error("1C API connection error [%s %s]: %s", method, full_url, exc)
            raise OneCConnectionError(
                f"Не удалось подключиться к 1С: {exc.reason}",
                error_code="CONNECTION_ERROR",
            ) from exc

    def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json_body: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None,
    ) -> Dict[str, Any]:
        url = self._build_url(path)
        req_timeout = timeout or self.timeout

        if self.session is not None:
            status_code, content = self._send_via_requests(
                method, url, params, json_body, req_timeout
            )
        else:
            status_code, content = self._send_via_urllib(
                method, url, params, json_body, req_timeout
            )

        try:
            data = json.loads(content.decode("utf-8")) if content else {}
        except (ValueError, UnicodeDecodeError) as exc:
            preview = content[:500].decode("utf-8", errors="replace") if content else ""
            logger.error(
                "1C API non-JSON response [%s %s] status=%s body=%r",
                method,
                url,
                status_code,
                preview,
            )
            raise OneCAPIError(
                f"1С вернула некорректный ответ (HTTP {status_code}).",
                status_code=status_code,
                error_code="INVALID_RESPONSE",
            ) from exc

        if 200 <= status_code < 300:
            return data

        error_code = data.get("error_code") if isinstance(data, dict) else None
        message = (
            data.get("message")
            if isinstance(data, dict) and data.get("message")
            else f"Ошибка 1С (HTTP {status_code})"
        )
        logger.warning(
            "1C API error [%s %s] status=%s error_code=%s message=%s",
            method,
            url,
            status_code,
            error_code,
            message,
        )
        raise OneCAPIError(
            message=message,
            status_code=status_code,
            error_code=error_code,
            payload=data if isinstance(data, dict) else {},
        )

    def get_frames_page(self, page: int = 1, limit: Optional[int] = None) -> Dict[str, Any]:
        page_limit = limit or getattr(settings, "ONE_C_PAGE_LIMIT", 500)
        return self._request(
            "GET",
            "/v1/catalog/frames",
            params={"page": page, "limit": page_limit},
        )

    def get_lenses_page(self, page: int = 1, limit: Optional[int] = None) -> Dict[str, Any]:
        page_limit = limit or getattr(settings, "ONE_C_PAGE_LIMIT", 500)
        return self._request(
            "GET",
            "/v1/catalog/lenses",
            params={"page": page, "limit": page_limit},
        )

    def _iter_paginated(
        self,
        fetch_page,
        limit: Optional[int] = None,
    ) -> Iterator[Dict[str, Any]]:
        page_limit = limit or getattr(settings, "ONE_C_PAGE_LIMIT", 500)
        page = 1
        fetched = 0

        while True:
            data = fetch_page(page=page, limit=page_limit)
            items = data.get("items") or []
            total_count = data.get("count")

            yield {
                "page": page,
                "count": total_count,
                "currency": data.get("currency"),
                "items": items,
            }

            if not items:
                break

            fetched += len(items)
            if len(items) < page_limit:
                break
            if isinstance(total_count, int) and total_count >= 0 and fetched >= total_count:
                break

            page += 1

    def iter_frames(self, limit: Optional[int] = None) -> Iterator[Dict[str, Any]]:
        return self._iter_paginated(self.get_frames_page, limit=limit)

    def iter_lenses(self, limit: Optional[int] = None) -> Iterator[Dict[str, Any]]:
        return self._iter_paginated(self.get_lenses_page, limit=limit)

    def get_customers(self) -> Dict[str, Any]:
        return self._request("GET", "/v1/customers")

    def create_order(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._request("POST", "/v1/orders", json_body=payload)
