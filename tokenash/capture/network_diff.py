"""Differential network capture reporting for Claude Code vs Tokenash.

The capture format is intentionally JSONL so mitmproxy addons, tests, and
future packet capture tools can all produce the same records without a heavy
dependency in the Tokenash package.
"""

from __future__ import annotations

import base64
import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

SENSITIVE_HEADER_PARTS = ("authorization", "api-key", "apikey", "token", "secret", "cookie")
SENSITIVE_QUERY_PARTS = ("key", "token", "secret", "signature", "code")
MAX_BODY_PREVIEW_CHARS = 1200


@dataclass(frozen=True)
class CapturedExchange:
    """A sanitized HTTP request/response pair captured by the harness."""

    lane: str
    sequence: int
    method: str
    url: str
    host: str
    path: str
    request_headers: dict[str, str] = field(default_factory=dict)
    response_status: int | None = None
    response_headers: dict[str, str] = field(default_factory=dict)
    request_body_sha256: str | None = None
    request_body_size: int = 0
    request_json: Any | None = None
    request_body_preview: str | None = None

    @property
    def route_key(self) -> str:
        return f"{self.method.upper()} {self.host}{self.path}"

    @property
    def path_key(self) -> str:
        return f"{self.method.upper()} {self.path}"


@dataclass(frozen=True)
class CaptureDiff:
    """Comparison result between a direct lane and a Tokenash lane."""

    direct_count: int
    tokenash_count: int
    only_direct: list[str]
    only_tokenash: list[str]
    paired: list[dict[str, Any]]
    generated_at: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "generated_at": self.generated_at,
            "direct_count": self.direct_count,
            "tokenash_count": self.tokenash_count,
            "only_direct": self.only_direct,
            "only_tokenash": self.only_tokenash,
            "paired": self.paired,
        }


def _redact_value(value: object) -> str:
    if value is None:
        return ""
    text = str(value)
    if not text:
        return text
    return "<redacted>"


def sanitize_headers(headers: dict[str, Any] | None) -> dict[str, str]:
    sanitized: dict[str, str] = {}
    for key, value in (headers or {}).items():
        lower = str(key).lower()
        if any(part in lower for part in SENSITIVE_HEADER_PARTS):
            sanitized[str(key)] = _redact_value(value)
        else:
            sanitized[str(key)] = str(value)
    return sanitized


def sanitize_url(url: str) -> str:
    parsed = urlsplit(url)
    pairs = []
    for key, value in parse_qsl(parsed.query, keep_blank_values=True):
        if any(part in key.lower() for part in SENSITIVE_QUERY_PARTS):
            pairs.append((key, "<redacted>"))
        else:
            pairs.append((key, value))
    query = urlencode(pairs, doseq=True)
    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, query, ""))


def _body_bytes(record: dict[str, Any]) -> bytes:
    body_b64 = record.get("request_body_b64")
    if isinstance(body_b64, str):
        try:
            return base64.b64decode(body_b64, validate=True)
        except Exception:
            return b""
    body = record.get("request_body")
    if isinstance(body, str):
        return body.encode("utf-8", errors="replace")
    return b""


def _parse_json_body(body: bytes) -> Any | None:
    if not body:
        return None
    try:
        return json.loads(body.decode("utf-8"))
    except Exception:
        return None


def _preview_body(body: bytes) -> str | None:
    if not body:
        return None
    text = body[:MAX_BODY_PREVIEW_CHARS].decode("utf-8", errors="replace")
    return text.replace("\r\n", "\n")


def exchange_from_record(
    record: dict[str, Any], *, fallback_lane: str, sequence: int
) -> CapturedExchange:
    url = sanitize_url(str(record.get("url") or ""))
    parsed = urlsplit(url)
    path = parsed.path or "/"
    if parsed.query:
        path = f"{path}?{parsed.query}"
    body = _body_bytes(record)
    request_json = record.get("request_json")
    if request_json is None:
        request_json = _parse_json_body(body)
    body_sha = record.get("request_body_sha256")
    if body_sha is None and body:
        body_sha = hashlib.sha256(body).hexdigest()
    return CapturedExchange(
        lane=str(record.get("lane") or fallback_lane),
        sequence=int(record.get("sequence") or sequence),
        method=str(record.get("method") or "GET").upper(),
        url=url,
        host=parsed.netloc or str(record.get("host") or ""),
        path=path,
        request_headers=sanitize_headers(record.get("request_headers")),
        response_status=record.get("response_status"),
        response_headers=sanitize_headers(record.get("response_headers")),
        request_body_sha256=str(body_sha) if body_sha else None,
        request_body_size=int(record.get("request_body_size") or len(body)),
        request_json=request_json,
        request_body_preview=_preview_body(body),
    )


def load_capture_file(path: str | Path, *, fallback_lane: str) -> list[CapturedExchange]:
    """Load a JSONL capture file produced by the mitmproxy addon."""

    exchanges: list[CapturedExchange] = []
    capture_path = Path(path)
    for line_number, line in enumerate(capture_path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        record = json.loads(line)
        exchanges.append(
            exchange_from_record(record, fallback_lane=fallback_lane, sequence=line_number)
        )
    return exchanges


def _json_paths(value: Any, prefix: str = "$") -> dict[str, Any]:
    if isinstance(value, dict):
        paths: dict[str, Any] = {}
        for key, child in sorted(value.items()):
            paths.update(_json_paths(child, f"{prefix}.{key}"))
        return paths or {prefix: {}}
    if isinstance(value, list):
        paths = {}
        for index, child in enumerate(value):
            paths.update(_json_paths(child, f"{prefix}[{index}]"))
        return paths or {prefix: []}
    return {prefix: value}


def _header_delta(
    direct: dict[str, str], tokenash: dict[str, str]
) -> tuple[list[str], list[str], list[str]]:
    direct_keys = {key.lower(): key for key in direct}
    tokenash_keys = {key.lower(): key for key in tokenash}
    only_direct = sorted(direct_keys[key] for key in set(direct_keys) - set(tokenash_keys))
    only_tokenash = sorted(tokenash_keys[key] for key in set(tokenash_keys) - set(direct_keys))
    changed: list[str] = []
    for lower in sorted(set(direct_keys) & set(tokenash_keys)):
        d_key = direct_keys[lower]
        h_key = tokenash_keys[lower]
        if direct[d_key] != tokenash[h_key]:
            changed.append(d_key)
    return only_direct, only_tokenash, changed


def _header_value(headers: dict[str, str], name: str) -> str | None:
    target = name.lower()
    for key, value in headers.items():
        if key.lower() == target:
            return value
    return None


def _anthropic_request_summary(exchange: CapturedExchange) -> dict[str, Any]:
    request_json = exchange.request_json if isinstance(exchange.request_json, dict) else {}
    tools = request_json.get("tools")
    tool_count = len(tools) if isinstance(tools, list) else 0
    tool_bytes = (
        len(json.dumps(tools, sort_keys=True, separators=(",", ":")).encode("utf-8"))
        if isinstance(tools, list)
        else 0
    )
    return {
        "anthropic_beta": _header_value(exchange.request_headers, "anthropic-beta"),
        "tools_count": tool_count,
        "tools_bytes": tool_bytes,
    }


def _pair_exchanges(
    direct: list[CapturedExchange], tokenash: list[CapturedExchange], *, pair_by: str = "path"
) -> tuple[list[tuple[CapturedExchange, CapturedExchange]], list[str], list[str]]:
    direct_by_key: dict[str, list[CapturedExchange]] = {}
    tokenash_by_key: dict[str, list[CapturedExchange]] = {}
    for item in direct:
        key = item.route_key if pair_by == "route" else item.path_key
        direct_by_key.setdefault(key, []).append(item)
    for item in tokenash:
        key = item.route_key if pair_by == "route" else item.path_key
        tokenash_by_key.setdefault(key, []).append(item)

    pairs: list[tuple[CapturedExchange, CapturedExchange]] = []
    only_direct: list[str] = []
    only_tokenash: list[str] = []
    for key in sorted(set(direct_by_key) | set(tokenash_by_key)):
        direct_items = direct_by_key.get(key, [])
        tokenash_items = tokenash_by_key.get(key, [])
        shared = min(len(direct_items), len(tokenash_items))
        pairs.extend(zip(direct_items[:shared], tokenash_items[:shared], strict=False))
        only_direct.extend([item.route_key for item in direct_items[shared:]])
        only_tokenash.extend([item.route_key for item in tokenash_items[shared:]])
    return pairs, only_direct, only_tokenash


def compare_captures(
    direct: list[CapturedExchange], tokenash: list[CapturedExchange], *, pair_by: str = "path"
) -> CaptureDiff:
    pairs, only_direct, only_tokenash = _pair_exchanges(direct, tokenash, pair_by=pair_by)
    paired: list[dict[str, Any]] = []
    for direct_item, tokenash_item in pairs:
        direct_paths = (
            _json_paths(direct_item.request_json) if direct_item.request_json is not None else {}
        )
        tokenash_paths = (
            _json_paths(tokenash_item.request_json)
            if tokenash_item.request_json is not None
            else {}
        )
        only_direct_json = sorted(set(direct_paths) - set(tokenash_paths))
        only_tokenash_json = sorted(set(tokenash_paths) - set(direct_paths))
        changed_json = sorted(
            path
            for path in set(direct_paths) & set(tokenash_paths)
            if direct_paths[path] != tokenash_paths[path]
        )
        headers_only_direct, headers_only_tokenash, headers_changed = _header_delta(
            direct_item.request_headers, tokenash_item.request_headers
        )
        paired.append(
            {
                "route": direct_item.route_key,
                "tokenash_route": tokenash_item.route_key,
                "direct_sequence": direct_item.sequence,
                "tokenash_sequence": tokenash_item.sequence,
                "status": {
                    "direct": direct_item.response_status,
                    "tokenash": tokenash_item.response_status,
                },
                "request_body_size": {
                    "direct": direct_item.request_body_size,
                    "tokenash": tokenash_item.request_body_size,
                    "delta": tokenash_item.request_body_size - direct_item.request_body_size,
                },
                "request_body_sha256": {
                    "direct": direct_item.request_body_sha256,
                    "tokenash": tokenash_item.request_body_sha256,
                    "same": direct_item.request_body_sha256 == tokenash_item.request_body_sha256,
                },
                "anthropic": {
                    "direct": _anthropic_request_summary(direct_item),
                    "tokenash": _anthropic_request_summary(tokenash_item),
                },
                "headers": {
                    "only_direct": headers_only_direct,
                    "only_tokenash": headers_only_tokenash,
                    "changed": headers_changed,
                },
                "json": {
                    "only_direct": only_direct_json,
                    "only_tokenash": only_tokenash_json,
                    "changed": changed_json,
                },
            }
        )
    return CaptureDiff(
        direct_count=len(direct),
        tokenash_count=len(tokenash),
        only_direct=only_direct,
        only_tokenash=only_tokenash,
        paired=paired,
        generated_at=datetime.now(timezone.utc).isoformat(),
    )


def _list_or_dash(values: list[str]) -> str:
    return ", ".join(values) if values else "-"


def render_markdown_report(diff: CaptureDiff) -> str:
    lines = [
        "# Differential Network Capture Report",
        "",
        f"Generated: `{diff.generated_at}`",
        "",
        "## Summary",
        "",
        f"- Direct exchanges: `{diff.direct_count}`",
        f"- Tokenash exchanges: `{diff.tokenash_count}`",
        f"- Paired exchanges: `{len(diff.paired)}`",
        f"- Only direct: `{len(diff.only_direct)}`",
        f"- Only Tokenash: `{len(diff.only_tokenash)}`",
        "",
    ]
    if diff.only_direct:
        lines.extend(["## Only Direct", "", *[f"- `{route}`" for route in diff.only_direct], ""])
    if diff.only_tokenash:
        lines.extend(
            ["## Only Tokenash", "", *[f"- `{route}`" for route in diff.only_tokenash], ""]
        )

    lines.extend(
        [
            "## Paired Exchanges",
            "",
            "| Route | Status | Body Bytes | Body SHA | Header Delta | JSON Delta |",
            "| --- | --- | ---: | --- | --- | --- |",
        ]
    )
    for item in diff.paired:
        route = item["route"]
        if item.get("tokenash_route") and item["tokenash_route"] != route:
            route = f"{route} -> {item['tokenash_route']}"
        status = f"{item['status']['direct']} -> {item['status']['tokenash']}"
        sizes = item["request_body_size"]
        body = f"{sizes['direct']} -> {sizes['tokenash']} ({sizes['delta']:+})"
        sha = "same" if item["request_body_sha256"]["same"] else "changed"
        headers = item["headers"]
        header_delta = (
            f"+{_list_or_dash(headers['only_tokenash'])}; "
            f"-{_list_or_dash(headers['only_direct'])}; "
            f"changed={_list_or_dash(headers['changed'])}"
        )
        json_delta = item["json"]
        json_text = (
            f"+{_list_or_dash(json_delta['only_tokenash'])}; "
            f"-{_list_or_dash(json_delta['only_direct'])}; "
            f"changed={_list_or_dash(json_delta['changed'])}"
        )
        anthropic = item.get("anthropic", {})
        direct_anthropic = anthropic.get("direct", {})
        tokenash_anthropic = anthropic.get("tokenash", {})
        tool_delta = tokenash_anthropic.get("tools_bytes", 0) - direct_anthropic.get(
            "tools_bytes", 0
        )
        json_text = (
            f"{json_text}; tools={direct_anthropic.get('tools_count', 0)}"
            f"->{tokenash_anthropic.get('tools_count', 0)}"
            f" ({tool_delta:+} bytes)"
        )
        lines.append(
            f"| `{route}` | `{status}` | `{body}` | `{sha}` | {header_delta} | {json_text} |"
        )
    lines.append("")
    return "\n".join(lines)
