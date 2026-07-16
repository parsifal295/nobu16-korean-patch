#!/usr/bin/env python3
"""Assemble the Steam PK 1.1.7 JP-route v0.8.0 exact-12 v4 candidate.

This is a post-v3 composition wrapper.  It first reconstructs the pinned v3
candidate privately, then applies only the three issue-specific JP deltas:

* scenario calendar-month wording in ``MSG_PK/JP/msgui.bin``;
* event-family clan labels in ``MSG_PK/JP/msgdata.bin``; and
* tactics-reading wording in the same ``msgdata.bin`` after the clan baseline;
* display-name / reading normalization for the reviewed court-office core; and
* the bounded 66-row residual event-text wave in ``MSG_PK/JP/msgev.bin``.

The wrapper never writes an installed Steam file.  It retains all output only
below ``tmp`` and emits a ZIP with exactly the twelve JP Steam paths.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Any, Mapping, Sequence


sys.dont_write_bytecode = True

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = SCRIPT.parents[2]
V3_PATH = (
    REPO
    / "workstreams"
    / "steam_jp_117_candidate_v3"
    / "build_steam_jp_117_candidate_v3.py"
)
SCENARIO_PATH = (
    REPO
    / "workstreams"
    / "steam_jp_scenario_date_hotfix_v1"
    / "build_steam_jp_scenario_date_hotfix_v1.py"
)
CLAN_PATH = (
    REPO
    / "workstreams"
    / "steam_jp_clan_label_normalization_v1"
    / "build_steam_jp_clan_label_normalization_v1.py"
)
TACTICS_PATH = (
    REPO
    / "workstreams"
    / "steam_jp_tactics_reading_hotfix_v1"
    / "build_steam_jp_tactics_reading_hotfix_v1.py"
)
OFFICE_PATH = (
    REPO
    / "workstreams"
    / "steam_jp_office_titles_core_v1"
    / "build_steam_jp_office_titles_core_v1.py"
)
MSGEV_RESIDUAL_PATH = (
    REPO
    / "workstreams"
    / "msgev_steam_jp_residual_wave09"
    / "build_msgev_steam_jp_residual_wave09.py"
)

DEFAULT_OUTPUT_ROOT = REPO / "tmp" / "steam_jp_117_candidate_v4"
DEFAULT_ZIP_NAME = "NOBU16_PK_Korean_Patch_Steam_1.1.7_v0.8.0.zip"
SCHEMA = "nobu16.kr.steam-jp-1.1.7-candidate-manifest.v4"
VERIFICATION_SCHEMA = "nobu16.kr.steam-jp-1.1.7-candidate-verification.v4"
VERIFICATION_PATH = WORKSTREAM / "verification.v4.json"

# The v3 tracked verification is the immutable integration baseline.  This
# pin prevents a later unreviewed v3 edit being silently absorbed into v4.
V3_VERIFICATION_SHA256 = (
    "7B05C0F44AE4849BAB65E55FD32CF62B37931E66EE41D6CC743BDC083F7D1FC8"
)
MSGUI_RESOURCE = "MSG_PK/JP/msgui.bin"
MSGDATA_RESOURCE = "MSG_PK/JP/msgdata.bin"
MSGEV_RESOURCE = "MSG_PK/JP/msgev.bin"
EXPECTED_SCENARIO_DELTA_COUNT = 1
EXPECTED_CLAN_DELTA_COUNT = 159
EXPECTED_MSGEV_RESIDUAL_EVENT_STORY_DELTA_COUNT = 50
EXPECTED_MSGEV_RESIDUAL_EVENT_LABEL_DELTA_COUNT = 16
EXPECTED_MSGEV_RESIDUAL_DELTA_COUNT = 66
EXPECTED_MSGEV_RESIDUAL_COMPOSED_CANDIDATE_PIN = {
    "size": 1_040_799,
    "packed_sha256": "A8835C3520B29A076A21014E17B17D7AAABF4AC99D37D65C891415AC17BBF3F5",
    "raw_size": 1_036_708,
    "raw_sha256": "6D87086EA6B533EAB3F3745DB7564E8D7842E7DD603AD765B2D6D900644E00FB",
    "string_count": 17_916,
}
EXPECTED_OFFICE_DISPLAY_DELTA_COUNT = 113
EXPECTED_OFFICE_READING_DELTA_COUNT = 8
EXPECTED_OFFICE_DELTA_COUNT = 121
EXPECTED_OFFICE_COMPOSED_CANDIDATE_PIN = {
    "size": 496_999,
    "packed_sha256": "2D1BEFF03972777FBA5EE0B8FEF24E6A03B285DA466A4DA439794D21587A0F69",
    "raw_size": 495_032,
    "raw_sha256": "25593167A47B5B0F69357F71E5E9882382F346AEF1B8DCA7DB6902D7E270AB67",
    "string_count": 29_218,
}
EXPECTED_OFFICE_DISPLAY_READING_ANCHORS = (
    (16_399, 16_670, "관백", "간파쿠"),
    (16_402, 16_673, "우대신", "우다이진"),
    (16_404, 16_675, "대납언", "다이나곤"),
    (16_613, 16_884, "정이대장군", "세이이다이쇼군"),
)


class CandidateV4Error(RuntimeError):
    """A v4 dependency, composition invariant, or output guard failed."""


def load_module(name: str, path: Path) -> Any:
    if not path.is_file():
        raise CandidateV4Error(f"required component is missing: {path}")
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise CandidateV4Error(f"cannot import component: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


V3 = load_module("nobu16_steam_jp_117_candidate_v4_base", V3_PATH)

STOCK_ROOT = V3.STOCK_ROOT
DEFAULT_FONT_ROOT = V3.DEFAULT_FONT_ROOT
PORT_TARGETS = V3.PORT_TARGETS
FONT_RESOURCES = V3.FONT_RESOURCES
TARGETS = V3.TARGETS
EXPECTED_TARGETS = V3.EXPECTED_TARGETS
if TARGETS != EXPECTED_TARGETS or len(TARGETS) != 12:
    raise RuntimeError("v4 exact-twelve target vector changed")
if DEFAULT_ZIP_NAME != V3.DEFAULT_ZIP_NAME:
    raise RuntimeError("v4 release asset name differs from v3")

IMMUTABLE_V07_TARGETS = tuple(
    path for path in V3.IMMUTABLE_V07_TARGETS if path != MSGUI_RESOURCE
)
V3_UNCHANGED_TARGETS = tuple(
    path
    for path in TARGETS
    if path not in {MSGUI_RESOURCE, MSGDATA_RESOURCE, MSGEV_RESOURCE}
)
if len(IMMUTABLE_V07_TARGETS) != 6 or len(V3_UNCHANGED_TARGETS) != 9:
    raise RuntimeError("v4 mutable target vector changed")


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def blob_spec(blob: bytes) -> dict[str, Any]:
    return {"size": len(blob), "sha256": sha256(blob)}


def path_spec(path: Path) -> dict[str, Any]:
    return blob_spec(path.read_bytes())


def full_packed_spec(common: Any, blob: bytes) -> dict[str, Any]:
    _wrapper, raw = common.decompress_wrapper(blob)
    table = common.parse_message_table(raw)
    return {
        "size": len(blob),
        "packed_sha256": sha256(blob),
        "raw_size": len(raw),
        "raw_sha256": sha256(raw),
        "string_count": table.string_count,
    }


def _require_equal(actual: Any, expected: Any, label: str) -> None:
    if actual != expected:
        raise CandidateV4Error(f"{label} differs: expected={expected!r}, actual={actual!r}")


def _require_int(value: Any, expected: int, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value != expected:
        raise CandidateV4Error(f"{label} differs: {value!r} != {expected}")
    return value


def _source_free_json_spec(path: Path) -> dict[str, Any]:
    blob = path.read_bytes()
    try:
        value = json.loads(blob.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CandidateV4Error(f"invalid public JSON: {path}") from exc
    if not isinstance(value, dict):
        raise CandidateV4Error(f"public JSON root is not an object: {path}")
    return {"path": path.relative_to(REPO).as_posix(), **blob_spec(blob)}


def load_v3_verification() -> dict[str, Any]:
    if not V3.VERIFICATION_PATH.is_file():
        raise CandidateV4Error("tracked v3 verification is missing")
    blob = V3.VERIFICATION_PATH.read_bytes()
    if sha256(blob) != V3_VERIFICATION_SHA256:
        raise CandidateV4Error("immutable v3 verification pin changed")
    value = json.loads(blob.decode("utf-8"))
    if not isinstance(value, dict) or value.get("schema") != V3.VERIFICATION_SCHEMA:
        raise CandidateV4Error("immutable v3 verification schema changed")
    if value.get("candidate_paths") != list(TARGETS):
        raise CandidateV4Error("immutable v3 candidate vector changed")
    candidates = value.get("candidates")
    if not isinstance(candidates, dict) or set(candidates) != set(TARGETS):
        raise CandidateV4Error("immutable v3 candidate pins changed")
    return value


def load_scenario() -> Any:
    module = load_module("nobu16_steam_jp_scenario_date_hotfix_v4", SCENARIO_PATH)
    if getattr(module, "RESOURCE", None) != MSGUI_RESOURCE:
        raise CandidateV4Error("scenario-date resource differs from msgui")
    if not callable(getattr(module, "build_blob", None)):
        raise CandidateV4Error("scenario-date component has no build_blob(stock_root)")
    return module


def load_clan() -> Any:
    module = load_module("nobu16_steam_jp_clan_label_normalization_v4", CLAN_PATH)
    if getattr(module, "RESOURCE", None) != MSGDATA_RESOURCE:
        raise CandidateV4Error("clan-label resource differs from msgdata")
    if not callable(getattr(module, "build_blob", None)):
        raise CandidateV4Error("clan-label component has no build_blob(stock_root)")
    return module


def load_tactics() -> Any:
    module = load_module("nobu16_steam_jp_tactics_reading_hotfix_v4", TACTICS_PATH)
    if getattr(module, "RESOURCE", None) != MSGDATA_RESOURCE:
        raise CandidateV4Error("tactics-reading resource differs from msgdata")
    if not callable(getattr(module, "build_blob", None)):
        raise CandidateV4Error("tactics-reading component has no build_blob(stock_root)")
    return module


def load_office() -> Any:
    module = load_module("nobu16_steam_jp_office_titles_core_v4", OFFICE_PATH)
    if getattr(module, "RESOURCE", None) != MSGDATA_RESOURCE:
        raise CandidateV4Error("office-title resource differs from msgdata")
    if not callable(getattr(module, "apply_to_packed", None)):
        raise CandidateV4Error("office-title component has no apply_to_packed(stock_root, baseline_packed)")
    return module


def load_msgev_residual() -> Any:
    module = load_module(
        "nobu16_msgev_steam_jp_residual_wave09_v4", MSGEV_RESIDUAL_PATH
    )
    if getattr(module, "RESOURCE", None) != MSGEV_RESOURCE:
        raise CandidateV4Error("msgev residual resource differs from msgev")
    if not callable(getattr(module, "build_blob", None)):
        raise CandidateV4Error("msgev residual component has no build_blob(stock_root)")
    return module


def _changed_ids(common: Any, before: bytes, after: bytes) -> list[int]:
    _before_header, before_raw = common.decompress_wrapper(before)
    _after_header, after_raw = common.decompress_wrapper(after)
    before_table = common.parse_message_table(before_raw)
    after_table = common.parse_message_table(after_raw)
    if before_table.string_count != after_table.string_count:
        raise CandidateV4Error("message string-domain length changed")
    return [
        entry_id
        for entry_id, (old, new) in enumerate(zip(before_table.texts, after_table.texts))
        if old != new
    ]


def build_msgev_residual_hotfix(
    stock_root: Path, v3_msgev: bytes
) -> tuple[bytes, dict[str, Any]]:
    """Build the reviewed residual event wave on the pinned v3 ``msgev`` layer."""

    module = load_msgev_residual()
    v3_spec = module.packed_spec(v3_msgev)
    _require_equal(
        v3_spec,
        getattr(module, "WAVE08_BASELINE_PIN", None),
        "msgev residual v3 baseline",
    )
    candidate, metrics = module.build_blob(stock_root)
    if not isinstance(candidate, bytes) or not isinstance(metrics, dict):
        raise CandidateV4Error("msgev residual build_blob returned malformed values")
    candidate_spec = module.packed_spec(candidate)
    _require_equal(
        candidate_spec,
        getattr(module, "OUTPUT_CANDIDATE_PIN", None),
        "msgev residual component candidate pin",
    )
    _require_equal(
        full_packed_spec(module.COMMON, candidate),
        EXPECTED_MSGEV_RESIDUAL_COMPOSED_CANDIDATE_PIN,
        "msgev residual composed candidate pin",
    )
    _require_equal(
        metrics.get("wave08_baseline"),
        v3_spec,
        "msgev residual reported baseline",
    )
    expected_ids = list(getattr(module, "TARGET_IDS", ()))
    if not expected_ids:
        raise CandidateV4Error("msgev residual target ID vector is missing")
    changed = _changed_ids(module.COMMON, v3_msgev, candidate)
    _require_equal(changed, expected_ids, "msgev residual changed ID vector")
    _require_int(
        metrics.get("residual_event_story_delta_count"),
        EXPECTED_MSGEV_RESIDUAL_EVENT_STORY_DELTA_COUNT,
        "msgev residual event-story delta count",
    )
    _require_int(
        metrics.get("residual_event_label_delta_count"),
        EXPECTED_MSGEV_RESIDUAL_EVENT_LABEL_DELTA_COUNT,
        "msgev residual event-label delta count",
    )
    _require_int(
        metrics.get("residual_delta_count"),
        EXPECTED_MSGEV_RESIDUAL_DELTA_COUNT,
        "msgev residual total delta count",
    )
    if not bool(metrics.get("non_target_texts_preserved")):
        raise CandidateV4Error("msgev residual non-target preservation proof is absent")
    if not bool(metrics.get("format_invariants_preserved")):
        raise CandidateV4Error("msgev residual format-invariant proof is absent")
    if callable(getattr(module, "verify", None)):
        verified = module.verify(stock_root)
        if not isinstance(verified, dict) or verified.get("status") != "PASS":
            raise CandidateV4Error("msgev residual tracked validation did not pass")
    return candidate, {
        "workstream": "msgev_steam_jp_residual_wave09",
        "validation": _source_free_json_spec(module.VALIDATION_PATH),
        "v3_baseline": v3_spec,
        "candidate": candidate_spec,
        "event_story_delta_count": metrics["residual_event_story_delta_count"],
        "event_label_delta_count": metrics["residual_event_label_delta_count"],
        "delta_count": metrics["residual_delta_count"],
        "target_ids_sha256": metrics.get("target_ids_sha256"),
        "changed_ids_sha256": sha256(V3.V2.BASE.json_bytes(changed)),
        "non_target_texts_preserved": True,
        "format_invariants_preserved": True,
        "wrapper_prefix_preserved": bool(metrics.get("wrapper_prefix_preserved")),
    }


def build_scenario_hotfix(stock_root: Path, v3_msgui: bytes) -> tuple[bytes, dict[str, Any]]:
    module = load_scenario()
    candidate, metrics = module.build_blob(stock_root)
    if not isinstance(candidate, bytes) or not isinstance(metrics, dict):
        raise CandidateV4Error("scenario-date build_blob returned malformed values")
    _require_equal(metrics.get("baseline"), blob_spec(v3_msgui), "scenario v3 baseline")
    _require_int(metrics.get("entry_count"), EXPECTED_SCENARIO_DELTA_COUNT, "scenario delta count")
    _require_equal(
        {"size": metrics.get("candidate", {}).get("size"), "sha256": metrics.get("candidate", {}).get("sha256")},
        blob_spec(candidate),
        "scenario candidate pin",
    )
    changed = _changed_ids(module.MSGUI, v3_msgui, candidate)
    _require_equal(changed, [module.ENTRY_ID], "scenario changed ID vector")
    if not bool(metrics.get("duration_month_preserved")):
        raise CandidateV4Error("scenario hotfix did not preserve duration month")
    if callable(getattr(module, "verify", None)):
        verified = module.verify(stock_root)
        if not isinstance(verified, dict) or verified.get("status") != "PASS":
            raise CandidateV4Error("scenario-date tracked validation did not pass")
    return candidate, {
        "workstream": "steam_jp_scenario_date_hotfix_v1",
        "validation": _source_free_json_spec(module.VALIDATION_PATH),
        "baseline": blob_spec(v3_msgui),
        "candidate": blob_spec(candidate),
        "entry_id": module.ENTRY_ID,
        "delta_count": len(changed),
        "duration_month_preserved": True,
        "wrapper_prefix_preserved": bool(metrics.get("wrapper_prefix_preserved")),
    }


def build_msgdata_hotfixes(
    stock_root: Path, v3_msgdata: bytes
) -> tuple[bytes, dict[str, Any]]:
    """Build the tactics delta only after proving the clan baseline composes."""

    clan = load_clan()
    clan_candidate, clan_metrics = clan.build_blob(stock_root)
    if not isinstance(clan_candidate, bytes) or not isinstance(clan_metrics, dict):
        raise CandidateV4Error("clan-label build_blob returned malformed values")
    v3_spec = full_packed_spec(clan.COMMON, v3_msgdata)
    _require_equal(clan_metrics.get("wave08_baseline"), v3_spec, "clan v3 baseline")
    _require_int(
        clan_metrics.get("normalization_delta_count"),
        EXPECTED_CLAN_DELTA_COUNT,
        "clan normalization delta count",
    )
    _require_equal(
        clan_metrics.get("candidate"),
        full_packed_spec(clan.COMMON, clan_candidate),
        "clan candidate pin",
    )
    clan_changed = _changed_ids(clan.COMMON, v3_msgdata, clan_candidate)
    if len(clan_changed) != EXPECTED_CLAN_DELTA_COUNT:
        raise CandidateV4Error("clan changed ID count differs from its contract")
    if callable(getattr(clan, "verify", None)):
        verified = clan.verify(stock_root)
        if not isinstance(verified, dict) or verified.get("status") != "PASS":
            raise CandidateV4Error("clan-label tracked validation did not pass")

    tactics = load_tactics()
    candidate, metrics = tactics.build_blob(stock_root)
    if not isinstance(candidate, bytes) or not isinstance(metrics, dict):
        raise CandidateV4Error("tactics-reading build_blob returned malformed values")
    expected_pin = getattr(tactics, "OUTPUT_CANDIDATE_PIN", None)
    if not isinstance(expected_pin, dict):
        raise CandidateV4Error("tactics-reading output candidate pin is missing")
    candidate_spec = full_packed_spec(clan.COMMON, candidate)
    _require_equal(candidate_spec, expected_pin, "tactics-reading candidate pin")
    _require_equal(
        metrics.get("post_clan_baseline"),
        full_packed_spec(clan.COMMON, clan_candidate),
        "tactics-reading clan baseline",
    )

    # The tactics builder must retain every clan-normalized coordinate.  The
    # two hotfixes occupy distinct event-family and reading domains.
    _clan_header, clan_raw = clan.COMMON.decompress_wrapper(clan_candidate)
    _final_header, final_raw = clan.COMMON.decompress_wrapper(candidate)
    clan_table = clan.COMMON.parse_message_table(clan_raw)
    final_table = clan.COMMON.parse_message_table(final_raw)
    if final_table.string_count != clan_table.string_count:
        raise CandidateV4Error("tactics-reading changed the msgdata string domain")
    for entry_id in clan_changed:
        if final_table.texts[entry_id] != clan_table.texts[entry_id]:
            raise CandidateV4Error(f"tactics-reading reverted clan label at {entry_id}")
    tactics_changed = _changed_ids(clan.COMMON, clan_candidate, candidate)
    expected_tactics_ids = list(getattr(tactics, "TARGET_IDS", ()))
    if not expected_tactics_ids:
        raise CandidateV4Error("tactics-reading target ID vector is missing")
    _require_equal(tactics_changed, expected_tactics_ids, "tactics-reading changed ID vector")
    _require_int(
        metrics.get("tactics_reading_delta_count"),
        len(expected_tactics_ids),
        "tactics-reading delta count",
    )
    if not bool(metrics.get("all_active_tactics_reading_slots_no_latin")):
        raise CandidateV4Error("tactics-reading Latin-free proof is absent")
    if callable(getattr(tactics, "verify", None)):
        verified = tactics.verify(stock_root)
        if not isinstance(verified, dict) or verified.get("status") != "PASS":
            raise CandidateV4Error("tactics-reading tracked validation did not pass")

    tactics_meta = {
        "workstream": "steam_jp_tactics_reading_hotfix_v1",
        "validation": _source_free_json_spec(tactics.VALIDATION_PATH),
        "v3_baseline": v3_spec,
        "clan_candidate": full_packed_spec(clan.COMMON, clan_candidate),
        "candidate": candidate_spec,
        "clan_delta_count": len(clan_changed),
        "tactics_delta_count": len(tactics_changed),
        "tactics_target_ids_sha256": getattr(tactics, "TARGET_IDS_SHA256", None),
        "active_tactics_reading_slot_count": metrics.get(
            "active_tactics_reading_slot_count"
        ),
        "all_active_tactics_reading_slots_no_latin": True,
        "clan_changed_ids_sha256": sha256(
            V3.V2.BASE.json_bytes(clan_changed)
        ),
        "tactics_changed_ids_sha256": sha256(
            V3.V2.BASE.json_bytes(tactics_changed)
        ),
        "clan_wrapper_prefix_preserved": bool(
            clan_metrics.get("wrapper_prefix_preserved")
        ),
    }

    office = load_office()
    office_candidate, office_metrics = office.apply_to_packed(stock_root, candidate)
    if not isinstance(office_candidate, bytes) or not isinstance(office_metrics, dict):
        raise CandidateV4Error("office-title apply_to_packed returned malformed values")
    _require_equal(
        office_metrics.get("input_baseline"),
        candidate_spec,
        "office-title tactics baseline",
    )
    office_candidate_spec = full_packed_spec(clan.COMMON, office_candidate)
    _require_equal(
        office_candidate_spec,
        EXPECTED_OFFICE_COMPOSED_CANDIDATE_PIN,
        "office-title composed candidate pin",
    )
    _require_equal(
        office_metrics.get("candidate"),
        office_candidate_spec,
        "office-title candidate pin",
    )
    office_translation = office_metrics.get("translation")
    if not isinstance(office_translation, dict):
        raise CandidateV4Error("office-title translation metadata is missing")
    _require_int(
        office_translation.get("changed_display_count"),
        EXPECTED_OFFICE_DISPLAY_DELTA_COUNT,
        "office-title display delta count",
    )
    _require_int(
        office_translation.get("changed_reading_count"),
        EXPECTED_OFFICE_READING_DELTA_COUNT,
        "office-title reading delta count",
    )
    _require_int(
        office_translation.get("changed_entry_count"),
        EXPECTED_OFFICE_DELTA_COUNT,
        "office-title total delta count",
    )
    office_changed = _changed_ids(clan.COMMON, candidate, office_candidate)
    if len(office_changed) != EXPECTED_OFFICE_DELTA_COUNT:
        raise CandidateV4Error("office-title changed ID count differs from its contract")
    target_coordinates = set(office.target_by_coordinate(final_table.texts))
    if not set(office_changed).issubset(target_coordinates):
        raise CandidateV4Error("office-title changed a coordinate outside reviewed core scope")
    _office_header, office_raw = clan.COMMON.decompress_wrapper(office_candidate)
    office_table = clan.COMMON.parse_message_table(office_raw)
    for display_id, reading_id, display, reading in EXPECTED_OFFICE_DISPLAY_READING_ANCHORS:
        _require_equal(
            office_table.texts[display_id],
            display,
            f"office display anchor {display_id}",
        )
        _require_equal(
            office_table.texts[reading_id],
            reading,
            f"office reading anchor {reading_id}",
        )
    for entry_id in (*clan_changed, *tactics_changed):
        if office_table.texts[entry_id] != final_table.texts[entry_id]:
            raise CandidateV4Error(f"office-title reverted prior msgdata delta at {entry_id}")
    office_scope = office_metrics.get("scope")
    if not isinstance(office_scope, dict):
        raise CandidateV4Error("office-title scope metadata is missing")
    _require_int(
        office_scope.get("target_contract_count"),
        292,
        "office-title target contract count",
    )
    excluded = office_scope.get("excluded_bakufu_id_range")
    _require_equal(excluded, [16_614, 16_624], "office-title excluded Bakufu range")
    if set(office_changed) & set(range(excluded[0], excluded[1] + 1)):
        raise CandidateV4Error("office-title changed the deferred Bakufu scope")

    office_meta = {
        "workstream": "steam_jp_office_titles_core_v1",
        "validation": _source_free_json_spec(office.VALIDATION_PATH),
        "input_baseline": candidate_spec,
        "candidate": office_candidate_spec,
        "display_delta_count": office_translation["changed_display_count"],
        "reading_delta_count": office_translation["changed_reading_count"],
        "delta_count": office_translation["changed_entry_count"],
        "scope": office_scope,
        "display_reading_anchors": {
            str(display_id): {
                "display": display,
                "reading_id": reading_id,
                "reading": reading,
            }
            for display_id, reading_id, display, reading in EXPECTED_OFFICE_DISPLAY_READING_ANCHORS
        },
        "deferred_domains": {
            "geographic_title_categories": True,
            "bakufu_16614_16624": True,
        },
        "changed_ids_sha256": sha256(V3.V2.BASE.json_bytes(office_changed)),
        "prior_clan_and_tactics_preserved": True,
    }
    return office_candidate, {"tactics_reading": tactics_meta, "office_titles_core": office_meta}


def _candidate_files(candidate_root: Path) -> dict[str, dict[str, Any]]:
    if V3.V2.BASE.candidate_files(candidate_root) != list(TARGETS):
        raise CandidateV4Error("candidate root is not the exact twelve-file vector")
    return {
        relative: path_spec(candidate_root / Path(relative)) for relative in TARGETS
    }


def _replace_candidate_file(
    candidate_root: Path,
    relative: str,
    expected_before: Mapping[str, Any],
    replacement: bytes,
) -> dict[str, Any]:
    target = candidate_root / Path(relative)
    if not target.is_file():
        raise CandidateV4Error(f"v3 candidate target is missing: {relative}")
    _require_equal(path_spec(target), dict(expected_before), f"v3 input pin {relative}")
    temporary = target.with_name(target.name + ".v4.tmp")
    if temporary.exists():
        raise CandidateV4Error(f"unsafe existing temporary target: {temporary}")
    temporary.write_bytes(replacement)
    try:
        _require_equal(path_spec(temporary), blob_spec(replacement), f"replacement pin {relative}")
        os.replace(temporary, target)
    finally:
        if temporary.exists():
            temporary.unlink()
    return path_spec(target)


def _assert_immutable_vectors(
    candidates: Mapping[str, dict[str, Any]], v3_pins: Mapping[str, dict[str, Any]]
) -> None:
    if set(candidates) != set(TARGETS):
        raise CandidateV4Error("candidate manifest does not cover exact target vector")
    for relative in V3_UNCHANGED_TARGETS:
        _require_equal(candidates.get(relative), v3_pins.get(relative), f"v3 unchanged pin {relative}")
    v07_pins = V3.immutable_v07_candidate_pins()
    for relative in IMMUTABLE_V07_TARGETS:
        _require_equal(candidates.get(relative), v07_pins.get(relative), f"v0.7 immutable pin {relative}")
    for relative in FONT_RESOURCES:
        _require_equal(candidates.get(relative), v07_pins.get(relative), f"v0.7 font pin {relative}")


def _assert_zip_matches(candidate_root: Path, zip_path: Path) -> None:
    with zipfile.ZipFile(zip_path, "r") as archive:
        names = archive.namelist()
        if names != list(TARGETS):
            raise CandidateV4Error("ZIP member vector is not exact twelve-file JP order")
        for relative in TARGETS:
            if archive.read(relative) != (candidate_root / Path(relative)).read_bytes():
                raise CandidateV4Error(f"ZIP payload differs from candidate: {relative}")


def verification_projection(manifest: dict[str, Any]) -> dict[str, Any]:
    components = manifest["components"]
    v3_translation = manifest["v3_translation"]
    scenario = components["scenario_date_hotfix"]
    msgdata = components["msgdata_hotfixes"]
    tactics = msgdata["tactics_reading"]
    office = msgdata["office_titles_core"]
    msgev_residual = components["msgev_residual_wave09"]
    return {
        "schema": VERIFICATION_SCHEMA,
        "runtime": manifest["runtime"],
        "candidate_file_count": manifest["candidate_file_count"],
        "candidate_paths": manifest["candidate_paths"],
        "predecessors": manifest["predecessors"],
        "candidates": manifest["candidates"],
        "translation": {
            **v3_translation,
            "scenario_calendar_month_delta_entries": scenario["delta_count"],
            "scenario_duration_month_preserved": scenario["duration_month_preserved"],
            "msgev_residual_event_story_delta_entries": msgev_residual[
                "event_story_delta_count"
            ],
            "msgev_residual_event_label_delta_entries": msgev_residual[
                "event_label_delta_count"
            ],
            "msgev_residual_wave09_delta_entries": msgev_residual["delta_count"],
            "clan_label_normalization_delta_entries": tactics["clan_delta_count"],
            "tactics_reading_delta_entries": tactics["tactics_delta_count"],
            "office_titles_core_display_delta_entries": office["display_delta_count"],
            "office_titles_core_reading_delta_entries": office["reading_delta_count"],
            "office_titles_core_delta_entries": office["delta_count"],
        },
        "provenance": {
            "v3_verification_sha256": V3_VERIFICATION_SHA256,
            "scenario_date_hotfix": scenario,
            "msgev_residual_wave09": msgev_residual,
            "tactics_reading_hotfix": tactics,
            "office_titles_core": office,
            "fonts": components["fonts"]["evidence"],
        },
        "zip": manifest["zip"],
        "checks": {
            "steam_1_1_7_predecessors_exact": True,
            "v3_baseline_candidate_exact": True,
            "scenario_date_id1051_integrated": True,
            "scenario_duration_month_preserved": True,
            "msgev_residual_wave09_66_integrated": True,
            "clan_label_normalization_159_integrated": True,
            "tactics_reading_hotfix_integrated": True,
            "office_titles_core_121_integrated": True,
            "office_titles_geographic_and_bakufu_deferred": True,
            "v0_7_0_non_common_candidates_exact": True,
            "high_resolution_seoul_hangang_four_routes_exact": True,
            "exact_twelve_files": True,
            "zip_payloads_equal_candidates": True,
            "staged_before_promote": True,
            "sc_container_used": False,
            "steam_files_written": False,
        },
    }


def validate_destination(path: Path) -> Path:
    resolved = path.resolve()
    tmp_root = (REPO / "tmp").resolve()
    if resolved == tmp_root or tmp_root not in resolved.parents:
        raise CandidateV4Error(f"output must be below repository tmp: {resolved}")
    if resolved.exists():
        raise CandidateV4Error(f"output already exists: {resolved}")
    resolved.parent.mkdir(parents=True, exist_ok=True)
    return resolved


def build_staged(
    stock_root: Path, port_stock_root: Path, font_root: Path, staging: Path
) -> tuple[dict[str, Any], dict[str, Any]]:
    v3_manifest, v3_projection = V3.build_staged(
        stock_root, port_stock_root, font_root, staging
    )
    v3_verification = load_v3_verification()
    _require_equal(v3_projection, v3_verification, "reconstructed v3 verification")
    candidate_root = staging / "candidate"
    base_pins = v3_manifest["candidates"]
    if set(base_pins) != set(TARGETS):
        raise CandidateV4Error("v3 base manifest candidate vector changed")

    v3_msgui = (candidate_root / Path(MSGUI_RESOURCE)).read_bytes()
    v3_msgdata = (candidate_root / Path(MSGDATA_RESOURCE)).read_bytes()
    v3_msgev = (candidate_root / Path(MSGEV_RESOURCE)).read_bytes()
    _require_equal(blob_spec(v3_msgui), base_pins[MSGUI_RESOURCE], "v3 msgui pin")
    _require_equal(blob_spec(v3_msgdata), base_pins[MSGDATA_RESOURCE], "v3 msgdata pin")
    _require_equal(blob_spec(v3_msgev), base_pins[MSGEV_RESOURCE], "v3 msgev pin")
    scenario_blob, scenario_meta = build_scenario_hotfix(stock_root, v3_msgui)
    msgev_blob, msgev_meta = build_msgev_residual_hotfix(stock_root, v3_msgev)
    msgdata_blob, msgdata_meta = build_msgdata_hotfixes(stock_root, v3_msgdata)

    _replace_candidate_file(candidate_root, MSGUI_RESOURCE, base_pins[MSGUI_RESOURCE], scenario_blob)
    _replace_candidate_file(candidate_root, MSGEV_RESOURCE, base_pins[MSGEV_RESOURCE], msgev_blob)
    _replace_candidate_file(candidate_root, MSGDATA_RESOURCE, base_pins[MSGDATA_RESOURCE], msgdata_blob)
    candidates = _candidate_files(candidate_root)
    _assert_immutable_vectors(candidates, base_pins)
    if V3.V2.predecessor_vector(stock_root, port_stock_root) != v3_manifest["predecessors"]:
        raise CandidateV4Error("Steam stock vector changed during offline build")

    old_zip = staging / DEFAULT_ZIP_NAME
    if not old_zip.is_file():
        raise CandidateV4Error("v3 staged ZIP is missing")
    old_zip.unlink()
    zip_spec = V3.V2.make_zip(candidate_root, old_zip)
    _assert_zip_matches(candidate_root, old_zip)
    old_v3_manifest = staging / "candidate_manifest.v3.json"
    if old_v3_manifest.is_file():
        old_v3_manifest.unlink()

    manifest = {
        "schema": SCHEMA,
        "runtime": dict(v3_manifest["runtime"]),
        "candidate_root": "candidate",
        "candidate_file_count": len(candidates),
        "candidate_paths": list(TARGETS),
        "predecessors": v3_manifest["predecessors"],
        "candidates": {relative: candidates[relative] for relative in TARGETS},
        "v3_translation": dict(v3_verification["translation"]),
        "components": {
            "v3_base": {
                "verification": {
                    "path": V3.VERIFICATION_PATH.relative_to(REPO).as_posix(),
                    "sha256": V3_VERIFICATION_SHA256,
                },
                "unchanged_targets": list(V3_UNCHANGED_TARGETS),
            },
            "scenario_date_hotfix": scenario_meta,
            "msgev_residual_wave09": msgev_meta,
            "msgdata_hotfixes": msgdata_meta,
            "fonts": dict(v3_manifest["components"]["fonts"]),
        },
        "zip": {"name": DEFAULT_ZIP_NAME, **zip_spec, "member_count": len(TARGETS)},
        "checks": {
            "steam_1_1_7_predecessors_exact": True,
            "jp_route_exact": True,
            "exact_twelve_files": True,
            "v3_baseline_candidate_exact": True,
            "scenario_date_id1051_integrated": True,
            "scenario_duration_month_preserved": True,
            "msgev_residual_wave09_66_integrated": True,
            "clan_label_normalization_159_integrated": True,
            "tactics_reading_hotfix_integrated": True,
            "office_titles_core_121_integrated": True,
            "office_titles_geographic_and_bakufu_deferred": True,
            "v0_7_0_non_common_candidates_exact": True,
            "high_resolution_seoul_hangang_four_routes_exact": True,
            "zip_payloads_equal_candidates": True,
            "staged_before_promote": True,
            "sc_container_used": False,
            "memory_patch": False,
            "dll_injection": False,
            "hooking": False,
            "exe_or_registry_modified": False,
            "steam_files_written": False,
        },
    }
    projection = verification_projection(manifest)
    (staging / "candidate_manifest.v4.json").write_bytes(V3.V2.BASE.json_bytes(manifest))
    return manifest, projection


def staged_build(
    stock_root: Path,
    port_stock_root: Path,
    font_root: Path,
    destination_parent: Path,
) -> tuple[Path, dict[str, Any], dict[str, Any]]:
    staging = Path(tempfile.mkdtemp(prefix=".steam-jp-117-v4-", dir=destination_parent))
    try:
        manifest, projection = build_staged(stock_root, port_stock_root, font_root, staging)
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    return staging, manifest, projection


def load_tracked_verification() -> dict[str, Any]:
    if not VERIFICATION_PATH.is_file():
        raise CandidateV4Error("tracked v4 verification is missing")
    blob = VERIFICATION_PATH.read_bytes()
    value = json.loads(blob.decode("utf-8"))
    if not isinstance(value, dict) or value.get("schema") != VERIFICATION_SCHEMA:
        raise CandidateV4Error("tracked v4 verification schema changed")
    if blob != V3.V2.BASE.json_bytes(value):
        raise CandidateV4Error("tracked v4 verification formatting changed")
    return value


def command_bootstrap(args: argparse.Namespace) -> int:
    proposal = validate_destination(args.proposal)
    staging, _manifest, projection = staged_build(
        args.stock_root.resolve(),
        args.port_stock_root.resolve(),
        args.font_candidate_root.resolve(),
        proposal.parent,
    )
    try:
        V3.V2.atomic_write(proposal, V3.V2.BASE.json_bytes(projection))
    finally:
        shutil.rmtree(staging, ignore_errors=True)
    print(f"proposal={proposal}")
    print(f"proposal_sha256={V3.V2.BASE.sha256_path(proposal)}")
    print("candidate_outputs_retained=False")
    print("steam_files_written=False")
    return 0


def command_verify(args: argparse.Namespace) -> int:
    expected = load_tracked_verification()
    parent = validate_destination(args.scratch_root)
    parent.mkdir(parents=False)
    try:
        staging, _manifest, projection = staged_build(
            args.stock_root.resolve(),
            args.port_stock_root.resolve(),
            args.font_candidate_root.resolve(),
            parent,
        )
        try:
            _require_equal(projection, expected, "integrated v4 verification")
        finally:
            shutil.rmtree(staging, ignore_errors=True)
    finally:
        shutil.rmtree(parent, ignore_errors=True)
    print("status=PASS")
    print("candidate_outputs_retained=False")
    print("steam_files_written=False")
    return 0


def command_build(args: argparse.Namespace) -> int:
    expected = load_tracked_verification()
    output = validate_destination(args.output_root)
    staging, manifest, projection = staged_build(
        args.stock_root.resolve(),
        args.port_stock_root.resolve(),
        args.font_candidate_root.resolve(),
        output.parent,
    )
    try:
        _require_equal(projection, expected, "integrated v4 verification")
        os.replace(staging, output)
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    print("status=PASS")
    print(f"steam_pk_version={manifest['runtime']['pk_version']}")
    print(f"steam_build_id={manifest['runtime']['steam_build_id']}")
    print(f"candidate_files={manifest['candidate_file_count']}")
    print(f"zip_name={manifest['zip']['name']}")
    print(f"zip_sha256={manifest['zip']['sha256']}")
    print("steam_files_written=False")
    return 0


def add_common_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--stock-root", type=Path, default=STOCK_ROOT)
    parser.add_argument(
        "--port-stock-root",
        type=Path,
        required=True,
        help=(
            "directory containing pristine Steam 1.1.7 "
            "res_lang_pk_port1.bin and res_lang_pk_port2.bin"
        ),
    )
    parser.add_argument("--font-candidate-root", type=Path, default=DEFAULT_FONT_ROOT)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    bootstrap = commands.add_parser("bootstrap", help="emit only a proposed verification pin")
    add_common_arguments(bootstrap)
    bootstrap.add_argument(
        "--proposal",
        type=Path,
        default=REPO / "tmp" / "steam_jp_117_candidate_v4.proposed.json",
    )
    bootstrap.set_defaults(handler=command_bootstrap)
    verify = commands.add_parser("verify", help="rebuild privately and compare to pin")
    add_common_arguments(verify)
    verify.add_argument(
        "--scratch-root",
        type=Path,
        default=REPO / "tmp" / "steam_jp_117_candidate_v4_verify",
    )
    verify.set_defaults(handler=command_verify)
    build = commands.add_parser("build", help="stage, verify, and retain exact twelve")
    add_common_arguments(build)
    build.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    build.set_defaults(handler=command_build)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return int(args.handler(args))
    except (CandidateV4Error, OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
