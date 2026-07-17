#!/usr/bin/env python3
"""Pure parser for Tencent quote responses; performs no network or file I/O."""

from __future__ import annotations

import re


_RECORD = re.compile(r'^\s*[^=]+="(?P<payload>.*)"\s*$')


def _required_float(value: str, field: str) -> float:
    if not value.strip():
        raise ValueError(f"missing {field}")
    try:
        return float(value)
    except ValueError as exc:
        raise ValueError(f"invalid {field}: {value!r}") from exc


def parse_tencent_quotes(raw: bytes) -> list[dict[str, object]]:
    """Decode a GBK Tencent response and parse its quote records."""
    if not isinstance(raw, bytes):
        raise TypeError("raw response must be bytes")

    text = raw.decode("gbk", errors="strict")
    quotes: list[dict[str, object]] = []
    for fragment in text.split(";"):
        if not fragment.strip():
            continue
        match = _RECORD.fullmatch(fragment)
        if match is None:
            raise ValueError("malformed Tencent quote record")
        fields = match.group("payload").split("~")
        if len(fields) < 33:
            raise ValueError(f"expected at least 33 fields, got {len(fields)}")
        code = fields[2].strip()
        name = fields[1].strip()
        if not code or not name:
            raise ValueError("missing code or name")
        quotes.append(
            {
                "code": code,
                "name": name,
                "price": _required_float(fields[3], "price"),
                "change_pct": _required_float(fields[32], "change_pct"),
                "field_count": len(fields),
            }
        )
    if not quotes:
        raise ValueError("no Tencent quote records")
    return quotes
