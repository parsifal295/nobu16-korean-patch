#!/usr/bin/env python3
"""Compose the source-free safe residual wave for base JP event text.

This workstream is deliberately read-only with respect to game resources.  It
uses the pre-application Steam 1.1.7 backup as the only stock input, composes
the existing 13,045-row base transfer in memory, and then adds the disjoint
40-row residual overlay.  Five rows whose Korean target still requires a
terminology decision remain explicitly unchanged.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any, Iterable, Sequence


sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
BASE_BUILDER_PATH = (
    REPO
    / "workstreams"
    / "base_ev_strdata_jp_switch_v13_transfer_v1"
    / "build_base_ev_strdata_jp_switch_v13_transfer_v1.py"
)
CONTRACT_PATH = (
    REPO
    / "workstreams"
    / "base_jp_residual_wave10_inventory"
    / "public"
    / "base_jp_residual_wave10_contracts.v1.json"
)
OVERLAY_PATH = HERE / "public" / "ev_strdata_ko_base_jp_residual_wave11_40.v1.json"
HOLD_PATH = HERE / "public" / "ev_strdata_base_jp_residual_wave11_holds_5.v1.json"
VALIDATION_PATH = HERE / "validation.v1.json"
TRANSLATIONS_PATH = HERE / "translations.py"


def load_translations() -> Any:
    """Load this workstream's targets without a generic module-name collision."""
    spec = importlib.util.spec_from_file_location("base_ev_strdata_wave11_translations", TRANSLATIONS_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load wave11 translations")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


_translations = load_translations()
TRANSLATIONS: dict[int, str] = _translations.TRANSLATIONS
MANUAL_HOLD_IDS: tuple[int, ...] = _translations.MANUAL_HOLD_IDS


RESOURCE = "MSG/JP/ev_strdata.bin"
LIVE_STEAM_ROOT = Path(r"F:/SteamLibrary/steamapps/common/NOBU16")
DEFAULT_STOCK_ROOT = (
    LIVE_STEAM_ROOT
    / "KR_PATCH_BACKUP"
    / "file_only_transaction"
    / "steam-jp-1.1.7-v0.8.0"
    / "originals"
)
DEFAULT_GAME_ROOT = DEFAULT_STOCK_ROOT
DEFAULT_SWITCH_ZIP = REPO / "tmp" / "third_party_switch_v13" / "NobunagaShinsei_KoreanPatch_v1.3.zip"
OVERLAY_SCHEMA = "nobu16.kr.base-ev-strdata-jp-residual-wave11-overlay.v1"
HOLD_SCHEMA = "nobu16.kr.base-ev-strdata-jp-residual-wave11-holds.v1"
VALIDATION_SCHEMA = "nobu16.kr.base-ev-strdata-jp-residual-wave11-validation.v1"
OVERLAY_ID = "base_ev_strdata_jp_residual_wave11_40"

# The deterministic in-memory candidate is pinned before public artifact
# generation.  Any source, contract, or transform drift therefore fails closed.
TARGET_PIN: dict[str, Any] = {
    "packed_size": 928_464,
    "packed_sha256": "9ED892E85AF18EB3BC965A834853969BC06F486A2466A83F3CEBED1B8D5433C0",
    "raw_size": 924_812,
    "raw_sha256": "205BA7CA7873411B03C51D1931C277DA9BA8E56700B5EA0D8EDB82B49BD45ABE",
    "string_count": 17_868,
}
# Stable composition interface for a later exact-file candidate assembler.
EXPECTED_CANDIDATE: dict[str, Any] = dict(TARGET_PIN)

HANGUL_RE = re.compile(r"[\uAC00-\uD7A3]")
SOURCE_SCRIPT_RE = re.compile(
    r"[\u3040-\u30FF\u31F0-\u31FF\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF]"
)

HOLD_REASONS: dict[int, dict[str, str]] = {
    3917: {
        "reason_code": "institutional_term_style",
        "review_question": "중세 봉신 신분의 한국어 표기를 고정한 뒤 반영",
    },
    4835: {
        "reason_code": "character_trait_gloss",
        "review_question": "인물 성품을 나타내는 강조어의 문맥 번역을 화면 확인 뒤 반영",
    },
    7260: {
        "reason_code": "naval_vessel_term_style",
        "review_question": "대형 군선 유형의 한국어 명칭을 확정한 뒤 반영",
    },
    8818: {
        "reason_code": "historic_policy_term_gloss",
        "review_question": "관백 표기는 유지하되 제도명 설명 표기를 확정한 뒤 반영",
    },
    8904: {
        "reason_code": "religious_title_style",
        "review_question": "출가 인물 호칭의 한국어 표기를 확정한 뒤 반영",
    },
}


class WaveError(ValueError):
    """Raised when a source, contract, or candidate invariant differs."""


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def text_hash(text: str) -> str:
    return sha256(text.encode("utf-16-le"))


def canonical_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def id_sha256(ids: Iterable[int]) -> str:
    return sha256("".join(f"{entry_id}\n" for entry_id in ids).encode("ascii"))


def require_equal(actual: Any, expected: Any, label: str) -> None:
    if actual != expected:
        raise WaveError(f"{label} differs: {actual!r} != {expected!r}")


def strict_object(pairs: Iterable[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    folded: set[str] = set()
    for key, value in pairs:
        normalized = key.casefold()
        if normalized in folded:
            raise WaveError(f"duplicate or case-colliding JSON key: {key!r}")
        folded.add(normalized)
        result[key] = value
    return result


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=strict_object)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise WaveError(f"cannot read strict JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise WaveError(f"JSON root must be an object: {path}")
    return value


def load_base_builder() -> Any:
    spec = importlib.util.spec_from_file_location("base_ev_strdata_wave11_base", BASE_BUILDER_PATH)
    if spec is None or spec.loader is None:
        raise WaveError("cannot load base event transfer builder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def ensure_stock_root(stock_root: Path) -> Path:
    resolved = stock_root.resolve()
    if resolved == LIVE_STEAM_ROOT.resolve():
        raise WaveError("the live Steam root is prohibited as a wave11 stock input")
    if not (resolved / Path(RESOURCE)).is_file():
        raise WaveError(f"stock root has no {RESOURCE}: {resolved}")
    return resolved


def source_free(value: Any, label: str) -> None:
    serialized = json.dumps(value, ensure_ascii=False, sort_keys=True)
    if SOURCE_SCRIPT_RE.search(serialized):
        raise WaveError(f"{label} contains source-script text")


def normalise_switch_target(entry_id: int, value: str) -> str:
    """Apply only the documented source-free and display-title transforms."""
    result = value.replace("\u30fb", "·")
    if entry_id == 7240:
        if result.count("간파쿠") != 1:
            raise WaveError("display-title policy anchor changed at 7240")
        result = result.replace("간파쿠", "관백")
    return result


def contract_rows() -> list[dict[str, Any]]:
    contract = read_json(CONTRACT_PATH)
    if contract.get("schema") != "nobu16.kr.base-jp-residual-wave10-contracts.v1":
        raise WaveError("upstream residual contract schema changed")
    rows = [row for row in contract.get("entries", []) if row.get("resource") == RESOURCE]
    if not all(isinstance(row, dict) for row in rows):
        raise WaveError("upstream event contract contains a non-object row")
    ids = [row.get("id") for row in rows]
    if ids != sorted(ids) or len(ids) != len(set(ids)):
        raise WaveError("upstream event contract IDs are not sorted and unique")
    if len(rows) != 40:
        raise WaveError(f"upstream event contract count differs: {len(rows)}")
    if set(ids) != set(TRANSLATIONS):
        raise WaveError("translation IDs differ from the upstream event contract")
    if set(ids) & set(MANUAL_HOLD_IDS):
        raise WaveError("safe contract and manual holds overlap")
    return rows


def hold_model(base: Any, stock: Any, switch: Any, residual_ids: set[int]) -> dict[str, Any]:
    if tuple(sorted(MANUAL_HOLD_IDS)) != MANUAL_HOLD_IDS:
        raise WaveError("manual hold IDs must be sorted")
    if set(MANUAL_HOLD_IDS) - residual_ids:
        raise WaveError("manual hold no longer belongs to the residual domain")
    rows: list[dict[str, Any]] = []
    for entry_id in MANUAL_HOLD_IDS:
        if entry_id not in HOLD_REASONS:
            raise WaveError(f"missing hold rationale at {entry_id}")
        source = stock.texts[entry_id]
        target = switch.texts[entry_id]
        if not HANGUL_RE.search(target) or not SOURCE_SCRIPT_RE.search(target):
            raise WaveError(f"manual hold predicate changed at {entry_id}")
        rows.append(
            {
                "id": entry_id,
                "source_jp_utf16le_sha256": text_hash(source),
                "switch_ko_utf16le_sha256": text_hash(target),
                **HOLD_REASONS[entry_id],
                "action": "leave_stock_jp_unchanged",
            }
        )
    model = {
        "schema": HOLD_SCHEMA,
        "resource": RESOURCE,
        "base_language": "JP",
        "entry_count": len(rows),
        "ids_sha256": id_sha256(MANUAL_HOLD_IDS),
        "policy_context": {
            "display_title_policy": "관백",
            "reading_style_policy": "간레이",
            "candidate_action": "manual_rows_excluded",
        },
        "entries": rows,
    }
    source_free(model, "hold model")
    return model


def overlay_model(base: Any, stock: Any, switch: Any, residual_ids: set[int]) -> dict[str, Any]:
    rows = contract_rows()
    base_selected, base_residual, hangul_count = base.select_transfer_entries(stock, switch)
    base_residual_ids = {row["id"] for row in base_residual}
    require_equal(base_residual_ids, residual_ids, "base residual ID domain")
    if hangul_count != base.EXPECTED_SWITCH_HANGUL_CANDIDATES:
        raise WaveError("base Switch candidate count changed")
    entries: list[dict[str, Any]] = []
    for contract in rows:
        entry_id = contract["id"]
        source = stock.texts[entry_id]
        switch_target = switch.texts[entry_id]
        require_equal(contract["source_jp_utf16le_sha256"], text_hash(source), f"source hash at {entry_id}")
        require_equal(contract["planned_ko_utf16le_sha256"], text_hash(switch_target), f"upstream target hash at {entry_id}")
        planned = normalise_switch_target(entry_id, switch_target)
        require_equal(TRANSLATIONS[entry_id], planned, f"translation target at {entry_id}")
        if not HANGUL_RE.search(planned):
            raise WaveError(f"translation has no Hangul at {entry_id}")
        if SOURCE_SCRIPT_RE.search(planned):
            raise WaveError(f"translation retains source script at {entry_id}")
        if "\0" in planned or not unicodedata.is_normalized("NFC", planned):
            raise WaveError(f"translation encoding is invalid at {entry_id}")
        mismatches = base.invariant_mismatches(source, planned)
        if mismatches:
            raise WaveError(f"translation invariant mismatch at {entry_id}: {mismatches}")
        transform = "switch_v13_middle_dot_to_center_dot"
        if entry_id == 7240:
            transform = "switch_v13_middle_dot_to_center_dot_and_display_title_policy"
        entries.append(
            {
                "id": entry_id,
                "source_jp_utf16le_sha256": text_hash(source),
                "switch_ko_utf16le_sha256": text_hash(switch_target),
                "planned_ko_utf16le_sha256": text_hash(planned),
                "transform": transform,
                "ko": planned,
            }
        )
    if len(entries) != 40:
        raise WaveError("safe overlay count differs")
    entry_ids = [row["id"] for row in entries]
    if entry_ids != sorted(entry_ids) or set(entry_ids) & {row["id"] for row in base_selected}:
        raise WaveError("safe overlay domain is not disjoint from the base transfer")
    model = {
        "schema": OVERLAY_SCHEMA,
        "overlay_id": OVERLAY_ID,
        "resource": RESOURCE,
        "base_language": "JP",
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
            "contains_switch_binary": False,
        },
        "stock_jp": dict(base.STEAM_JP_PIN),
        "upstream_contract": {
            "path": "workstreams/base_jp_residual_wave10_inventory/public/base_jp_residual_wave10_contracts.v1.json",
            "schema": "nobu16.kr.base-jp-residual-wave10-contracts.v1",
            "entry_count": len(entries),
            "ids_sha256": id_sha256(entry_ids),
        },
        "base_transfer": {
            "overlay_id": base.OVERLAY_ID,
            "entry_count": base.EXPECTED_SELECTED_COUNT,
            "entry_ids_sha256": base.EXPECTED_SELECTED_IDS_SHA256,
        },
        "policy": {
            "source_free_separator": "middle_dot_to_center_dot",
            "display_title_7240": "관백",
            "reading_style": "간레이",
        },
        "entry_count": len(entries),
        "entries": entries,
    }
    source_free(model, "overlay model")
    return model


def validate_public_models(base: Any, stock: Any, switch: Any, overlay: dict[str, Any], holds: dict[str, Any]) -> dict[int, str]:
    selected, residual, _hangul = base.select_transfer_entries(stock, switch)
    residual_ids = {row["id"] for row in residual}
    expected_overlay = overlay_model(base, stock, switch, residual_ids)
    expected_holds = hold_model(base, stock, switch, residual_ids)
    require_equal(overlay, expected_overlay, "tracked safe overlay model")
    require_equal(holds, expected_holds, "tracked manual hold model")
    source_free(overlay, "tracked overlay")
    source_free(holds, "tracked holds")
    entries = overlay["entries"]
    replacements = {row["id"]: row["ko"] for row in entries}
    if len(replacements) != 40 or set(replacements) & {row["id"] for row in selected}:
        raise WaveError("replacement domain changed")
    if set(replacements) | set(MANUAL_HOLD_IDS) != residual_ids:
        raise WaveError("safe and manual partitions no longer cover the residual domain")
    return replacements


def _target_pin(candidate: bytes, raw: bytes, table: Any) -> dict[str, Any]:
    return {
        "packed_size": len(candidate),
        "packed_sha256": sha256(candidate),
        "raw_size": len(raw),
        "raw_sha256": sha256(raw),
        "string_count": table.string_count,
    }


def build_blob(
    stock_root: Path = DEFAULT_STOCK_ROOT,
    switch_zip: Path = DEFAULT_SWITCH_ZIP,
) -> tuple[bytes, dict[str, Any]]:
    """Return the 13,085-row event candidate in memory; never write Steam."""
    base = load_base_builder()
    stock_root = ensure_stock_root(stock_root)
    overlay = read_json(OVERLAY_PATH)
    holds = read_json(HOLD_PATH)
    return build_blob_from_models(base, stock_root, switch_zip, overlay, holds)


def expected_public_models(stock_root: Path, switch_zip: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    base = load_base_builder()
    stock_root = ensure_stock_root(stock_root)
    stock_packed, _wrapper, _raw, stock = base.load_steam_jp(stock_root)
    _switch_packed, _switch_wrapper, _switch_raw, switch = base.load_switch_v13(switch_zip)
    selected, residual, _hangul = base.select_transfer_entries(stock, switch)
    if selected and not stock_packed:
        raise WaveError("impossible empty stock condition")
    residual_ids = {row["id"] for row in residual}
    overlay = overlay_model(base, stock, switch, residual_ids)
    holds = hold_model(base, stock, switch, residual_ids)
    _candidate, validation = build_blob_from_models(base, stock_root, switch_zip, overlay, holds)
    return overlay, holds, validation


def build_blob_from_models(base: Any, stock_root: Path, switch_zip: Path, overlay: dict[str, Any], holds: dict[str, Any]) -> tuple[bytes, dict[str, Any]]:
    """Temporary model composition used to emit/verify public artifacts."""
    stock_packed, wrapper, _stock_raw, stock = base.load_steam_jp(stock_root)
    _switch_packed, _switch_wrapper, _switch_raw, switch = base.load_switch_v13(switch_zip)
    before = sha256(stock_packed)
    replacements = validate_public_models(base, stock, switch, overlay, holds)
    base_candidate, base_metrics = base.build_blob(stock_root, switch_zip)
    _base_wrapper, base_raw = base.decompress_wrapper(base_candidate)
    base_table = base.parse_message_table(base_raw)
    texts = list(base_table.texts)
    for entry_id, korean in replacements.items():
        texts[entry_id] = korean
    candidate_raw = base.rebuild_message_table(base_table, texts)
    candidate = base.recompress_wrapper(candidate_raw, wrapper)
    candidate_wrapper, roundtrip_raw = base.decompress_wrapper(candidate)
    if candidate_wrapper.prefix != wrapper.prefix or roundtrip_raw != candidate_raw:
        raise WaveError("candidate wrapper round-trip differs")
    candidate_table = base.parse_message_table(candidate_raw)
    require_equal(candidate_table.string_count, stock.string_count, "candidate string count")
    for entry_id, korean in replacements.items():
        require_equal(candidate_table.texts[entry_id], korean, f"candidate target at {entry_id}")
    for entry_id in MANUAL_HOLD_IDS:
        require_equal(candidate_table.texts[entry_id], stock.texts[entry_id], f"manual hold preservation at {entry_id}")
    actual_pin = _target_pin(candidate, candidate_raw, candidate_table)
    require_equal(actual_pin, TARGET_PIN, "wave11 candidate target pin")
    require_equal(sha256(stock_packed), before, "stock backup after build")
    manifest = {
        "schema": VALIDATION_SCHEMA,
        "status": "PASS",
        "resource": RESOURCE,
        "runtime": {"distribution": "Steam", "base_language_route": "JP", "steam_pk_version": "1.1.7"},
        "stock_jp": dict(base.STEAM_JP_PIN),
        "base_transfer": {"entry_count": base.EXPECTED_SELECTED_COUNT, "candidate": dict(base.TARGET_PIN)},
        "wave11": {
            "safe_entry_count": len(replacements),
            "manual_hold_count": len(MANUAL_HOLD_IDS),
            "safe_ids_sha256": id_sha256(sorted(replacements)),
            "hold_ids_sha256": id_sha256(MANUAL_HOLD_IDS),
        },
        "candidate": actual_pin | {"changed_entry_count": base.EXPECTED_SELECTED_COUNT + len(replacements)},
        "checks": {
            "preapplication_stock_backup_hash_gate": True,
            "live_steam_root_rejected": True,
            "upstream_contract_hash_gate": True,
            "source_hash_gate": True,
            "switch_target_hash_gate": True,
            "source_free_overlay": True,
            "middle_dot_normalization": True,
            "display_title_policy_7240": True,
            "control_linebreak_placeholder_invariants": True,
            "base_and_wave_domains_disjoint": True,
            "manual_hold_rows_preserved": True,
            "candidate_parse_roundtrip": True,
            "wrapper_prefix_preserved": True,
            "installed_game_file_written": False,
            "current_v5_candidate_modified": False,
            "release_asset_written": False,
        },
    }
    source_free(manifest, "validation model")
    return candidate, manifest


def write_exact(path: Path, value: dict[str, Any]) -> None:
    blob = canonical_json_bytes(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(blob)
    if path.read_bytes() != blob:
        raise WaveError(f"write verification failed: {path}")


def generate_public(stock_root: Path, switch_zip: Path) -> dict[str, Any]:
    overlay, holds, validation = expected_public_models(stock_root, switch_zip)
    write_exact(OVERLAY_PATH, overlay)
    write_exact(HOLD_PATH, holds)
    write_exact(VALIDATION_PATH, validation)
    return validation


def verify(
    stock_root: Path = DEFAULT_STOCK_ROOT,
    switch_zip: Path = DEFAULT_SWITCH_ZIP,
) -> dict[str, Any]:
    stock_root = ensure_stock_root(stock_root)
    before = sha256((stock_root / Path(RESOURCE)).read_bytes())
    overlay, holds, validation = expected_public_models(stock_root, switch_zip)
    for path, expected in ((OVERLAY_PATH, overlay), (HOLD_PATH, holds), (VALIDATION_PATH, validation)):
        actual = read_json(path)
        require_equal(actual, expected, f"tracked artifact model at {path.name}")
        require_equal(path.read_bytes(), canonical_json_bytes(actual), f"canonical artifact bytes at {path.name}")
        source_free(actual, f"tracked artifact {path.name}")
    first, first_manifest = build_blob(stock_root, switch_zip)
    second, second_manifest = build_blob(stock_root, switch_zip)
    if first != second or canonical_json_bytes(first_manifest) != canonical_json_bytes(second_manifest):
        raise WaveError("deterministic A/B build differs")
    require_equal(sha256((stock_root / Path(RESOURCE)).read_bytes()), before, "stock backup after verification")
    return validation | {"deterministic_ab_equal": True}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("generate-public", "verify"))
    parser.add_argument("--stock-root", type=Path, default=DEFAULT_STOCK_ROOT)
    parser.add_argument("--switch-zip", type=Path, default=DEFAULT_SWITCH_ZIP)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = generate_public(args.stock_root, args.switch_zip) if args.command == "generate-public" else verify(args.stock_root, args.switch_zip)
    except (OSError, ValueError, WaveError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"status={result['status']}")
    print(f"safe_entries={result['wave11']['safe_entry_count']}")
    print(f"manual_holds={result['wave11']['manual_hold_count']}")
    print("installed_game_file_written=False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
