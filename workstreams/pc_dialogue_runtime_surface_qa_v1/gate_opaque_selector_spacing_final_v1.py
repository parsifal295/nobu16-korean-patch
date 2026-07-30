#!/usr/bin/env python3
"""Release-blocking Base/PK gate for opaque selector right spacing."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
AUDIT_PATH = WORKSTREAM / "audit_opaque_person_selector_spacing_v1.py"
SCHEMA = "nobu16.kr.opaque-selector-spacing-final-gate.v1"
RELEASE_TARGET = "0.15.0"


def load_module(name: str, path: Path) -> Any:
    specification = importlib.util.spec_from_file_location(name, path)
    if specification is None or specification.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


AUDIT = load_module(
    "opaque_selector_spacing_final_gate_audit_v1",
    AUDIT_PATH,
)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def build_gate(
    resources: Sequence[Any],
) -> dict[str, Any]:
    report = AUDIT.build_report(resources)
    source_free = bool(
        report["audit_contract"]["source_or_translation_bodies_omitted"]
    )
    passed = report["issue_count"] == 0 and source_free
    return {
        "schema": SCHEMA,
        "status": "PASS" if passed else "FAIL",
        "release_target": RELEASE_TARGET,
        "runtime_completion": "PASS" if passed else "FAIL",
        "runtime_completion_allowed": passed,
        "issue_count": report["issue_count"],
        "category_counts": report["category_counts"],
        "resources": report["resources"],
        "issues": report["issues"],
        "source_or_translation_bodies_omitted": source_free,
        "audit_contract": {
            "schema": report["schema"],
            "engine_sha256": sha256_bytes(AUDIT_PATH.read_bytes()),
            **report["audit_contract"],
        },
        "steam_write_performed": False,
    }


def canonical_json(value: Mapping[str, Any]) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    ) + "\n"


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, default=AUDIT.DEFAULT_BASE)
    parser.add_argument("--pk", type=Path, default=AUDIT.DEFAULT_PK)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    resources = (
        AUDIT.audit_resource("base_msggame", args.base),
        AUDIT.audit_resource("pk_msggame", args.pk),
    )
    gate = build_gate(resources)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        canonical_json(gate),
        encoding="utf-8",
        newline="\n",
    )
    print(
        json.dumps(
            {
                "schema": SCHEMA,
                "status": gate["status"],
                "issue_count": gate["issue_count"],
                "resources": {
                    resource.resource: {
                        "sha256": resource.sha256,
                        "issue_count": len(resource.issues),
                    }
                    for resource in resources
                },
                "output": str(args.output.resolve()),
            },
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        )
    )
    return 0 if gate["status"] == "PASS" else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, AUDIT.OpaqueSelectorSpacingError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
