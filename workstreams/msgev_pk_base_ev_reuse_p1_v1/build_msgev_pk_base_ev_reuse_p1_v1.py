#!/usr/bin/env python3
"""Build P1-01 active-JP ``msgev`` residuals from source-hash twins.

The PK event resource duplicates many lines from the already-translated base
event resource.  This builder transfers Korean only when the active JP source
UTF-16LE hash is exactly equal to a source-free base-event overlay entry; the
three unmatched rows use project-authored Korean.  It rebuilds a private
candidate from the deterministic Wave09 JP baseline and never writes Steam,
GitHub, or release files.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import shutil
import sys
from pathlib import Path
from typing import Any, Iterable


sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))

from manual_translations import MANUAL_KO


def import_file(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import prerequisite: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


WAVE09_PATH = REPO / "workstreams" / "msgev_steam_jp_residual_wave09" / "build_msgev_steam_jp_residual_wave09.py"
# Wave09 intentionally imports its sibling ``translations`` module by its
# historical short name.  Keep this workstream's manual payload under a
# distinct module name and isolate Wave09's sibling import deterministically.
sys.modules.pop("translations", None)
sys.path.insert(0, str(WAVE09_PATH.parent))
try:
    WAVE09 = import_file("msgev_pk_base_ev_reuse_p1_wave09", WAVE09_PATH)
finally:
    sys.path.remove(str(WAVE09_PATH.parent))
COMMON = WAVE09.COMMON

RESOURCE = "MSG_PK/JP/msgev.bin"
AUDIT_PATH = REPO / "workstreams" / "jp_active_message_residual_audit_v1" / "validation.active_steam.v1.json"
BASE_OVERLAYS = (
    REPO
    / "workstreams"
    / "base_ev_strdata_jp_switch_v13_transfer_v1"
    / "public"
    / "ev_strdata_ko_base_jp_switch_v13_transfer_13045.v1.json",
    REPO
    / "workstreams"
    / "base_ev_strdata_jp_residual_wave11"
    / "public"
    / "ev_strdata_ko_base_jp_residual_wave11_40.v1.json",
)
OVERLAY_PATH = HERE / "public" / "msgev_ko_pk_base_ev_reuse_p1_185.v1.json"
VALIDATION_PATH = HERE / "validation.v1.json"
DEFAULT_STOCK_ROOT = WAVE09.DEFAULT_STOCK_ROOT
DEFAULT_OUTPUT_ROOT = REPO / "tmp" / "msgev_pk_base_ev_reuse_p1_candidate"

SCHEMA = "nobu16.kr.msgev-pk-base-ev-reuse-p1-overlay.v1"
VALIDATION_SCHEMA = "nobu16.kr.msgev-pk-base-ev-reuse-p1-validation.v1"
PRIVATE_SCHEMA = "nobu16.kr.msgev-pk-base-ev-reuse-p1-private-candidate.v1"
BUNDLE_ID = "p1-MSG_PK_JP_msgev-01"
BASELINE_PIN = {
    "size": 1_040_799,
    "sha256": "A8835C3520B29A076A21014E17B17D7AAABF4AC99D37D65C891415AC17BBF3F5",
    "packed_sha256": "A8835C3520B29A076A21014E17B17D7AAABF4AC99D37D65C891415AC17BBF3F5",
    "raw_size": 1_036_708,
    "raw_sha256": "6D87086EA6B533EAB3F3745DB7564E8D7842E7DD603AD765B2D6D900644E00FB",
    "string_count": 17_916,
}
EXPECTED_ENTRY_COUNT = 185
EXPECTED_REUSED_COUNT = 182
EXPECTED_MANUAL_IDS = (2356, 3643, 3767)
OUTPUT_CANDIDATE_PIN: dict[str, Any] | None = {
    "size": 1_044_554,
    "sha256": "7519E2E1DD68A43966AAE7A3FF5B44EEF2C513F298913B3ABDF964B7FB1AF2BD",
    "packed_sha256": "7519E2E1DD68A43966AAE7A3FF5B44EEF2C513F298913B3ABDF964B7FB1AF2BD",
    "raw_size": 1_040_448,
    "raw_sha256": "1F681172CD2130D4F2E88C3575110A41C3908D6B8B4744C910C4ED544DDDDBFE",
    "string_count": 17_916,
}

HANGUL_RE = re.compile(r"[\uAC00-\uD7A3]")
JAPANESE_RE = re.compile(r"[\u3040-\u30FF\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF]")


class ReuseP1Error(ValueError):
    """Raised when an input pin, reuse rule, or binary invariant differs."""


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def text_hash(text: str) -> str:
    return sha256(text.encode("utf-16-le"))


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def strict_json(path: Path) -> tuple[dict[str, Any], bytes]:
    blob = path.read_bytes()
    try:
        value = json.loads(blob.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ReuseP1Error(f"invalid JSON: {path}") from exc
    if not isinstance(value, dict):
        raise ReuseP1Error(f"JSON root is not an object: {path}")
    return value, blob


def ids_hash(ids: Iterable[int]) -> str:
    return sha256(
        json.dumps(
            [{"id": item} for item in ids],
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    )


def load_bundle_ids() -> tuple[list[int], str]:
    audit, _blob = strict_json(AUDIT_PATH)
    bundles = audit.get("recommended_parallel_bundles")
    if not isinstance(bundles, list):
        raise ReuseP1Error("residual audit bundles are missing")
    candidates = [item for item in bundles if isinstance(item, dict) and item.get("bundle_id") == BUNDLE_ID]
    if len(candidates) != 1:
        raise ReuseP1Error("P1 msgev bundle is absent or ambiguous")
    bundle = candidates[0]
    if (
        bundle.get("resource") != RESOURCE
        or bundle.get("format") != "common"
        or bundle.get("coordinate_count") != EXPECTED_ENTRY_COUNT
        or bundle.get("classification") != "japanese_kana_no_hangul"
    ):
        raise ReuseP1Error("P1 msgev bundle contract differs")
    coordinates = bundle.get("coordinates")
    if not isinstance(coordinates, list):
        raise ReuseP1Error("P1 msgev coordinates are absent")
    ids = [item.get("id") for item in coordinates if isinstance(item, dict)]
    if len(ids) != EXPECTED_ENTRY_COUNT or any(type(item) is not int for item in ids):
        raise ReuseP1Error("P1 msgev IDs are malformed")
    if len(set(ids)) != len(ids) or ids != sorted(ids):
        raise ReuseP1Error("P1 msgev IDs are not sorted and unique")
    actual_hash = ids_hash(ids)
    if bundle.get("coordinate_sha256") != actual_hash:
        raise ReuseP1Error("P1 msgev coordinate hash differs")
    return ids, actual_hash


def source_free_reference_map() -> dict[str, str]:
    """Return one canonical Korean text for each exact base-event source hash."""
    values: dict[str, set[str]] = {}
    for path in BASE_OVERLAYS:
        overlay, _blob = strict_json(path)
        entries = overlay.get("entries")
        if not isinstance(entries, list):
            raise ReuseP1Error(f"base-event entries missing: {path}")
        for entry in entries:
            if not isinstance(entry, dict):
                raise ReuseP1Error("base-event entry is not an object")
            source_hash = entry.get("source_jp_utf16le_sha256")
            korean = entry.get("ko")
            if not (
                isinstance(source_hash, str)
                and len(source_hash) == 64
                and isinstance(korean, str)
                and "\0" not in korean
                and HANGUL_RE.search(korean)
                and not JAPANESE_RE.search(korean)
            ):
                raise ReuseP1Error("base-event overlay entry violates source-free Korean contract")
            values.setdefault(source_hash, set()).add(korean)
    ambiguous = [key for key, value in values.items() if len(value) != 1]
    if ambiguous:
        raise ReuseP1Error("same JP source hash has conflicting base-event Korean")
    return {key: next(iter(value)) for key, value in values.items()}


def build_baseline(stock_root: Path) -> tuple[bytes, Any, Any]:
    packed, metrics = WAVE09.build_blob(stock_root)
    candidate = metrics.get("candidate")
    if candidate != BASELINE_PIN or WAVE09.packed_spec(packed) != BASELINE_PIN:
        raise ReuseP1Error("Wave09 deterministic baseline pin differs")
    _header, raw = COMMON.decompress_wrapper(packed)
    table = COMMON.parse_message_table(raw)
    if table.string_count != BASELINE_PIN["string_count"]:
        raise ReuseP1Error("baseline string count differs")
    return packed, raw, table


def replacements(stock_root: Path = DEFAULT_STOCK_ROOT) -> tuple[dict[int, str], dict[str, Any]]:
    ids, vector_hash = load_bundle_ids()
    packed, _raw, table = build_baseline(stock_root)
    del packed
    reference = source_free_reference_map()
    result: dict[int, str] = {}
    reused = 0
    manual = 0
    for entry_id in ids:
        if not 0 <= entry_id < table.string_count:
            raise ReuseP1Error(f"ID outside msgev table: {entry_id}")
        source = table.texts[entry_id]
        source_hash = text_hash(source)
        korean = reference.get(source_hash)
        origin = "base_ev_exact_source_hash"
        if korean is None:
            korean = MANUAL_KO.get(entry_id)
            origin = "project_authored_manual"
        if not isinstance(korean, str):
            raise ReuseP1Error(f"unresolved P1 msgev row: {entry_id}")
        if entry_id in MANUAL_KO:
            manual += 1
            if source_hash in reference:
                raise ReuseP1Error(f"manual row unexpectedly has a base-event twin: {entry_id}")
        else:
            reused += 1
            if origin != "base_ev_exact_source_hash":
                raise ReuseP1Error(f"non-manual row lacks a base-event twin: {entry_id}")
        if not HANGUL_RE.search(korean) or JAPANESE_RE.search(korean):
            raise ReuseP1Error(f"Korean script contract differs: {entry_id}")
        mismatches = COMMON.common.invariant_mismatches(source, korean)
        if mismatches:
            raise ReuseP1Error(f"format invariant differs at {entry_id}: {mismatches}")
        result[entry_id] = korean
    if tuple(sorted(MANUAL_KO)) != EXPECTED_MANUAL_IDS or manual != len(EXPECTED_MANUAL_IDS):
        raise ReuseP1Error("manual-row contract differs")
    if len(result) != EXPECTED_ENTRY_COUNT or reused != EXPECTED_REUSED_COUNT:
        raise ReuseP1Error("P1 reuse accounting differs")
    return result, {
        "ids": ids,
        "ids_sha256": vector_hash,
        "reused_exact_source_hash_count": reused,
        "project_authored_manual_count": manual,
    }


def expected_overlay(stock_root: Path = DEFAULT_STOCK_ROOT) -> dict[str, Any]:
    target, metadata = replacements(stock_root)
    _packed, _raw, table = build_baseline(stock_root)
    entries = [
        {
            "id": entry_id,
            "source_jp_utf16le_sha256": text_hash(table.texts[entry_id]),
            "ko": target[entry_id],
            "ko_utf16le_sha256": text_hash(target[entry_id]),
            "origin": (
                "project_authored_manual"
                if entry_id in MANUAL_KO
                else "base_ev_exact_source_hash"
            ),
        }
        for entry_id in metadata["ids"]
    ]
    return {
        "schema": SCHEMA,
        "overlay_id": "msgev_ko_pk_base_ev_reuse_p1_185.v1",
        "resource": RESOURCE,
        "base_language": "JP",
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
        },
        "baseline": {"workstream": "msgev_steam_jp_residual_wave09", "candidate": BASELINE_PIN},
        "selection": {
            "bundle_id": BUNDLE_ID,
            "entry_count": len(entries),
            "ids_sha256": metadata["ids_sha256"],
            "reused_exact_source_hash_count": metadata["reused_exact_source_hash_count"],
            "project_authored_manual_count": metadata["project_authored_manual_count"],
            "format_invariants_required": True,
            "active_jp_hash_gate_required": True,
        },
        "entries": entries,
    }


def build_blob(stock_root: Path = DEFAULT_STOCK_ROOT) -> tuple[bytes, dict[str, Any]]:
    baseline, _raw, table = build_baseline(stock_root)
    target, metadata = replacements(stock_root)
    texts = list(table.texts)
    for entry_id, korean in target.items():
        texts[entry_id] = korean
    rebuilt_raw = COMMON.rebuild_message_table(table, texts)
    reparsed = COMMON.parse_message_table(rebuilt_raw)
    if reparsed.texts != tuple(texts):
        raise ReuseP1Error("reparsed texts differ")
    if not COMMON._opaque_structure_preserved(table, reparsed, rebuilt_raw):
        raise ReuseP1Error("opaque table structure changed")
    for entry_id, prior in enumerate(table.texts):
        if entry_id not in target and reparsed.texts[entry_id] != prior:
            raise ReuseP1Error(f"non-target text changed: {entry_id}")
    candidate = COMMON.recompress_wrapper(rebuilt_raw, baseline)
    _header, roundtrip = COMMON.decompress_wrapper(candidate)
    if roundtrip != rebuilt_raw or candidate[:8] != baseline[:8]:
        raise ReuseP1Error("wrapper round-trip or prefix differs")
    parsed_candidate = COMMON.parse_message_table(roundtrip)
    for entry_id, korean in target.items():
        if parsed_candidate.texts[entry_id] != korean:
            raise ReuseP1Error(f"target Korean differs: {entry_id}")
    spec = WAVE09.packed_spec(candidate)
    if OUTPUT_CANDIDATE_PIN is not None and spec != OUTPUT_CANDIDATE_PIN:
        raise ReuseP1Error("P1 output candidate pin differs")
    return candidate, {
        "resource": RESOURCE,
        "baseline": BASELINE_PIN,
        "candidate": spec,
        "entry_count": len(target),
        "ids_sha256": metadata["ids_sha256"],
        "reused_exact_source_hash_count": metadata["reused_exact_source_hash_count"],
        "project_authored_manual_count": metadata["project_authored_manual_count"],
        "non_target_texts_preserved": True,
        "opaque_non_string_metadata_preserved": True,
        "wrapper_prefix_preserved": True,
        "format_invariants_preserved": True,
        "candidate_written": False,
        "installed_game_files_modified": False,
    }


def validation_model(metrics: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": VALIDATION_SCHEMA,
        "status": "PASS",
        "resource": RESOURCE,
        "translation": {
            "entry_count": metrics["entry_count"],
            "ids_sha256": metrics["ids_sha256"],
            "reused_exact_source_hash_count": metrics["reused_exact_source_hash_count"],
            "project_authored_manual_count": metrics["project_authored_manual_count"],
        },
        "expected": {"baseline": BASELINE_PIN, "candidate": metrics["candidate"]},
        "proofs": {
            "deterministic_ab_equal": True,
            "active_jp_hash_gate_required": True,
            "format_invariants_preserved": metrics["format_invariants_preserved"],
            "non_target_texts_preserved": metrics["non_target_texts_preserved"],
            "opaque_non_string_metadata_preserved": metrics["opaque_non_string_metadata_preserved"],
            "wrapper_prefix_preserved": metrics["wrapper_prefix_preserved"],
        },
        "safety": {
            "complete_candidate_binary_tracked": False,
            "installed_game_files_modified": metrics["installed_game_files_modified"],
            "sc_binary_used": False,
            "source_text_embedded": False,
        },
    }


def generate(stock_root: Path = DEFAULT_STOCK_ROOT) -> dict[str, Any]:
    overlay = expected_overlay(stock_root)
    OVERLAY_PATH.parent.mkdir(parents=True, exist_ok=True)
    OVERLAY_PATH.write_bytes(canonical_bytes(overlay))
    first, metrics = build_blob(stock_root)
    second, second_metrics = build_blob(stock_root)
    if first != second or metrics != second_metrics:
        raise ReuseP1Error("deterministic A/B candidate differs")
    VALIDATION_PATH.write_bytes(canonical_bytes(validation_model(metrics)))
    return metrics


def verify(stock_root: Path = DEFAULT_STOCK_ROOT) -> dict[str, Any]:
    if OUTPUT_CANDIDATE_PIN is None:
        raise ReuseP1Error("output candidate pin is not committed")
    expected = expected_overlay(stock_root)
    overlay, blob = strict_json(OVERLAY_PATH)
    if overlay != expected or blob != canonical_bytes(expected):
        raise ReuseP1Error("tracked overlay differs")
    first, metrics = build_blob(stock_root)
    second, second_metrics = build_blob(stock_root)
    if first != second or metrics != second_metrics:
        raise ReuseP1Error("deterministic A/B candidate differs")
    validation, validation_blob = strict_json(VALIDATION_PATH)
    expected_validation = validation_model(metrics)
    if validation != expected_validation or validation_blob != canonical_bytes(expected_validation):
        raise ReuseP1Error("tracked validation differs")
    return {**metrics, "deterministic_ab_equal": True}


def safe_output_root(value: Path) -> Path:
    output = value.resolve()
    tmp = (REPO / "tmp").resolve()
    if output == tmp or tmp not in output.parents or output.exists():
        raise ReuseP1Error(f"unsafe output root: {output}")
    return output


def build(stock_root: Path, output_root: Path) -> Path:
    output = safe_output_root(output_root)
    candidate, metrics = build_blob(stock_root)
    target = output / Path(RESOURCE)
    target.parent.mkdir(parents=True, exist_ok=False)
    target.write_bytes(candidate)
    (output / "private_manifest.json").write_bytes(
        canonical_bytes({"schema": PRIVATE_SCHEMA, "resource": RESOURCE, "candidate": metrics["candidate"]})
    )
    return output


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("generate", "verify", "build"):
        child = commands.add_parser(name)
        child.add_argument("--stock-root", type=Path, default=DEFAULT_STOCK_ROOT)
        if name == "build":
            child.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    args = parser.parse_args(argv)
    if args.command == "generate":
        result = generate(args.stock_root)
    elif args.command == "verify":
        result = verify(args.stock_root)
    else:
        result = {"status": "BUILT", "output_root": str(build(args.stock_root, args.output_root))}
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
