import json
import re
import threading
from datetime import datetime, timezone
from pathlib import Path

from fastapi import Request
from starlette.responses import Response

from app.config import settings


class JsonRequestLogger:
    ENDPOINT_NAMES = {
        "/api/orders": "ordenes",
        "/api/products": "productos",
        "/api/products/stock": "stock_productos",
        "/api/products/categories": "categorias_productos",
        "/health": "health",
    }

    def __init__(self, output_dir: str | None = None) -> None:
        self.output_dir = Path(output_dir or settings.json_output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()

    async def log(self, request: Request, response: Response) -> Response:
        request_body = await request.body()
        response_body = b""
        async for chunk in response.body_iterator:
            response_body += chunk

        request_payload = self._decode_json(request_body)
        response_payload = self._decode_json(response_body)

        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "request": {
                "method": request.method,
                "path": request.url.path,
                "query": dict(request.query_params),
                "body": request_payload,
            },
            "response": {
                "status_code": response.status_code,
                "body": response_payload,
            },
        }

        endpoint_name = self._endpoint_name(request.url.path)
        output_path = self.output_dir / self._next_filename(endpoint_name)
        output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

        return Response(
            content=response_body,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type,
        )

    def _endpoint_name(self, path: str) -> str:
        if path in self.ENDPOINT_NAMES:
            return self.ENDPOINT_NAMES[path]

        clean_path = path.strip("/")
        if not clean_path:
            return "Consulta"

        name = clean_path.replace("/", "_")
        name = re.sub(r"[^a-zA-Z0-9_]", "", name)
        return name[:60] or "Consulta"

    def _next_filename(self, endpoint_name: str) -> str:
        pattern = re.compile(rf"^{re.escape(endpoint_name)}_(\d+)\.json$")
        with self._lock:
            max_number = 0
            for file_path in self.output_dir.glob(f"{endpoint_name}_*.json"):
                match = pattern.match(file_path.name)
                if match:
                    number = int(match.group(1))
                    if number > max_number:
                        max_number = number

            return f"{endpoint_name}_{max_number + 1}.json"

    @staticmethod
    def _decode_json(raw: bytes):
        if not raw:
            return None

        text = raw.decode("utf-8", errors="replace")
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return text
