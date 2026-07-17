#!/usr/bin/env python3
"""Read-only probe for optional Pantalone host capabilities."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import yaml


def probe(manifest_path: Path, hermes_home: Path) -> dict:
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    results = []
    for relative_path, contract in sorted(manifest["capabilities"].items()):
        target = hermes_home / relative_path
        available = target.is_file()
        results.append(
            {
                "path": relative_path,
                "required": bool(contract["required"]),
                "available": available,
                "fallback": contract["fallback"],
            }
        )
    missing = [item for item in results if not item["available"]]
    return {
        "hermes_home": str(hermes_home),
        "total": len(results),
        "available": len(results) - len(missing),
        "missing_optional": len(missing),
        "required_missing": [item["path"] for item in missing if item["required"]],
        "capabilities": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "references/external-capabilities.yaml",
    )
    parser.add_argument(
        "--hermes-home",
        type=Path,
        default=None,
    )
    args = parser.parse_args()
    if args.hermes_home is None:
        raw_home = os.environ.get("HERMES_HOME", "").strip()
        args.hermes_home = Path(raw_home) if raw_home else None
    if args.hermes_home is None:
        parser.error("HERMES_HOME is empty; pass --hermes-home explicitly")
    result = probe(args.manifest, args.hermes_home)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result["required_missing"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
