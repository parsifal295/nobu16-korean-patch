#!/usr/bin/env python3
"""Correct the Steam-JP scenario-date month unit without touching duration units.

The v0.7 msgui candidate translated both JP ``%d月`` (calendar month) and
``%dカ月`` (duration in months) as ``%d개월``.  This post-candidate delta
changes only the former, Steam JP msgui ID 1051, to ``%d월``.  It derives the
published source-free overlay and validation from the pristine Steam 1.1.7
JP input and the immutable v0.7 msgui candidate; no SC asset is read.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import shutil
import sys
from pathlib import Path
from typing import Any


sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
V2_PATH = (
    REPO
    / "workstreams"
    / "steam_jp_117_candidate_v2"
    / "build_steam_jp_117_candidate_v2.py"
)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import required module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


V2 = load_module("nobu16_scenario_date_hotfix_v2", V2_PATH)
MSGUI = V2.BASE.MSGUI

SCHEMA = "nobu16.kr.steam-jp-scenario-date-hotfix-overlay.v1"
VALIDATION_SCHEMA = "nobu16.kr.steam-jp-scenario-date-hotfix-validation.v1"
RESOURCE = "MSG_PK/JP/msgui.bin"
ISSUE_NUMBER = 45
ENTRY_ID = 1_051
YEAR_ENTRY_ID = 1_050
DURATION_ENTRY_ID = 1_678
SOURCE_JP_TEXT = "%d月"
SOURCE_JP_HASH = "64D041CB87FA66AB6E106F4DE86C17514A8A404238DAFCB1B91419B9A4D904F7"
BASELINE_KO = "%d개월"
TARGET_KO = "%d월"
YEAR_KO = "%d년"
SCENARIO_DATE_EXAMPLE = "1559년 3월"
OVERLAY_PATH = HERE / "public" / "msgui_ko_steam_jp_scenario_date_month.v1.json"
VALIDATION_PATH = HERE / "validation.v1.json"
DEFAULT_STOCK_ROOT = V2.STOCK_ROOT
DEFAULT_OUTPUT_ROOT = REPO / "tmp" / "steam_jp_scenario_date_hotfix_v1_candidate"


class ScenarioDateHotfixError(ValueError):
    """A Steam source, candidate baseline, or one-entry delta diverged."""


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def path_spec(path: Path) -> dict[str, Any]:
    blob = path.read_bytes()
    return {"size": len(blob), "sha256": sha256(blob)}


def pretty_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(
        "utf-8"
    )


def strict_json(path: Path) -> tuple[dict[str, Any], bytes]:
    blob = path.read_bytes()
    value = json.loads(blob.decode("utf-8"))
    if not isinstance(value, dict):
        raise ScenarioDateHotfixError(f"JSON root is not an object: {path}")
    return value, blob


def baseline_blob(stock_root: Path) -> tuple[bytes, dict[str, Any]]:
    baseline, metadata = V2.build_msgui(stock_root)
    expected = V2.load_tracked_verification()["candidates"][RESOURCE]
    observed = {"size": len(baseline), "sha256": sha256(baseline)}
    if observed != expected:
        raise ScenarioDateHotfixError(
            f"v0.7 msgui baseline pin changed: {observed} != {expected}"
        )
    return baseline, metadata


def expected_overlay(stock_root: Path) -> dict[str, Any]:
    _path, _packed, _raw, stock = MSGUI.load_stock(stock_root)
    baseline, _metadata = baseline_blob(stock_root)
    _wrapper, baseline_raw = V2.BASE.decompress_wrapper(baseline)
    baseline_table = MSGUI.parse_message_table(baseline_raw)

    source = stock.texts[ENTRY_ID]
    if source != SOURCE_JP_TEXT or MSGUI.text_hash(source) != SOURCE_JP_HASH:
        raise ScenarioDateHotfixError("Steam JP calendar-month source differs")
    if baseline_table.texts[ENTRY_ID] != BASELINE_KO:
        raise ScenarioDateHotfixError("v0.7 calendar-month baseline differs")
    if baseline_table.texts[YEAR_ENTRY_ID] != YEAR_KO:
        raise ScenarioDateHotfixError("v0.7 year-unit anchor differs")
    if baseline_table.texts[DURATION_ENTRY_ID] != BASELINE_KO:
        raise ScenarioDateHotfixError("v0.7 duration-month anchor differs")

    entry = {
        "id": ENTRY_ID,
        "source_jp_utf16le_sha256": MSGUI.text_hash(source),
        "baseline_ko_utf16le_sha256": MSGUI.text_hash(baseline_table.texts[ENTRY_ID]),
        "ko": TARGET_KO,
        "ko_utf16le_sha256": MSGUI.text_hash(TARGET_KO),
    }
    return {
        "schema": SCHEMA,
        "overlay_id": "msgui_ko_steam_jp_scenario_date_month.v1",
        "issue": ISSUE_NUMBER,
        "resource": RESOURCE,
        "base_language": "JP",
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
        },
        "stock_jp": MSGUI.stock_spec(),
        "baseline": {
            "candidate": V2.load_tracked_verification()["candidates"][RESOURCE],
            "builder": "steam_jp_msgui_v1+wave07_recovery",
        },
        "entry_count": 1,
        "entries": [entry],
        "regression_anchors": {
            "year_entry_id": YEAR_ENTRY_ID,
            "year_ko_utf16le_sha256": MSGUI.text_hash(YEAR_KO),
            "calendar_month_entry_id": ENTRY_ID,
            "duration_month_entry_id": DURATION_ENTRY_ID,
            "duration_ko_utf16le_sha256": MSGUI.text_hash(BASELINE_KO),
        },
        "safety": {
            "current_jp_source_hashes_fail_closed": True,
            "baseline_ko_hashes_fail_closed": True,
            "sc_binary_used": False,
            "sc_runtime_path_used": False,
        },
    }


def load_overlay(stock_root: Path) -> tuple[dict[str, Any], bytes]:
    value, blob = strict_json(OVERLAY_PATH)
    expected = expected_overlay(stock_root)
    if value != expected or blob != pretty_bytes(expected):
        raise ScenarioDateHotfixError("tracked date-hotfix overlay differs from model")
    return value, blob


def build_blob(stock_root: Path) -> tuple[bytes, dict[str, Any]]:
    overlay, overlay_blob = load_overlay(stock_root)
    _path, _stock_packed, _stock_raw, stock = MSGUI.load_stock(stock_root)
    baseline, baseline_metadata = baseline_blob(stock_root)
    wrapper, baseline_raw = V2.BASE.decompress_wrapper(baseline)
    baseline_table = MSGUI.parse_message_table(baseline_raw)
    texts = list(baseline_table.texts)
    changed: set[int] = set()

    for entry in overlay["entries"]:
        entry_id = int(entry["id"])
        source = stock.texts[entry_id]
        current = texts[entry_id]
        if MSGUI.text_hash(source) != entry["source_jp_utf16le_sha256"]:
            raise ScenarioDateHotfixError(f"Steam JP source hash differs at {entry_id}")
        if MSGUI.text_hash(current) != entry["baseline_ko_utf16le_sha256"]:
            raise ScenarioDateHotfixError(f"baseline Korean hash differs at {entry_id}")
        if source != SOURCE_JP_TEXT or current != BASELINE_KO or entry["ko"] != TARGET_KO:
            raise ScenarioDateHotfixError("calendar-month delta contract differs")
        texts[entry_id] = str(entry["ko"])
        changed.add(entry_id)

    if changed != {ENTRY_ID}:
        raise ScenarioDateHotfixError(f"unexpected target coordinates: {sorted(changed)}")
    if texts[YEAR_ENTRY_ID] != YEAR_KO or texts[ENTRY_ID] != TARGET_KO:
        raise ScenarioDateHotfixError("scenario date composition anchors differ")
    if texts[DURATION_ENTRY_ID] != BASELINE_KO:
        raise ScenarioDateHotfixError("duration month was changed by calendar fix")

    rebuilt_raw = MSGUI.rebuild_message_table(baseline_table, texts)
    reparsed = MSGUI.parse_message_table(rebuilt_raw)
    if reparsed.texts != tuple(texts):
        raise ScenarioDateHotfixError("rebuilt date-hotfix table differs")
    if len(reparsed.texts) != len(baseline_table.texts):
        raise ScenarioDateHotfixError("string-domain length changed")
    for entry_id, text in enumerate(baseline_table.texts):
        if entry_id not in changed and reparsed.texts[entry_id] != text:
            raise ScenarioDateHotfixError(f"non-target text changed at {entry_id}")

    candidate = V2.BASE.recompress_wrapper(rebuilt_raw, wrapper)
    _roundtrip_header, roundtrip = V2.BASE.decompress_wrapper(candidate)
    if roundtrip != rebuilt_raw or candidate[:8] != baseline[:8]:
        raise ScenarioDateHotfixError("date-hotfix wrapper round-trip differs")
    return candidate, {
        "resource": RESOURCE,
        "baseline": {"size": len(baseline), "sha256": sha256(baseline)},
        "entry_count": len(changed),
        "candidate": {
            "size": len(candidate),
            "sha256": sha256(candidate),
            "raw_size": len(rebuilt_raw),
            "raw_sha256": sha256(rebuilt_raw),
        },
        "overlay": {"size": len(overlay_blob), "sha256": sha256(overlay_blob)},
        "scenario_date_composition": SCENARIO_DATE_EXAMPLE,
        "duration_month_preserved": True,
        "non_delta_texts_preserved": True,
        "wrapper_prefix_preserved": True,
        "baseline_builder": baseline_metadata["builder"],
        "sc_binary_used": False,
    }


def validation_model(metrics: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": VALIDATION_SCHEMA,
        "status": "PASS",
        "issue": ISSUE_NUMBER,
        "resource": RESOURCE,
        "translation": {
            "calendar_month_entry_id": ENTRY_ID,
            "calendar_month_delta_count": 1,
            "duration_month_preserved": True,
        },
        "expected": {
            "baseline": metrics["baseline"],
            "candidate": metrics["candidate"],
            "overlay": metrics["overlay"],
        },
        "proofs": {
            "scenario_date_composition": metrics["scenario_date_composition"],
            "current_jp_source_hashes_fail_closed": True,
            "baseline_ko_hashes_fail_closed": True,
            "non_delta_texts_preserved": metrics["non_delta_texts_preserved"],
            "wrapper_prefix_preserved": metrics["wrapper_prefix_preserved"],
            "deterministic_ab_equal": True,
        },
        "safety": {
            "complete_candidate_binary_tracked": False,
            "installed_game_files_modified": False,
            "sc_binary_used": False,
        },
    }


def generate(stock_root: Path) -> dict[str, Any]:
    OVERLAY_PATH.parent.mkdir(parents=True, exist_ok=True)
    OVERLAY_PATH.write_bytes(pretty_bytes(expected_overlay(stock_root)))
    first, first_metrics = build_blob(stock_root)
    second, second_metrics = build_blob(stock_root)
    if first != second or first_metrics != second_metrics:
        raise ScenarioDateHotfixError("date-hotfix deterministic A/B differs")
    VALIDATION_PATH.write_bytes(pretty_bytes(validation_model(first_metrics)))
    return {"status": "GENERATED", **first_metrics, "deterministic_ab_equal": True}


def verify(stock_root: Path) -> dict[str, Any]:
    first, first_metrics = build_blob(stock_root)
    second, second_metrics = build_blob(stock_root)
    if first != second or first_metrics != second_metrics:
        raise ScenarioDateHotfixError("date-hotfix deterministic A/B differs")
    validation, validation_blob = strict_json(VALIDATION_PATH)
    expected = validation_model(first_metrics)
    if validation != expected or validation_blob != pretty_bytes(expected):
        raise ScenarioDateHotfixError("tracked date-hotfix validation differs")
    return {"status": "PASS", **first_metrics, "deterministic_ab_equal": True}


def safe_output_root(path: Path) -> Path:
    resolved = path.resolve()
    tmp_root = (REPO / "tmp").resolve()
    if resolved == tmp_root or tmp_root not in resolved.parents or resolved.exists():
        raise ScenarioDateHotfixError(f"unsafe output root: {resolved}")
    return resolved


def build_output(stock_root: Path, output_root: Path) -> dict[str, Any]:
    candidate, metrics = build_blob(stock_root)
    destination = safe_output_root(output_root)
    try:
        target = destination / Path(RESOURCE)
        target.parent.mkdir(parents=True, exist_ok=False)
        target.write_bytes(candidate)
        (destination / "private_manifest.json").write_bytes(pretty_bytes(metrics))
    except Exception:
        shutil.rmtree(destination, ignore_errors=True)
        raise
    return metrics


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("generate", "verify", "build"):
        child = commands.add_parser(name)
        child.add_argument("--stock-root", type=Path, default=DEFAULT_STOCK_ROOT)
        if name == "build":
            child.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    args = parser.parse_args()
    if args.command == "generate":
        result = generate(args.stock_root)
    elif args.command == "verify":
        result = verify(args.stock_root)
    else:
        result = build_output(args.stock_root, args.output_root)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
