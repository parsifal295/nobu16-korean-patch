#!/usr/bin/env python3
"""Port structurally compatible Switch v1.1 Korean event strings to PK msgev.

The supplied Switch archive is read as an input only.  This builder emits a
source-free PC PK overlay plus audit artifacts; it never extracts the archive,
writes a complete game resource, or changes an installed game file.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = SCRIPT_PATH.parent
REPO_ROOT = SCRIPT_PATH.parents[2]
GAME_ROOT = REPO_ROOT.parent
TOOLS_ROOT = REPO_ROOT / "tools"
sys.path.insert(0, str(TOOLS_ROOT))

import build_common_message_overlay as common  # noqa: E402
from nobu16_lz4 import decompress_wrapper, recompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table, rebuild_message_table  # noqa: E402


BATCH_ID = "switch-v11-pk-msgev-port-7025.v1"
OVERLAY_NAME = "msgev_ko_switch_v11_ported_7025.v1.json"
EVIDENCE_NAME = "switch_v11_pk_msgev_alignment.v1.json"
REVIEW_NAME = "switch_v11_pk_msgev_review.v1.json"
VALIDATION_NAME = "validation.v1.json"
RESOURCE = "MSG_PK/SC/msgev.bin"

SWITCH_ARCHIVE_RELATIVE = Path(
    "tmp/third_party_switch_v11/NobunagaShinsei_KoreanPatch_v1.1.zip"
)
SWITCH_ENTRY = "NobunagaShinsei_KR/romfs/MSG/JP/ev_strdata.bin"
SWITCH_RELEASE = {
    "title": "NobunagaShinsei Korean Patch",
    "platform": "Nintendo Switch",
    "release_tag": "v1.1",
    "release_url": "https://github.com/snake7594/nobunaga-shinsei-korean-patch/releases/tag/v1.1",
    "source_repository": "https://github.com/snake7594/nobunaga-shinsei-korean-patch",
    "author_account": "snake7594",
    "attribution": "snake7594_unofficial_fan_translation_v1_1",
    "archive_relative_path": SWITCH_ARCHIVE_RELATIVE.as_posix(),
    "archive_size": 73_040_529,
    "archive_sha256": "931E7C5BDECD724E44987D722E71A12161448A1A583DFFB4A569A4FA58EC46F6",
    "entry_path": SWITCH_ENTRY,
    "entry_crc32": "018EAC29",
    "entry_uncompressed_size": 396_257,
    "entry_compressed_size": 314_537,
}

SOURCE_PINS: dict[str, dict[str, Any]] = {
    "switch_ko": {
        "logical_path": f"ZIP!/{SWITCH_ENTRY}",
        "size": 396_257,
        "packed_sha256": "A5D70580790330EF845EC73FDB8D6ACC89EBAD8D026DFE1B1D873C50B43CAD5D",
        "raw_size": 925_000,
        "raw_sha256": "1B8F7197D48598994852317B19CA3B9EC113A3B07A3B22642FBD336C21C4F7C3",
        "string_count": 17_868,
    },
    "base_jp": {
        "logical_path": "MSG/JP/ev_strdata.bin",
        "size": 496_819,
        "packed_sha256": "EADCD167EF9684C7F077694A1A7F68966E34FD2E2EEF9DEFB7817031C3D773EB",
        "raw_size": 789_260,
        "raw_sha256": "5FBD960A4870FA4850BD725C58E67BE3A7F191960737C36E4505151FE4B7C528",
        "string_count": 17_868,
    },
    "pk_jp": {
        "logical_path": "MSG_PK/JP/msgev.bin",
        "size": 555_784,
        "packed_sha256": "03426B59D32EB628021DE43BC02FF82B56B04D97C25CE37F735630EA7C4E2002",
        "raw_size": 890_428,
        "raw_sha256": "4A916CA6837C4F8FC2D8B6254ECBEF26339558D2DDFEBF5A1637F8426F5918DE",
        "string_count": 17_910,
    },
    "pk_sc_stock": {
        "logical_path": "backups/officer_name_probe_v0_1/msgev.SC.stock.bin",
        "size": 522_918,
        "packed_sha256": "7221A53E6E5CF493A3FAFFFCE35280E8147898120EEC59E460A2429AA265C1F9",
        "raw_size": 750_584,
        "raw_sha256": "99E0338A64FF4140AD6E27503B1BF138AC44F5B68F01973ED61D0C949619DC91",
        "string_count": 17_910,
    },
}

OFFICER_RECIPE_RELATIVE = Path(
    "workstreams/officer_names/full_v0.1/public/msgev_sc.recipe.json"
)
OFFICER_RECIPE_SHA256 = "E1F0398219C322C87D9BA785C66FC1F33AE1E8871654080F37C8C38153FB2F6D"
DIALOGUE_CATALOG_MANIFEST_SHA256 = (
    "88FACF29C9FBD0504D3AA1E93FD6C1D094D2527804E8C7B113C0E390282FCCBE"
)
EXPECTED_EXISTING_ID_COUNT = 5_469
EXPECTED_EXISTING_IDS_SHA256 = (
    "D3827CB87DA20F6807558E055D831E7640DA14652C2C32C4E1292EE899E4D5C4"
)
EXPECTED_DIALOGUE_CATALOG_COUNT = 27
EXPECTED_SELECTED_COUNT = 7_025
EXPECTED_SELECTED_IDS_SHA256 = (
    "ECE96F365962D0408CC80D5324D2D900C4983B423D782D77B0CF4A4799299DCF"
)
EXPECTED_SOURCE_SCRIPT_EXCLUDED_COUNT = 20
EXPECTED_SOURCE_SCRIPT_EXCLUDED_IDS_SHA256 = (
    "F9B2C54B499583605D1D8748747123DE1C4FF2C3C990383FD0E672DF8D7BCFDB"
)

BRACKET_TOKEN_RE = re.compile(r"\[[a-z0-9_]+\]")


class SwitchMsgevPortError(ValueError):
    """Raised when the pinned Switch-to-PC compatibility gate fails."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def hash_json(value: Any) -> str:
    return sha256(json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))


def encode_json(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def write_json(path: Path, value: Any) -> dict[str, Any]:
    blob = encode_json(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(blob)
    return {
        "path": path.name if path.parent == WORKSTREAM_ROOT else path.as_posix(),
        "size": len(blob),
        "sha256": sha256(blob),
    }


def source_free_counts(blob: bytes) -> dict[str, int]:
    text = blob.decode("utf-8")
    han_ranges = (
        (0x3400, 0x4DBF),
        (0x4E00, 0x9FFF),
        (0x20000, 0x2EBEF),
        (0x30000, 0x323AF),
        (0xF900, 0xFAFF),
    )
    kana_ranges = (
        (0x3040, 0x309F),
        (0x30A0, 0x30FF),
        (0x31F0, 0x31FF),
        (0xFF66, 0xFF9D),
    )
    return {
        "han_or_kana_count": sum(
            any(start <= ord(character) <= end for start, end in han_ranges + kana_ranges)
            for character in text
        ),
        "embedded_nul_count": text.count("\x00"),
    }


def source_structure(text: str) -> dict[str, Any]:
    invariants = common.message_invariants(text)
    return {
        "esc": invariants["esc"],
        "line_breaks": invariants["line_breaks"],
        "printf": invariants["printf"],
        "unknown_percent_count": invariants["unknown_percent_count"],
        "control_count": len(invariants["controls"]),
        "pua": invariants["pua"],
        "leading_whitespace_utf16le_sha256": common.text_hash(
            invariants["leading_whitespace"]
        ),
        "trailing_whitespace_utf16le_sha256": common.text_hash(
            invariants["trailing_whitespace"]
        ),
    }


def load_pinned_table(label: str, packed: bytes, pin: dict[str, Any]) -> dict[str, Any]:
    if len(packed) != int(pin["size"]):
        raise SwitchMsgevPortError(f"{label} packed size does not match pin")
    if sha256(packed) != str(pin["packed_sha256"]):
        raise SwitchMsgevPortError(f"{label} packed SHA-256 does not match pin")
    _, raw = decompress_wrapper(packed)
    if len(raw) != int(pin["raw_size"]):
        raise SwitchMsgevPortError(f"{label} raw size does not match pin")
    if sha256(raw) != str(pin["raw_sha256"]):
        raise SwitchMsgevPortError(f"{label} raw SHA-256 does not match pin")
    table = parse_message_table(raw)
    if table.string_count != int(pin["string_count"]):
        raise SwitchMsgevPortError(f"{label} string count does not match pin")
    if rebuild_message_table(table, table.texts) != raw:
        raise SwitchMsgevPortError(f"{label} parse/rebuild is not byte-identical")
    return {"packed": packed, "raw": raw, "table": table}


def read_switch_table(archive_path: Path) -> dict[str, Any]:
    archive_blob = archive_path.read_bytes()
    if len(archive_blob) != int(SWITCH_RELEASE["archive_size"]):
        raise SwitchMsgevPortError("Switch archive size does not match release pin")
    if sha256(archive_blob) != str(SWITCH_RELEASE["archive_sha256"]):
        raise SwitchMsgevPortError("Switch archive SHA-256 does not match release pin")
    with zipfile.ZipFile(archive_path) as archive:
        info = archive.getinfo(SWITCH_ENTRY)
        if f"{info.CRC:08X}" != SWITCH_RELEASE["entry_crc32"]:
            raise SwitchMsgevPortError("Switch entry CRC32 does not match release pin")
        if info.file_size != int(SWITCH_RELEASE["entry_uncompressed_size"]):
            raise SwitchMsgevPortError("Switch entry size does not match release pin")
        if info.compress_size != int(SWITCH_RELEASE["entry_compressed_size"]):
            raise SwitchMsgevPortError("Switch entry compressed size does not match release pin")
        packed = archive.read(info)
    return load_pinned_table("switch_ko", packed, SOURCE_PINS["switch_ko"])


def load_sources(
    game_root: Path, repo_root: Path, archive_path: Path
) -> dict[str, dict[str, Any]]:
    return {
        "switch_ko": read_switch_table(archive_path),
        "base_jp": load_pinned_table(
            "base_jp",
            (game_root / SOURCE_PINS["base_jp"]["logical_path"]).read_bytes(),
            SOURCE_PINS["base_jp"],
        ),
        "pk_jp": load_pinned_table(
            "pk_jp",
            (game_root / SOURCE_PINS["pk_jp"]["logical_path"]).read_bytes(),
            SOURCE_PINS["pk_jp"],
        ),
        "pk_sc_stock": load_pinned_table(
            "pk_sc_stock",
            (repo_root / SOURCE_PINS["pk_sc_stock"]["logical_path"]).read_bytes(),
            SOURCE_PINS["pk_sc_stock"],
        ),
    }


def input_snapshot(game_root: Path, repo_root: Path, archive_path: Path) -> dict[str, str]:
    paths = {
        "switch_archive": archive_path,
        "base_jp": game_root / SOURCE_PINS["base_jp"]["logical_path"],
        "pk_jp": game_root / SOURCE_PINS["pk_jp"]["logical_path"],
        "pk_sc_stock": repo_root / SOURCE_PINS["pk_sc_stock"]["logical_path"],
    }
    return {name: sha256(path.read_bytes()) for name, path in paths.items()}


def existing_msgev_catalog_snapshot(repo_root: Path) -> dict[str, Any]:
    officer_path = repo_root / OFFICER_RECIPE_RELATIVE
    officer_blob = officer_path.read_bytes()
    if sha256(officer_blob) != OFFICER_RECIPE_SHA256:
        raise SwitchMsgevPortError("officer-name msgev public recipe changed")
    officer = json.loads(officer_blob.decode("utf-8"), object_pairs_hook=common.strict_object)
    if officer["source"]["relative_path"] != RESOURCE:
        raise SwitchMsgevPortError("officer-name recipe does not target PK msgev")
    officer_ids = [int(operation["id"]) for operation in officer["operations"]]
    if officer_ids != list(range(2_207)):
        raise SwitchMsgevPortError("officer-name recipe does not own IDs 0 through 2206")

    dialogue_dir = repo_root / "workstreams" / "dialogue" / "public"
    dialogue_rows: list[dict[str, Any]] = []
    dialogue_ids: list[int] = []
    for path in sorted(dialogue_dir.glob("msgev_ko_*.json")):
        overlay, blob = common.load_json_strict(path)
        resource, _, entries = common.validate_overlay_shape(overlay)
        if resource != RESOURCE:
            continue
        ids = [int(entry["id"]) for entry in entries]
        dialogue_rows.append(
            {
                "path": path.relative_to(repo_root).as_posix(),
                "entry_count": len(ids),
                "sha256": sha256(blob),
            }
        )
        dialogue_ids.extend(ids)
    if len(dialogue_rows) != EXPECTED_DIALOGUE_CATALOG_COUNT:
        raise SwitchMsgevPortError("dialogue public overlay count changed")
    if hash_json(dialogue_rows) != DIALOGUE_CATALOG_MANIFEST_SHA256:
        raise SwitchMsgevPortError("dialogue public overlay manifest changed")
    if len(dialogue_ids) != len(set(dialogue_ids)):
        raise SwitchMsgevPortError("dialogue public overlays overlap one another")

    owners = sorted(set(officer_ids) | set(dialogue_ids))
    if len(owners) != len(officer_ids) + len(dialogue_ids):
        raise SwitchMsgevPortError("officer and dialogue public catalogs overlap")
    if len(owners) != EXPECTED_EXISTING_ID_COUNT:
        raise SwitchMsgevPortError("existing PK msgev public catalog count changed")
    if hash_json(owners) != EXPECTED_EXISTING_IDS_SHA256:
        raise SwitchMsgevPortError("existing PK msgev public catalog IDs changed")
    return {
        "unique_id_count": len(owners),
        "ids_sha256": hash_json(owners),
        "cross_catalog_overlap_count": 0,
        "officer_recipe": {
            "path": OFFICER_RECIPE_RELATIVE.as_posix(),
            "entry_count": len(officer_ids),
            "sha256": sha256(officer_blob),
        },
        "dialogue_catalog": {
            "entry_count": len(dialogue_rows),
            "manifest_sha256": hash_json(dialogue_rows),
            "entries": dialogue_rows,
        },
        "ids": owners,
    }


def has_meaningful_hangul(value: str) -> bool:
    return common.has_semantic_text(value) and any(
        0xAC00 <= ord(character) <= 0xD7A3 for character in value
    )


def contains_cjk_or_kana(value: str) -> bool:
    return any(
        0x3400 <= ord(character) <= 0x4DBF
        or 0x4E00 <= ord(character) <= 0x9FFF
        or 0xF900 <= ord(character) <= 0xFAFF
        or 0x3040 <= ord(character) <= 0x30FF
        or 0x31F0 <= ord(character) <= 0x31FF
        for character in value
    )


def select_portable_entries(
    sources: dict[str, dict[str, Any]], existing: dict[str, Any]
) -> tuple[list[dict[str, Any]], dict[str, int], list[int], list[int]]:
    switch = sources["switch_ko"]["table"]
    base_jp = sources["base_jp"]["table"]
    pk_jp = sources["pk_jp"]["table"]
    pk_sc = sources["pk_sc_stock"]["table"]
    if base_jp.string_count != switch.string_count:
        raise SwitchMsgevPortError("Switch Korean and PC base JP string counts differ")
    if pk_jp.string_count != pk_sc.string_count:
        raise SwitchMsgevPortError("PC PK JP and SC string counts differ")
    if base_jp.string_count > pk_jp.string_count:
        raise SwitchMsgevPortError("PC PK table cannot cover PC base IDs")

    existing_ids = set(existing["ids"])
    stages = {
        "base_jp_scope_count": base_jp.string_count,
        "pk_extra_slot_count": pk_jp.string_count - base_jp.string_count,
        "meaningful_hangul_count": 0,
        "base_jp_equals_pk_jp_count": 0,
        "switch_korean_differs_from_jp_count": 0,
        "pk_sc_invariant_match_count": 0,
        "existing_nonoverlap_count": 0,
        "source_script_excluded_count": 0,
        "source_script_free_portable_count": 0,
    }
    selected: list[dict[str, Any]] = []
    source_script_excluded_ids: list[int] = []
    bracket_mismatch_ids: list[int] = []
    for entry_id in range(base_jp.string_count):
        switch_ko = switch.texts[entry_id]
        if not has_meaningful_hangul(switch_ko):
            continue
        stages["meaningful_hangul_count"] += 1
        reference_jp = base_jp.texts[entry_id]
        if reference_jp != pk_jp.texts[entry_id]:
            continue
        stages["base_jp_equals_pk_jp_count"] += 1
        if switch_ko == reference_jp:
            continue
        stages["switch_korean_differs_from_jp_count"] += 1
        problems = common.invariant_mismatches(pk_sc.texts[entry_id], switch_ko)
        if problems:
            continue
        stages["pk_sc_invariant_match_count"] += 1
        if entry_id in existing_ids:
            continue
        stages["existing_nonoverlap_count"] += 1
        if contains_cjk_or_kana(switch_ko):
            stages["source_script_excluded_count"] += 1
            source_script_excluded_ids.append(entry_id)
            continue
        ported_ko = switch_ko
        stages["source_script_free_portable_count"] += 1
        if BRACKET_TOKEN_RE.findall(pk_sc.texts[entry_id]) != BRACKET_TOKEN_RE.findall(
            ported_ko
        ):
            bracket_mismatch_ids.append(entry_id)
        selected.append(
            {
                "id": entry_id,
                "ko": ported_ko,
                "source_sc_utf16le_sha256": common.text_hash(pk_sc.texts[entry_id]),
                "switch_ko_utf16le_sha256": common.text_hash(switch_ko),
                "ported_ko_utf16le_sha256": common.text_hash(ported_ko),
                "base_jp_utf16le_sha256": common.text_hash(reference_jp),
                "pk_jp_utf16le_sha256": common.text_hash(pk_jp.texts[entry_id]),
                "pk_sc_structure": source_structure(pk_sc.texts[entry_id]),
                "ported_ko_structure": source_structure(ported_ko),
            }
        )
    ids = [entry["id"] for entry in selected]
    if ids != sorted(ids) or len(ids) != len(set(ids)):
        raise SwitchMsgevPortError("selected Switch port IDs are not sorted and unique")
    if len(ids) != EXPECTED_SELECTED_COUNT:
        raise SwitchMsgevPortError(
            f"selected Switch port count is {len(ids)}, expected {EXPECTED_SELECTED_COUNT}"
        )
    if hash_json(ids) != EXPECTED_SELECTED_IDS_SHA256:
        raise SwitchMsgevPortError("selected Switch port IDs do not match the reviewed set")
    if len(source_script_excluded_ids) != EXPECTED_SOURCE_SCRIPT_EXCLUDED_COUNT:
        raise SwitchMsgevPortError("source-script exclusion count does not match review pin")
    if (
        hash_json(source_script_excluded_ids)
        != EXPECTED_SOURCE_SCRIPT_EXCLUDED_IDS_SHA256
    ):
        raise SwitchMsgevPortError("source-script exclusion IDs do not match review pin")
    return selected, stages, source_script_excluded_ids, bracket_mismatch_ids


def reconstruct_pk_sc_target(
    pk_sc_source: dict[str, Any], selected: list[dict[str, Any]]
) -> dict[str, Any]:
    table = pk_sc_source["table"]
    texts = list(table.texts)
    for entry in selected:
        texts[int(entry["id"])] = str(entry["ko"])
    raw = rebuild_message_table(table, texts)
    if parse_message_table(raw).texts != tuple(texts):
        raise SwitchMsgevPortError("ported PK SC target does not parse back exactly")
    wrapper = recompress_wrapper(raw, pk_sc_source["packed"])
    if decompress_wrapper(wrapper)[1] != raw:
        raise SwitchMsgevPortError("ported PK SC wrapper does not decompress exactly")
    return {
        "changed_entry_count": len(selected),
        "wrapper_size": len(wrapper),
        "wrapper_sha256": sha256(wrapper),
        "raw_size": len(raw),
        "raw_sha256": sha256(raw),
    }


def build_once(
    game_root: Path, repo_root: Path, archive_path: Path, out_root: Path
) -> dict[str, Any]:
    before = input_snapshot(game_root, repo_root, archive_path)
    sources = load_sources(game_root, repo_root, archive_path)
    existing = existing_msgev_catalog_snapshot(repo_root)
    selected, stages, source_script_excluded_ids, bracket_mismatch_ids = select_portable_entries(
        sources, existing
    )
    ids = [int(entry["id"]) for entry in selected]
    pk_sc = sources["pk_sc_stock"]["table"]
    target = reconstruct_pk_sc_target(sources["pk_sc_stock"], selected)

    overlay = {
        "schema": common.OVERLAY_SCHEMA,
        "overlay_id": BATCH_ID,
        "resource": RESOURCE,
        "base_language": "SC",
        "entry_count": len(selected),
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
        },
        "stock_sc": {
            key: SOURCE_PINS["pk_sc_stock"][key]
            for key in ("size", "packed_sha256", "raw_size", "raw_sha256", "string_count")
        },
        "defaults": {"status": "translated"},
        "entries": [
            {
                "id": int(entry["id"]),
                "source_sc_utf16le_sha256": entry["source_sc_utf16le_sha256"],
                "ko": entry["ko"],
            }
            for entry in selected
        ],
    }
    common.validate_overlay_shape(overlay)

    source_files = {
        name: dict(pin) for name, pin in SOURCE_PINS.items()
    }
    evidence = {
        "schema": "nobu16.kr.switch-msgev-v11-alignment-evidence.v1",
        "batch_id": BATCH_ID,
        "resource": RESOURCE,
        "source_release": SWITCH_RELEASE,
        "selection_method": [
            "switch_patch_value_has_semantic_hangul",
            "pc_base_jp_equals_pc_pk_jp_at_same_numeric_id",
            "switch_patch_value_differs_from_common_jp_reference",
            "ported_korean_matches_pk_sc_printf_esc_control_and_linebreak_invariants",
            "existing_public_pk_msgev_id_exclusion",
            "cjk_unified_han_and_kana_exclusion_for_source_free_pc_font_compatibility",
        ],
        "source_files": source_files,
        "selection": {
            **stages,
            "selected_count": len(selected),
            "selected_ids_sha256": hash_json(ids),
            "switch_to_pc_numeric_id_mapping": "identity_for_ids_0_through_17867",
            "jp_original_equality_scope": "PC_base_JP_and_PC_PK_JP",
            "switch_patch_value_role": "Korean_replacement_in_Switch_JP_tree",
            "source_script_filter": {
                "ranges": [
                    "U+3400-U+4DBF",
                    "U+4E00-U+9FFF",
                    "U+F900-U+FAFF",
                    "U+3040-U+30FF",
                    "U+31F0-U+31FF",
                ],
                "excluded_count": len(source_script_excluded_ids),
                "excluded_ids_sha256": hash_json(source_script_excluded_ids),
            },
            "custom_bracket_token_mismatch_count": len(bracket_mismatch_ids),
            "custom_bracket_token_mismatch_ids_sha256": hash_json(
                bracket_mismatch_ids
            ),
        },
        "existing_public_catalog_exclusion": {
            key: value for key, value in existing.items() if key != "ids"
        },
        "entry_count": len(selected),
        "entries": [
            {
                "id": int(entry["id"]),
                "switch_ko_utf16le_sha256": entry["switch_ko_utf16le_sha256"],
                "ported_ko_utf16le_sha256": entry["ported_ko_utf16le_sha256"],
                "base_jp_utf16le_sha256": entry["base_jp_utf16le_sha256"],
                "pk_jp_utf16le_sha256": entry["pk_jp_utf16le_sha256"],
                "pk_sc_utf16le_sha256": entry["source_sc_utf16le_sha256"],
                "base_jp_equals_pk_jp": True,
                "switch_ko_differs_from_jp": True,
                "pk_sc_invariants_match": True,
                "pk_sc_structure": entry["pk_sc_structure"],
                "ported_ko_structure": entry["ported_ko_structure"],
            }
            for entry in selected
        ],
        "contains_commercial_source_text": False,
    }
    review = {
        "schema": "nobu16.kr.switch-msgev-v11-review-index.v1",
        "batch_id": BATCH_ID,
        "quality_state": "switch_v11_import_pending_pc_runtime_review",
        "entry_count": len(selected),
        "entries": [
            {
                "id": int(entry["id"]),
                "status": "translated",
                "translation_origin": "switch_v11_structurally_gated_port",
                "human_review_required": True,
                "runtime_reviewed": False,
                "uncertainty_flags": [
                    "pc_pk_runtime_layout_review",
                    "switch_to_pc_context_review",
                ]
                + (
                    ["custom_bracket_token_difference_review"]
                    if int(entry["id"]) in bracket_mismatch_ids
                    else []
                ),
            }
            for entry in selected
        ],
        "contains_commercial_source_text": False,
    }

    out_root = out_root.resolve()
    overlay_path = out_root / "public" / OVERLAY_NAME
    evidence_path = out_root / "evidence" / EVIDENCE_NAME
    review_path = out_root / "review" / REVIEW_NAME
    for path, value in (
        (overlay_path, overlay),
        (evidence_path, evidence),
        (review_path, review),
    ):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(encode_json(value))
    source_free_scan = {
        "overlay": source_free_counts(overlay_path.read_bytes()),
        "alignment_evidence": source_free_counts(evidence_path.read_bytes()),
        "review_index": source_free_counts(review_path.read_bytes()),
    }
    if any(
        result != {"han_or_kana_count": 0, "embedded_nul_count": 0}
        for result in source_free_scan.values()
    ):
        raise SwitchMsgevPortError("a generated public artifact contains source script")

    artifacts = {
        "overlay": {
            "path": f"public/{OVERLAY_NAME}",
            "size": overlay_path.stat().st_size,
            "sha256": sha256(overlay_path.read_bytes()),
        },
        "alignment_evidence": {
            "path": f"evidence/{EVIDENCE_NAME}",
            "size": evidence_path.stat().st_size,
            "sha256": sha256(evidence_path.read_bytes()),
        },
        "review_index": {
            "path": f"review/{REVIEW_NAME}",
            "size": review_path.stat().st_size,
            "sha256": sha256(review_path.read_bytes()),
        },
    }
    validation = {
        "schema": "nobu16.kr.switch-msgev-v11-generation-validation.v1",
        "batch_id": BATCH_ID,
        "passed": True,
        "selection": evidence["selection"],
        "source_release": SWITCH_RELEASE,
        "source_alignment": {
            "source_string_counts": {
                name: int(pin["string_count"]) for name, pin in SOURCE_PINS.items()
            },
            "pc_base_jp_to_pk_jp_exact_match_count": stages[
                "base_jp_equals_pk_jp_count"
            ],
            "ported_entry_reference_hash_count": len(selected) * 4,
            "pk_sc_parse_rebuild_byte_exact": True,
            "switch_patch_parse_rebuild_byte_exact": True,
            "official_source_text_embedded": False,
        },
        "replacement_invariants": {
            "checked": len(selected),
            "failures": 0,
            "preserved": [
                "printf_tokens",
                "unknown_percent_count",
                "edge_whitespace",
                "esc_sequences_in_order",
                "control_characters",
                "line_break_sequence",
                "private_use_codepoints",
            ],
        },
        "existing_public_catalog_exclusion": {
            "existing_unique_id_count": existing["unique_id_count"],
            "existing_ids_sha256": existing["ids_sha256"],
            "selected_overlap_count": 0,
        },
        "custom_bracket_token_review": {
            "selection_gate": False,
            "mismatch_count": len(bracket_mismatch_ids),
            "mismatch_ids_sha256": hash_json(bracket_mismatch_ids),
            "runtime_review_required": bool(bracket_mismatch_ids),
        },
        "source_script_exclusion": {
            "excluded_count": len(source_script_excluded_ids),
            "excluded_ids_sha256": hash_json(source_script_excluded_ids),
            "selected_entries_are_cjk_kana_free": True,
        },
        "reconstruction": {
            "complete_target_included": False,
            "changed_entry_count": target["changed_entry_count"],
            "target": target,
        },
        "source_free_scan": source_free_scan,
        "artifacts": artifacts,
        "generator": {"path": SCRIPT_PATH.name, "sha256": sha256(SCRIPT_PATH.read_bytes())},
        "reproducibility": {
            "required_runs": ["isolated_a", "isolated_b", "final"],
            "byte_identical_artifacts_required": True,
        },
        "safety": {
            "switch_archive_extracted": False,
            "complete_game_resource_emitted": False,
            "installed_game_files_modified": False,
            "font_files_modified": False,
            "root_readme_or_progress_modified": False,
            "process_memory_access": False,
            "executable_modified": False,
            "registry_modified": False,
            "official_source_text_exposed_in_public_artifacts": False,
        },
    }
    validation_path = out_root / VALIDATION_NAME
    validation_path.write_bytes(encode_json(validation))
    if source_free_counts(validation_path.read_bytes()) != {
        "han_or_kana_count": 0,
        "embedded_nul_count": 0,
    }:
        raise SwitchMsgevPortError("validation is not source-free")

    after = input_snapshot(game_root, repo_root, archive_path)
    if before != after:
        raise SwitchMsgevPortError("an input resource changed while building")
    files = {
        f"public/{OVERLAY_NAME}": overlay_path.read_bytes(),
        f"evidence/{EVIDENCE_NAME}": evidence_path.read_bytes(),
        f"review/{REVIEW_NAME}": review_path.read_bytes(),
        VALIDATION_NAME: validation_path.read_bytes(),
    }
    return {
        "entry_count": len(selected),
        "selected_ids_sha256": hash_json(ids),
        "target": target,
        "files": files,
    }


def build_reproducibly(
    game_root: Path, repo_root: Path, archive_path: Path, out_root: Path
) -> dict[str, Any]:
    game_root = game_root.resolve()
    repo_root = repo_root.resolve()
    archive_path = archive_path.resolve()
    out_root = out_root.resolve()
    before = input_snapshot(game_root, repo_root, archive_path)
    with tempfile.TemporaryDirectory(prefix="nobu16-switch-msgev-a-") as first_directory:
        with tempfile.TemporaryDirectory(prefix="nobu16-switch-msgev-b-") as second_directory:
            first = build_once(
                game_root, repo_root, archive_path, Path(first_directory)
            )
            second = build_once(
                game_root, repo_root, archive_path, Path(second_directory)
            )
            if first["files"] != second["files"]:
                raise SwitchMsgevPortError("isolated builds are not byte-identical")
    final = build_once(game_root, repo_root, archive_path, out_root)
    if final["files"] != first["files"]:
        raise SwitchMsgevPortError("final build differs from isolated build")
    after = input_snapshot(game_root, repo_root, archive_path)
    if before != after:
        raise SwitchMsgevPortError("an input resource changed across reproducible build")
    return final


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game-root", type=Path, default=GAME_ROOT)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--archive", type=Path, default=REPO_ROOT / SWITCH_ARCHIVE_RELATIVE)
    parser.add_argument("--out-root", type=Path, default=WORKSTREAM_ROOT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        result = build_reproducibly(
            args.game_root, args.repo_root, args.archive, args.out_root
        )
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"out_root={args.out_root.resolve()}")
    print(f"ported_entries={result['entry_count']}")
    print(f"selected_ids_sha256={result['selected_ids_sha256']}")
    print(f"target_wrapper_sha256={result['target']['wrapper_sha256']}")
    for relative, blob in sorted(result["files"].items()):
        print(f"{relative}_sha256={sha256(blob)}")
    print("contains_commercial_source_text=False")
    print("installed_game_files_modified=False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
