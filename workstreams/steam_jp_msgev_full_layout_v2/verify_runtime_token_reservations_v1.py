#!/usr/bin/env python3
"""Verify the source-free full-review runtime-name reservation artifact."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
GENERATOR = WORKSTREAM / "generate_runtime_token_reservations_v1.py"
ARTIFACT = WORKSTREAM / "public" / "runtime_token_reservations.v1.json"
DEFAULT_STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")


class VerificationError(ValueError):
    pass


def load_generator() -> Any:
    spec = importlib.util.spec_from_file_location("verify_runtime_reservation_generator", GENERATOR)
    if spec is None or spec.loader is None:
        raise VerificationError("cannot load reservation generator")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def verify(steam_root: Path) -> dict[str, int]:
    generator = load_generator()
    try:
        actual = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise VerificationError("cannot read reservation artifact") from exc
    expected = generator.generate(steam_root)
    if actual != expected:
        raise VerificationError("reservation artifact differs from the pinned full-review source calculation")
    reservations = actual.get("reservations")
    if not isinstance(reservations, dict):
        raise VerificationError("reservation vector is absent")
    forbidden = {"source_name", "source_text", "ko", "jp"}
    for token, row in reservations.items():
        if not isinstance(token, str) or not isinstance(row, dict):
            raise VerificationError("reservation row is malformed")
        if forbidden.intersection(row):
            raise VerificationError("reservation artifact stores source text")
    return {
        "reservations": len(reservations),
        "reviewed_token_rows": int(actual["counts"]["reviewed_runtime_token_rows"]),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--steam-root", type=Path, default=DEFAULT_STEAM_ROOT)
    args = parser.parse_args()
    try:
        report = verify(args.steam_root)
        print("status=PASS")
        print(f"reservations={report['reservations']}")
        print(f"reviewed_token_rows={report['reviewed_token_rows']}")
        print("steam_files_written=False")
        return 0
    except (VerificationError, OSError, ValueError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
