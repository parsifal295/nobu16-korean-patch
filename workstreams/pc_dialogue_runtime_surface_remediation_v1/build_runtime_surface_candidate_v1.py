#!/usr/bin/env python3
"""Apply reviewed runtime-surface overlays and audit the rebuilt candidates."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Sequence


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
DEFAULT_INPUT_ROOT = (
    REPO
    / "tmp"
    / "pc_dialogue_full_retranslation_v0150"
    / "finalizer_preflight_52803"
    / "candidate"
)
DEFAULT_OUTPUT_ROOT = (
    REPO / "tmp" / "pc_dialogue_runtime_surface_remediation_v1" / "candidate"
)
DEFAULT_PRIORITY_OVERLAY = WORKSTREAM / "priority_regressions.overlay.v1.json"

sys.path[:0] = [
    str(REPO / "tools"),
    str(REPO / "workstreams" / "msggame"),
]

from msggame_format import (  # noqa: E402
    iter_literals,
    parse_packed_msggame,
    rebuild_packed_with_literals,
)


SCHEMA = "nobu16.kr.pc-dialogue-runtime-surface-overlay.v1"
RESOURCE_PATHS = {
    "base_msggame": Path("MSG") / "JP" / "msggame.bin",
    "pk_msggame": Path("MSG_PK") / "JP" / "msggame.bin",
}


class RemediationError(ValueError):
    """Raised when an overlay is ambiguous or its source guard has drifted."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RemediationError(message)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def text_sha256(value: str) -> str:
    return sha256_bytes(value.encode("utf-16le"))


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"overlay root must be an object: {path}")
    return value


def load_surface_audit():
    path = (
        REPO
        / "workstreams"
        / "pc_dialogue_runtime_surface_qa_v1"
        / "audit_runtime_surface_v1.py"
    )
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_runtime_surface_audit",
        path,
    )
    require(spec is not None and spec.loader is not None, "audit import failed")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def overlay_entries(
    paths: Iterable[Path],
) -> dict[str, dict[tuple[int, int, int], dict[str, Any]]]:
    result: dict[str, dict[tuple[int, int, int], dict[str, Any]]] = {
        resource: {} for resource in RESOURCE_PATHS
    }
    for path in paths:
        overlay = load_json(path)
        require(
            overlay.get("schema") == SCHEMA,
            f"unsupported overlay schema: {path}",
        )
        entries = overlay.get("entries")
        require(isinstance(entries, list), f"entries must be an array: {path}")
        for ordinal, entry in enumerate(entries, start=1):
            require(
                isinstance(entry, dict),
                f"{path}: entry {ordinal} must be an object",
            )
            resource = entry.get("resource")
            require(
                resource in RESOURCE_PATHS,
                f"{path}: entry {ordinal} has unknown resource",
            )
            values = (
                entry.get("block_id"),
                entry.get("record_id"),
                entry.get("literal_id"),
            )
            require(
                all(isinstance(value, int) and not isinstance(value, bool)
                    and value >= 0 for value in values),
                f"{path}: entry {ordinal} has invalid coordinate",
            )
            coordinate = tuple(values)
            require(
                coordinate not in result[resource],
                f"duplicate overlay coordinate: {resource} {coordinate}",
            )
            require(
                isinstance(entry.get("source_text_utf16le_sha256"), str)
                and len(entry["source_text_utf16le_sha256"]) == 64,
                f"{path}: entry {ordinal} has invalid source hash",
            )
            require(
                isinstance(entry.get("ko"), str),
                f"{path}: entry {ordinal} has no Korean replacement",
            )
            result[resource][coordinate] = entry
    return result


def rebuild_resource(
    source: Path,
    entries: dict[tuple[int, int, int], dict[str, Any]],
) -> tuple[bytes, dict[str, Any]]:
    source_blob = source.read_bytes()
    archive = parse_packed_msggame(source_blob).archive
    literals = {
        (value.block_id, value.record_id, value.literal_id): value.text
        for value in iter_literals(archive)
    }
    replacements: dict[tuple[int, int, int], str] = {}
    for coordinate, entry in entries.items():
        require(
            coordinate in literals,
            f"overlay coordinate is absent: {coordinate}",
        )
        observed = text_sha256(literals[coordinate])
        require(
            observed == entry["source_text_utf16le_sha256"],
            (
                f"source text guard drift at {coordinate}: "
                f"expected={entry['source_text_utf16le_sha256']} "
                f"observed={observed}"
            ),
        )
        replacements[coordinate] = entry["ko"]
    rebuilt = rebuild_packed_with_literals(source_blob, replacements)
    checked = {
        (value.block_id, value.record_id, value.literal_id): value.text
        for value in iter_literals(parse_packed_msggame(rebuilt).archive)
    }
    require(
        all(checked[coordinate] == value for coordinate, value in replacements.items()),
        f"rebuilt literal mismatch: {source}",
    )
    return rebuilt, {
        "source_sha256": sha256_bytes(source_blob),
        "candidate_sha256": sha256_bytes(rebuilt),
        "replacement_count": len(replacements),
    }


def build(
    input_root: Path,
    output_root: Path,
    overlay_paths: Sequence[Path],
) -> dict[str, Any]:
    entries = overlay_entries(overlay_paths)
    metadata: dict[str, Any] = {}
    output_paths: dict[str, Path] = {}
    for resource, relative in RESOURCE_PATHS.items():
        source = input_root / relative
        require(source.is_file(), f"candidate input is absent: {source}")
        rebuilt, item = rebuild_resource(source, entries[resource])
        destination = output_root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(rebuilt)
        require(destination.read_bytes() == rebuilt, f"write drift: {destination}")
        metadata[resource] = item
        output_paths[resource] = destination

    audit = load_surface_audit()
    audits = tuple(
        audit.audit_resource(resource, output_paths[resource])
        for resource in RESOURCE_PATHS
    )
    surface = audit.report(audits)
    return {
        "schema": "nobu16.kr.pc-dialogue-runtime-surface-remediation-build.v1",
        "status": surface["status"],
        "overlay_count": len(overlay_paths),
        "replacement_count": sum(
            item["replacement_count"] for item in metadata.values()
        ),
        "resources": metadata,
        "surface_audit": {
            "status": surface["status"],
            "issue_count": surface["issue_count"],
            "category_counts": surface["category_counts"],
            "resource_issue_counts": {
                resource: surface["resources"][resource]["issue_count"]
                for resource in RESOURCE_PATHS
            },
        },
        "steam_write_performed": False,
    }


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-root", type=Path, default=DEFAULT_INPUT_ROOT)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument(
        "--overlay",
        type=Path,
        action="append",
        default=None,
        help="reviewed overlay; may be supplied more than once",
    )
    parser.add_argument(
        "--allow-remaining",
        action="store_true",
        help="write an intermediate candidate even when the surface gate fails",
    )
    args = parser.parse_args(argv)
    overlays = args.overlay or [DEFAULT_PRIORITY_OVERLAY]
    report = build(args.input_root, args.output_root, overlays)
    report_path = args.output_root / "runtime_surface_build.source_free.v1.json"
    report_path.write_text(canonical_json(report), encoding="utf-8")
    print(
        json.dumps(
            {
                "status": report["status"],
                "replacement_count": report["replacement_count"],
                "surface_audit": report["surface_audit"],
                "report": str(report_path.resolve()),
            },
            ensure_ascii=True,
            sort_keys=True,
        )
    )
    if report["status"] != "PASS" and not args.allow_remaining:
        return 1
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, RemediationError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
