#!/usr/bin/env python3
"""Build and verify the source-free msgire/msgstf Korean overlays.

This workstream deliberately delegates the packed-resource validation,
message-table rebuild, wrapper recompression, manifest generation, and recipe
generation to the repository's existing ``build_common_message_overlay``
builder.  The shared builder currently has a conservative two-resource allow
list, so this wrapper extends it only for the two audited small tables and
restores the original allow list before returning.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import tempfile
from pathlib import Path
from typing import Any, Sequence


REPO_ROOT = Path(__file__).resolve().parents[2]
TOOLS_ROOT = REPO_ROOT / "tools"
sys.path.insert(0, str(TOOLS_ROOT))

import build_common_message_overlay as common  # noqa: E402
from nobu16_lz4 import decompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table  # noqa: E402


WORKSTREAM_ROOT = Path(__file__).resolve().parent
PUBLIC_ROOT = WORKSTREAM_ROOT / "public"
OVERLAY_PATHS = (
    PUBLIC_ROOT / "msgire_ko_0000_0121.v0.1.json",
    PUBLIC_ROOT / "msgstf_ko_0000_0007.v0.1.json",
)
SUPPORTED_RESOURCES = frozenset(
    {
        "MSG_PK/SC/msgire.bin",
        "MSG_PK/SC/msgstf.bin",
    }
)
EXPECTED = {
    "MSG_PK/SC/msgire.bin": {
        "string_count": 122,
        "translation_target_count": 122,
        "translated_ids": list(range(122)),
        "structural_empty_ids": [],
    },
    "MSG_PK/SC/msgstf.bin": {
        "string_count": 20,
        "translation_target_count": 8,
        "translated_ids": list(range(8)),
        "structural_empty_ids": list(range(8, 20)),
    },
}
FORBIDDEN_SOURCE_SCRIPT_RE = re.compile(
    r"[\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF\u3040-\u30FF]"
)
ALLOWED_ROOT_KEYS = {
    "base_language",
    "defaults",
    "distribution_policy",
    "entries",
    "entry_count",
    "overlay_id",
    "resource",
    "schema",
    "stock_sc",
}
ALLOWED_ENTRY_KEYS = {
    "allow_edge_whitespace_change",
    "id",
    "ko",
    "source_sc_utf16le_sha256",
    "status",
}


class SmallTableError(ValueError):
    """Raised when this workstream's narrow public contract is violated."""


def sha256_bytes(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def _load_overlay(path: Path) -> tuple[dict[str, Any], bytes]:
    overlay, blob = common.load_json_strict(path)
    resource = overlay.get("resource")
    if resource not in SUPPORTED_RESOURCES:
        raise SmallTableError(
            f"{path.name}: resource must be one of {sorted(SUPPORTED_RESOURCES)!r}"
        )
    if set(overlay) != ALLOWED_ROOT_KEYS:
        raise SmallTableError(f"{path.name}: unexpected public root keys")
    if overlay.get("distribution_policy") != {
        "contains_commercial_source_text": False,
        "contains_complete_game_resource": False,
    }:
        raise SmallTableError(f"{path.name}: invalid distribution policy")
    entries = overlay.get("entries")
    if not isinstance(entries, list):
        raise SmallTableError(f"{path.name}: entries must be an array")
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict) or not set(entry) <= ALLOWED_ENTRY_KEYS:
            raise SmallTableError(f"{path.name}: invalid entry keys at {index}")
        ko = entry.get("ko")
        if not isinstance(ko, str):
            raise SmallTableError(f"{path.name}: entry {index} ko must be text")
        if FORBIDDEN_SOURCE_SCRIPT_RE.search(ko):
            raise SmallTableError(
                f"{path.name}: entry {index} contains a Han or kana source character"
            )
    return overlay, blob


def validate_public_overlays() -> list[dict[str, Any]]:
    """Validate the source-free shape without requiring installed game data."""
    original_allowlist = common.ALLOWED_RESOURCES
    common.ALLOWED_RESOURCES = original_allowlist | SUPPORTED_RESOURCES
    try:
        summaries: list[dict[str, Any]] = []
        seen_resources: set[str] = set()
        for path in OVERLAY_PATHS:
            overlay, blob = _load_overlay(path)
            resource, _, entries = common.validate_overlay_shape(overlay)
            if resource in seen_resources:
                raise SmallTableError(f"duplicate resource overlay: {resource}")
            seen_resources.add(resource)
            expected = EXPECTED[resource]
            ids = [int(entry["id"]) for entry in entries]
            if ids != expected["translated_ids"]:
                raise SmallTableError(f"{path.name}: translated id set is incomplete")
            if len(entries) != expected["translation_target_count"]:
                raise SmallTableError(f"{path.name}: target denominator changed")
            summaries.append(
                {
                    "overlay": path.relative_to(REPO_ROOT).as_posix(),
                    "overlay_sha256": sha256_bytes(blob),
                    "resource": resource,
                    "translated_count": len(entries),
                    "translation_target_count": expected[
                        "translation_target_count"
                    ],
                    "total_string_slots": expected["string_count"],
                    "structural_empty_ids": expected["structural_empty_ids"],
                }
            )
        if seen_resources != SUPPORTED_RESOURCES:
            raise SmallTableError("both audited resources must have exactly one overlay")
        return sorted(summaries, key=lambda item: item["resource"])
    finally:
        common.ALLOWED_RESOURCES = original_allowlist


def build_one(
    game_root: Path, overlay_path: Path, output_root: Path
) -> dict[str, Any]:
    """Build one audited overlay through the shared common-message builder."""
    overlay, _ = _load_overlay(overlay_path)
    resource = str(overlay["resource"])
    original_allowlist = common.ALLOWED_RESOURCES
    common.ALLOWED_RESOURCES = original_allowlist | SUPPORTED_RESOURCES
    try:
        result = common.build_overlay(game_root, overlay_path, output_root)
    finally:
        common.ALLOWED_RESOURCES = original_allowlist
    return {"resource": resource, **result}


def build_all(game_root: Path, output_root: Path) -> list[dict[str, Any]]:
    validate_public_overlays()
    return [
        build_one(game_root, overlay_path, output_root)
        for overlay_path in OVERLAY_PATHS
    ]


def _relative_file_map(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def verify(game_root: Path) -> dict[str, Any]:
    """Run stock alignment, invariant, round-trip, and A/B determinism checks."""
    public_summaries = validate_public_overlays()
    stock_before: dict[str, str] = {}
    source_checks: dict[str, dict[str, Any]] = {}
    for summary in public_summaries:
        resource = str(summary["resource"])
        expected = EXPECTED[resource]
        resource_name = Path(resource).name
        reference_languages: dict[str, dict[str, Any]] = {}
        for language in ("SC", "EN", "JP"):
            reference_resource = f"MSG_PK/{language}/{resource_name}"
            stock_path = game_root / Path(reference_resource)
            packed = stock_path.read_bytes()
            stock_before[reference_resource] = sha256_bytes(packed)
            _, raw = decompress_wrapper(packed)
            table = parse_message_table(raw)
            nonempty_ids = [
                entry_id for entry_id, text in enumerate(table.texts) if text != ""
            ]
            if table.string_count != expected["string_count"]:
                raise SmallTableError(
                    f"{reference_resource}: unexpected string count"
                )
            if nonempty_ids != expected["translated_ids"]:
                raise SmallTableError(
                    f"{reference_resource}: non-empty target ids changed"
                )
            actual_empty = [
                entry_id for entry_id, text in enumerate(table.texts) if text == ""
            ]
            if actual_empty != expected["structural_empty_ids"]:
                raise SmallTableError(
                    f"{reference_resource}: structural empty ids changed"
                )
            reference_languages[language] = {
                "packed_sha256": sha256_bytes(packed),
                "raw_sha256": sha256_bytes(raw),
                "total_string_slots": table.string_count,
                "display_nonempty_count": len(nonempty_ids),
            }
        sc_check = reference_languages["SC"]
        source_checks[resource] = {
            "packed_sha256": sc_check["packed_sha256"],
            "raw_sha256": sc_check["raw_sha256"],
            "total_string_slots": expected["string_count"],
            "display_nonempty_count": expected["translation_target_count"],
            "structural_empty_ids": expected["structural_empty_ids"],
            "reference_languages": reference_languages,
        }

    with tempfile.TemporaryDirectory(prefix="nobu16-small-a-") as first_tmp:
        with tempfile.TemporaryDirectory(prefix="nobu16-small-b-") as second_tmp:
            first_root = Path(first_tmp)
            second_root = Path(second_tmp)
            first_results = build_all(game_root, first_root)
            second_results = build_all(game_root, second_root)
            first_files = _relative_file_map(first_root)
            second_files = _relative_file_map(second_root)
            if first_files != second_files:
                raise SmallTableError("A/B builds are not byte-identical")
            artifact_summaries = [
                {
                    "path": relative,
                    "sha256": sha256_bytes(blob),
                    "size": len(blob),
                }
                for relative, blob in sorted(first_files.items())
            ]
            first_targets = {
                str(result["resource"]): str(result["target_sha256"])
                for result in first_results
            }
            second_targets = {
                str(result["resource"]): str(result["target_sha256"])
                for result in second_results
            }
            if first_targets != second_targets:
                raise SmallTableError("A/B target hashes differ")

    stock_after = {
        resource: sha256_file(game_root / Path(resource))
        for resource in stock_before
    }
    if stock_before != stock_after:
        raise SmallTableError("installed stock resources changed during verification")

    total_translated = sum(
        int(summary["translated_count"]) for summary in public_summaries
    )
    total_targets = sum(
        int(summary["translation_target_count"]) for summary in public_summaries
    )
    return {
        "schema": "nobu16.kr.small-message-validation.v1",
        "file_only": True,
        "installed_game_files_modified": False,
        "process_memory_access": False,
        "registry_modified": False,
        "executable_modified": False,
        "source_text_free_public_overlays": True,
        "han_kana_source_leak_count": 0,
        "shared_common_message_builder_reused": True,
        "control_whitespace_placeholder_invariants": "OK",
        "stock_language_alignment": ["SC", "EN", "JP"],
        "ab_build_byte_identical": True,
        "translated_count": total_translated,
        "translation_target_count": total_targets,
        "resources": public_summaries,
        "source_checks": source_checks,
        "artifacts": artifact_summaries,
    }


def write_validation(game_root: Path, output_path: Path) -> dict[str, Any]:
    report = verify(game_root.resolve())
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(common.encode_json(report))
    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    build = subparsers.add_parser("build", help="build both small-table overlays")
    build.add_argument("--game-root", type=Path, required=True)
    build.add_argument("--output-root", type=Path, required=True)

    validate = subparsers.add_parser(
        "validate-public", help="validate public overlays without game files"
    )

    verify_parser = subparsers.add_parser(
        "verify", help="run live stock checks and write deterministic validation JSON"
    )
    verify_parser.add_argument("--game-root", type=Path, required=True)
    verify_parser.add_argument(
        "--output",
        type=Path,
        default=WORKSTREAM_ROOT / "validation.json",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "validate-public":
            summaries = validate_public_overlays()
            print(f"resources={len(summaries)}")
            print(
                "translated="
                f"{sum(int(item['translated_count']) for item in summaries)}"
            )
            print("source_text_free=True")
            print("han_kana_source_leak_count=0")
        elif args.command == "build":
            results = build_all(args.game_root.resolve(), args.output_root.resolve())
            for result in results:
                print(f"resource={result['resource']}")
                print(f"target_sha256={result['target_sha256']}")
                print(f"overlay_entries={result['overlay_entries']}")
            print("installed_game_files_modified=False")
        elif args.command == "verify":
            report = write_validation(args.game_root, args.output.resolve())
            print(f"output={args.output.resolve()}")
            print(f"translated={report['translated_count']}")
            print(f"targets={report['translation_target_count']}")
            print("ab_build_byte_identical=True")
            print("installed_game_files_modified=False")
        else:
            raise SmallTableError(f"unsupported command: {args.command}")
    except (
        OSError,
        KeyError,
        TypeError,
        ValueError,
        common.CommonMessageOverlayError,
    ) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
